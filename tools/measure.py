#!/usr/bin/env python3
"""Measure time and memory for check.py on different CSV sizes."""
import subprocess
import time
import sys
from pathlib import Path

# Add parent directory to path for attendance module imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_check(csv_path):
    """Run check.py and measure time and memory."""
    csv_path = str(csv_path)
    # Time measurement via subprocess (captures real wall-clock time)
    start = time.perf_counter()
    result = subprocess.run([sys.executable, "check.py", csv_path],
                          cwd=Path(__file__).parent.parent, capture_output=True, text=True)
    elapsed = time.perf_counter() - start

    # Try to measure memory via tracemalloc on the loader in a separate call
    peak_mb = -1
    records_count = 0
    warnings_count = 0
    try:
        import tracemalloc
        tracemalloc.start()
        from attendance.loader import load_csv
        records, warnings = load_csv(csv_path)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_mb = peak / 1024 / 1024
        records_count = len(records)
        warnings_count = len(warnings)
    except Exception:
        try:
            import tracemalloc
            tracemalloc.stop()
        except Exception:
            pass
        # Memory measurement failed, just report subprocess metrics
        pass

    return {
        'time_sec': elapsed,
        'peak_mb': peak_mb,
        'records': records_count,
        'warnings': warnings_count,
        'returncode': result.returncode
    }


if __name__ == "__main__":
    sizes = [1, 10, 100]
    print(f"{'Size':<10} {'Rows':>10} {'Time (s)':>10} {'Peak MB':>10} {'Records':>10} {'Warnings':>10}")
    print("-" * 60)

    for mult in sizes:
        csv_path = Path(__file__).parent.parent / "tests" / "data" / "big" / f"hours_{mult}x.csv"
        if not csv_path.exists():
            print(f"{mult}x: FILE NOT FOUND")
            continue

        metrics = run_check(csv_path)
        print(f"{mult}x{'':<6} {metrics['records']:>10} {metrics['time_sec']:>10.2f} {metrics['peak_mb']:>10.1f} {metrics['records']:>10} {metrics['warnings']:>10}")