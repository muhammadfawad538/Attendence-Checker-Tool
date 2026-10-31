"""Entry point for Attendance Checker."""
import sys
import argparse
import json
from pathlib import Path

from attendance.loader import load_csv
from attendance.rules import (
    check_overwork, check_short_or_late, check_leave_pattern,
    check_bridge_leave, check_hours_on_leave, check_unexplained_absence,
    check_weekend_work
)


def parse_args():
    parser = argparse.ArgumentParser(description="Attendance Checker")
    parser.add_argument("csv_path", help="Path to CSV file")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if any warnings exist")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    return parser.parse_args()


def main(csv_path: str, strict: bool = False, output_format: str = "text") -> None:
    # Load data
    records, warnings = load_csv(csv_path)
    skipped_rows = sum(1 for w in warnings if any(kw in w for kw in [
        "missing required field",
        "duplicate entry",
        "invalid date",
        "invalid hours",
        "invalid leave_type",
    ]))

    # Handle critical data quality issues: missing columns
    for warning in warnings:
        if "Missing columns" in warning:
            print(f"ERROR: {warning}")
            sys.exit(1)

    # Print all non-critical warnings (including per-row warnings)
    for warning in warnings:
        if output_format == "text":
            print(f"WARNING: {warning}")

    # Print skipped rows summary (always, even if no valid records)
    if output_format == "text":
        skipped_msg = f"Skipped {skipped_rows} row(s)."
        print(skipped_msg)

    if len(records) == 0:
        print(f"ERROR: No valid data rows in {csv_path}")
        sys.exit(1)

    print(f"\nAnalyzing {len(records)} records...")

    # Check rules
    flags = []
    flags.extend(check_overwork(records))
    flags.extend(check_short_or_late(records))
    flags.extend(check_leave_pattern(records))
    flags.extend(check_bridge_leave(records))
    flags.extend(check_hours_on_leave(records))
    flags.extend(check_unexplained_absence(records))
    flags.extend(check_weekend_work(records))

    # Print flags sorted by employee then date
    flags.sort(key=lambda x: (x[0], x[1]))

    # Print each flag with one-sentence explanation
    if output_format == "text":
        for emp, msg in flags:
            print(f"FLAG: {emp}: {msg}")
    else:  # JSON format
        output = {
            "flags": [
                {"employee": emp, "message": msg}
                for emp, msg in flags
            ],
            "warnings": [w for w in warnings if "Missing columns" not in w],
            "skipped_rows": skipped_rows,
            "total_records": len(records)
        }
        print(json.dumps(output, indent=2))

    # Summary (only in text mode)
    if output_format == "text":
        print(f"\nDone. Found {len(flags)} flag(s).")

    # Strict mode: exit with code 1 if any warnings exist
    if strict and len(warnings) > 0:
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    try:
        main(args.csv_path, strict=args.strict, output_format=args.format)
    except FileNotFoundError:
        print(f"File not found: {args.csv_path}")
        sys.exit(1)