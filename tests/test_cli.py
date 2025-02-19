# ruff: noqa: S101, S105
import pytest
import yaml
from click.testing import CliRunner

from nbsapi_verify.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


def test_generate_config(runner, tmp_config_dir):
    """Test config generation with required parameters."""
    result = runner.invoke(
        cli,
        [
            "--generate",
            "--config-dir",
            str(tmp_config_dir),
            "--host",
            "http://test.com",
        ],
    )
    assert result.exit_code == 0

    # Check config file exists
    config_file = tmp_config_dir / "common.yaml"
    assert config_file.exists()

    # Verify config content
    with open(config_file) as f:
        config = yaml.safe_load(f)
    assert config["variables"]["host"] == "http://test.com"


def test_generate_config_with_auth(runner, tmp_config_dir):
    """Test config generation with auth credentials."""
    result = runner.invoke(
        cli,
        [
            "--generate",
            "--config-dir",
            str(tmp_config_dir),
            "--host",
            "http://test.com",
            "--username",
            "testuser",
            "--password",
            "testpass",
        ],
    )
    assert result.exit_code == 0

    with open(tmp_config_dir / "common.yaml") as f:
        config = yaml.safe_load(f)
    assert config["variables"]["username"] == "testuser"
    assert config["variables"]["password"] == "testpass"


def test_generate_requires_host(runner, tmp_config_dir):
    """Test that --generate requires --host."""
    result = runner.invoke(cli, ["--generate", "--config-dir", str(tmp_config_dir)])
    assert result.exit_code != 0
    assert "Error: --host is required" in result.output


def test_run_without_config(runner, tmp_config_dir):
    """Test running without an existing config file."""
    result = runner.invoke(cli, ["--config-dir", str(tmp_config_dir)])
    assert result.exit_code != 0
    assert "Error: Configuration file not found" in result.output


@pytest.fixture
def mock_test_dir(tmp_path):
    """Create a mock test directory with a simple test file."""
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    # Create a simple test file
    test_file = tests_dir / "test_simple.tavern.yaml"
    test_file.write_text("""
test_name: Simple test
stages:
  - name: Simple GET request
    request:
      url: "{host}/test"
      method: GET
    response:
      status_code: 200
""")

    # Make sure the parent directory is accessible
    return tests_dir
