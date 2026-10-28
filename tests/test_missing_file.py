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
