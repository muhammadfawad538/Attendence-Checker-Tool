"""Entry point for Attendance Checker."""
import sys
from pathlib import Path

from attendance.loader import load_csv
from attendance.rules import (
    check_overwork,
    check_short_or_late,
    check_leave_pattern,
    check_bridge_leave,
    check_hours_on_leave,
    check_unexplained_absence,
)
from attendance.config import (
    OVERWORK_HOURS,
    OVERWORK_MIN_DAYS,
    OVERWORK_WINDOW_DAYS,
    SHORT_HOURS,
    SHORT_MIN_DAYS,
)


def main(csv_path: str) -> None:
    # Load data
    records, warnings = load_csv(csv_path)

    # Print warnings first
    for warning in warnings:
        print(f"WARNING: {warning}")

    print(f"\nAnalyzing {len(records)} records...")

    # Check rules
    flags = []
    flags.extend(check_overwork(records))
    flags.extend(check_short_or_late(records))
    flags.extend(check_leave_pattern(records))
    flags.extend(check_bridge_leave(records))
    flags.extend(check_hours_on_leave(records))
    flags.extend(check_unexplained_absence(records))

    # Print flags sorted by employee then date
    flags.sort(key=lambda x: (x[0], x[1]))

    # Print each flag with one-sentence explanation
    for emp, msg in flags:
        print(f"FLAG: {emp}: {msg}")

    # Summary
    print(f"\nDone. Found {len(flags)} flag(s).")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check.py data/hours.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    try:
        main(csv_path)
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        sys.exit(1)