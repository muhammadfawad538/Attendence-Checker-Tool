"""Performance tests for attendance rules."""
import time
import pytest
from pathlib import Path

from attendance.loader import load_csv
from attendance.rules import check_weekend_work


def test_weekend_work_performance_100x():
    """check_weekend_work on 100x data (2M records) should complete in under 5 seconds."""
    records, _ = load_csv('tests/data/big/hours_100x.csv')
    assert len(records) > 1000000  # Sanity check

    start = time.perf_counter()
    flags = check_weekend_work(records)
    elapsed = time.perf_counter() - start

    print(f"check_weekend_work took {elapsed:.3f}s on {len(records)} records, produced {len(flags)} flags")
    assert elapsed < 5.0, f"check_weekend_work took {elapsed:.3f}s, expected < 5.0s"


def test_check_py_performance_100x():
    """Full check.py run on 100x data should complete in under 30 seconds."""
    import subprocess
    import sys

    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "check.py", "tests/data/big/hours_100x.csv"],
        cwd="D:/must-quest", capture_output=True, text=True
    )
    elapsed = time.perf_counter() - start

    print(f"check.py took {elapsed:.3f}s on 100x data, returncode={result.returncode}")
    assert elapsed < 30.0, f"check.py took {elapsed:.3f}s, expected < 30.0s"
    assert result.returncode == 0, f"check.py failed: {result.stderr}"


if __name__ == "__main__":
    # Allow running standalone
    test_weekend_work_performance_100x()
    print("Test passed!")
    test_check_py_performance_100x()
    print("Test passed!")