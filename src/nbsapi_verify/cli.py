# ruff: noqa: UP007

import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import click
import pytest
import yaml

from .formatting import ResultCapture, format_results


class TestType(str, Enum):
    ALL = "all"
    AUTH = "auth"
    PUBLIC = "public"


class NoAliasDumper(yaml.SafeDumper):
    """Custom YAML dumper that prevents creation of aliases for duplicate values."""

    def ignore_aliases(self, data):
        return True


def save_yaml(data: dict, file_path: Path) -> None:
    """Save data to YAML file without aliases."""
    with open(file_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, Dumper=NoAliasDumper)


def get_config_locations() -> list[Path]:
    """Get the possible locations for common.yaml in priority order."""
    return [
        Path.cwd() / "common.yaml",  # Current directory
        Path(click.get_app_dir("nbsinfra_verify")) / "common.yaml",  # User config dir
    ]


def find_config() -> Optional[Path]:
    """Find existing config file in priority order."""
    for path in get_config_locations():
        if path.exists():
            return path
    return None


def get_config_path(config_dir: Optional[str] = None) -> Path:
    """Get the path where config should be written/read.

    Args:
        config_dir: Optional custom config directory path. If provided,
                   this overrides the default locations.

    """
    if config_dir:
        path = Path(config_dir) / "common.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    # Default to current directory for new configs
    return Path.cwd() / "common.yaml"


@click.command()
@click.option(
    "--generate", is_flag=True, help="Generate common.yaml configuration file"
)
@click.option(
    "--config-dir",
    type=str,
    help="Custom directory for common.yaml (defaults to current directory)",
)
@click.option("--host", type=str, help="API host (e.g., http://localhost:8000)")
@click.option(
    "--testid",
    type=int,
    default=1,
    help="Existing test user ID (defaults to 1)",
)
@click.option("--username", type=str, help="Existing test username for auth tests")
@click.option("--password", type=str, help="Existing test password for auth tests")
@click.option(
    "--solution",
    type=int,
    default=1,
    help="Existing test solution ID (defaults to 1)",
)
@click.option(
    "--test-type",
    type=click.Choice(["all", "auth", "public"]),
    default="all",
    help="Type of tests to run",
)
def cli(
    generate: bool,
    config_dir: Optional[str],
    host: Optional[str],
    testid: int,
    username: Optional[str],
    password: Optional[str],
    solution: int,
    test_type: str,
):
    """Tavern test runner and configuration generator."""
    if generate:
        if not host:
            click.echo("Error: --host is required when using --generate", err=True)
            sys.exit(1)

        config_path = get_config_path(config_dir)  # Write to explicit path or cwd

        # Create common config
        config = {"variables": {"host": host}}
        config["variables"].update({"user_id": testid})
        config["variables"].update({"solution_id": solution})

        if username and password:
            config["variables"].update({"username": username, "password": password})

        # Write common config
        save_yaml(config, config_path)
        click.echo(f"Generated configuration file at: {config_path}")
        return

    # Running tests
    config_path = None
    if config_dir:
        # If explicit config dir provided, only look there
        config_path = Path(config_dir) / "common.yaml"
        if not config_path.exists():
            click.echo(
                f"Error: Configuration file not found at {config_path}",
                err=True,
            )
            sys.exit(1)
    else:
        # Otherwise search in priority order
        config_path = find_config()
        if not config_path:
            locations = "\n  ".join(str(p) for p in get_config_locations())
            click.echo(
                "Error: Configuration file not found in any of these locations:\n  "
                + locations
                + "\n\nPlease run with --generate flag first to create configuration.",
                err=True,
            )
            sys.exit(1)

    # Get the package's test directory
    package_dir = Path(__file__).parent
    test_dir = package_dir / "tests"

    if not test_dir.exists():
        click.echo(f"Error: Test directory not found at {test_dir}", err=True)
        sys.exit(1)

    # Prepare pytest arguments
    pytest_args = [
        str(test_dir),
        "-q",  # Quiet mode
        "--tb=no",  # Disable traceback
        "--no-header",  # Remove header
        "--no-summary",  # Remove summary
        f"--tavern-global-cfg={config_path}",
    ]

    # Add test type marker if not 'all'
    if test_type != TestType.ALL:
        pytest_args.extend(["-m", test_type])

    # Create result capture
    capture = ResultCapture()

    # Run pytest with capture
    exit_code = pytest.main(pytest_args, plugins=[capture])

    # Print formatted results
    click.echo(format_results(capture))

    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
