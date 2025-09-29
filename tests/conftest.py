# conftest.py
import pytest
import datetime
from pathlib import Path
# tests/conftest.py
import sys
import os

# Get the path of the project root (the directory above 'tests')
# and add it to the Python search path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

REPORTS_DIR = Path("artifacts")
REPORTS_FILE = REPORTS_DIR / "reports.txt"

def pytest_runtest_logreport(report):
    """Hook to log results after each test phase."""
    if report.when == "call":  # only log test execution phase (not setup/teardown)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        test_name = report.nodeid  # includes test name + path
        test_dir = Path(report.fspath).parent
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if report.passed:
            outcome = "PASS"
            message = ""
        else:
            outcome = "FAIL"
            message = str(report.longrepr)

        log_line = f"[{timestamp}] {test_name} | Dir: {test_dir} | {outcome} {message}\n"

        with open(REPORTS_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)