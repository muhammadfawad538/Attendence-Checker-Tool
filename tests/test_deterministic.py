"""Test that the pipeline produces deterministic output."""
import subprocess
import sys


def test_deterministic_output():
    """Running check.py twice on the same data should produce identical output."""
    # Run first time
    result1 = subprocess.run(
        [sys.executable, "check.py", "data/hours.csv"],
        cwd="D:/must-quest",
        capture_output=True,
        text=True,
    )
    # Run second time
    result2 = subprocess.run(
        [sys.executable, "check.py", "data/hours.csv"],
        cwd="D:/must-quest",
        capture_output=True,
        text=True,
    )

    # Both should succeed
    assert result1.returncode == 0, f"First run failed: {result1.stderr}"
    assert result2.returncode == 0, f"Second run failed: {result2.stderr}"

    # Output should be identical
    assert result1.stdout == result2.stdout, (
        f"Output not deterministic!\n"
        f"First run:\n{result1.stdout}\n"
        f"Second run:\n{result2.stdout}"
    )
    assert result1.stderr == result2.stderr, "Stderr not deterministic"