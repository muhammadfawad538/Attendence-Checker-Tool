"""Tests for full pipeline on files."""
import subprocess
import sys


def test_missing_file_clean_error():
    """Missing file should print one clear error and exit non-zero with no traceback."""
    result = subprocess.run(
        [sys.executable, "check.py", "nonexistent.csv"],
        cwd="D:/must-quest",
        capture_output=True,
        text=True,
    )
    # Should exit non-zero
    assert result.returncode == 1
    # Output should contain exactly one clear message
    output = result.stdout + result.stderr
    assert "File not found:" in output
    assert "nonexistent.csv" in output
    # Should NOT contain traceback
    assert "Traceback" not in output
    assert "FileNotFoundError" not in output


def test_empty_csv():
    """Empty CSV (header only) should print one error line and exit 1."""
    result = subprocess.run(
        [sys.executable, "check.py", "tests/data/hours_empty.csv"],
        cwd="D:/must-quest",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    output = result.stdout + result.stderr
    # Should have one ERROR line
    assert "ERROR: No valid data rows" in output
    assert "Traceback" not in output


def test_missing_hours_column():
    """CSV missing hours_worked column should print one error line and exit 1."""
    result = subprocess.run(
        [sys.executable, "check.py", "tests/data/hours_missing_hours.csv"],
        cwd="D:/must-quest",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    output = result.stdout + result.stderr
    # Should have one ERROR line
    assert "ERROR: Missing columns" in output
    assert "hours_worked" in output
    assert "Traceback" not in output
