"""Tests for input error handling (empty CSV, missing columns)."""
import subprocess
import sys


def test_empty_csv_exits_with_error():
    """Empty CSV (header only) should print ERROR and exit 1."""
    result = subprocess.run(
        [sys.executable, "check.py", "tests/data/hours_empty.csv"],
        cwd="D:/must-quest",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"
    output = result.stdout + result.stderr
    assert "ERROR: No valid data rows" in output, f"Expected ERROR message, got: {output}"
    assert "Traceback" not in output


def test_missing_hours_column_exits_with_error():
    """CSV missing hours_worked column should print ERROR and exit 1."""
    result = subprocess.run(
        [sys.executable, "check.py", "tests/data/hours_missing_hours.csv"],
        cwd="D:/must-quest",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"
    output = result.stdout + result.stderr
    assert "ERROR: Missing columns" in output, f"Expected ERROR message, got: {output}"
    assert "hours_worked" in output
    assert "Traceback" not in output