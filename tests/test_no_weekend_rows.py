"""Test that data/hours.csv has no weekend rows except for Grace."""
from attendance.loader import load_csv
from datetime import date


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5  # Saturday=5, Sunday=6


def test_no_weekend_rows_except_grace():
    """Ensure data/hours.csv has no weekend rows for employees other than Grace."""
    records, warnings = load_csv("data/hours.csv")

    weekend_employees = set()
    for r in records:
        if is_weekend(r.date):
            weekend_employees.add(r.employee)

    # Only Grace should have weekend rows
    assert weekend_employees == {"Grace"}, (
        f"Only Grace should have weekend rows, but found: {weekend_employees}"
    )

    # Grace should have exactly 2 weekend rows (2026-01-17 Sat, 2026-01-18 Sun)
    grace_weekend = [r for r in records if r.employee == "Grace" and is_weekend(r.date)]
    assert len(grace_weekend) == 2, f"Grace should have 2 weekend rows, got {len(grace_weekend)}"
    dates = {r.date for r in grace_weekend}
    assert date(2026, 1, 17) in dates, "Grace should have 2026-01-17 (Sat)"
    assert date(2026, 1, 18) in dates, "Grace should have 2026-01-18 (Sun)"