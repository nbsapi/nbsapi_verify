from _pytest.reports import TestReport


class ResultCapture:
    def __init__(self):
        self.passed: list[str] = []
        self.failed: list[dict[str, str]] = []
        self.skipped: list[str] = []
        self.total_duration: float = 0.0

    def pytest_runtest_logreport(self, report: TestReport):
        if report.when == "call":  # Only process the test result, not setup/teardown
            test_id = report.nodeid
            if report.passed:
                self.passed.append(test_id)
            elif report.failed:
                self.failed.append(
                    {
                        "id": test_id,
                        "error": str(report.longrepr)
                        if report.longrepr
                        else "No error details available",
                    }
                )
            elif report.skipped:
                self.skipped.append(test_id)

            if hasattr(report, "duration"):
                self.total_duration += report.duration


def format_results(capture: ResultCapture) -> str:
    """Format test results into a nice string, following common test output conventions."""
    output = []
    failures = False

    # Summary line
    total = len(capture.passed) + len(capture.failed) + len(capture.skipped)
    output.append(f"\nNbSAPI Conformance Test Summary ({capture.total_duration:.1f}s)")
    output.append("=" * 40)

    # Short summary counts
    summary_parts = []
    if capture.passed:
        summary_parts.append(f"{len(capture.passed)} passed")
    if capture.failed:
        summary_parts.append(f"{len(capture.failed)} failed")
    if capture.skipped:
        summary_parts.append(f"{len(capture.skipped)} skipped ⏭️")
    output.append(", ".join(summary_parts))

    # Only show detailed output for failures
    if capture.failed:
        failures = True
        output.append("\nFailures")
        output.append("-" * 40)
        for test in capture.failed:
            output.append(f"❌ {test['id']}")
            # Format error message with proper indentation
            error_lines = test["error"].split("\n")
            for line in error_lines:
                output.append(f"    {line}")
            output.append("")  # Empty line between failures

    # If there were skips, list them briefly
    if capture.skipped:
        output.append("\nSkipped Tests")
        output.append("-" * 40)
        for test in capture.skipped:
            output.append(f"⏭️  {test}")
    if not failures:
        output.append(
            "\n✨ Congratulations, your NbSAPI implementation is conformant! ✨"
        )

    return "\n".join(output)
