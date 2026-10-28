"""Tests asserting exact flag text for each rule."""
from datetime import date

import pytest

from attendance.loader import Record
from attendance.rules import (
    check_overwork,
    check_short_or_late,
    check_leave_pattern,
    check_bridge_leave,
    check_hours_on_leave,
    check_unexplained_absence,
)


def make_record(employee: str, d: str, hours: float, leave: str = "") -> Record:
    return Record(employee=employee, date=date.fromisoformat(d), hours_worked=hours, leave_type=leave)


def test_overwork_exact_message():
    """Overwork flag message should match exact expected text."""
    records = [
        make_record("Alice", "2026-01-08", 12.0),
        make_record("Alice", "2026-01-09", 12.0),
        make_record("Alice", "2026-01-10", 12.0),
        make_record("Alice", "2026-01-11", 12.0),
    ]
    flags = check_overwork(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Alice"
    # Message should NOT contain employee name
    assert msg == "worked 11+ hours on 4 days in the 7-day window ending 2026-01-11."


def test_short_or_late_exact_message():
    """Short-hours flag message should match exact expected text."""
    records = [
        make_record("Bob", "2026-01-12", 3.0),
        make_record("Bob", "2026-01-13", 3.0),
        make_record("Bob", "2026-01-14", 3.0),
    ]
    flags = check_short_or_late(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Bob"
    assert msg == "worked under 4 hours for 3 consecutive working days from 2026-01-12 to 2026-01-14."


def test_leave_pattern_exact_message():
    """Leave pattern flag message should match exact expected text."""
    leaves = [
        make_record("Carol", "2026-01-16", 8.0, "annual"),   # Friday
        make_record("Carol", "2026-01-19", 8.0, "annual"),   # Monday
        make_record("Carol", "2026-01-23", 8.0, "annual"),   # Friday
        make_record("Carol", "2026-01-26", 8.0, "annual"),   # Monday
        make_record("Carol", "2026-01-30", 8.0, "annual"),   # Friday
    ]
    flags = check_leave_pattern(leaves)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Carol"
    # Exact grammar: "Carol took annual leave on 5 Mondays or Fridays in the 8 weeks ending 2026-01-30."
    assert msg == "took annual leave on 5 Mondays or Fridays in the 8 weeks ending 2026-01-30."


def test_bridge_leave_exact_message():
    """Bridge leave flag message should match exact expected text."""
    records = [
        make_record("Dave", "2026-01-19", 8.0, "annual"),
        make_record("Dave", "2026-01-20", 0.0, "public_holiday"),
    ]
    flags = check_bridge_leave(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Dave"
    assert msg == "took annual leave on 2026-01-19, the day before public holiday 2026-01-20."


def test_hours_on_leave_exact_message():
    """Hours on leave flag message should match exact expected text."""
    records = [
        make_record("Eve", "2026-01-19", 6.5, "sick"),
    ]
    flags = check_hours_on_leave(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Eve"
    assert msg == "logged 6.5 hours on 2026-01-19 but that day is marked as sick leave."


def test_unexplained_absence_exact_message():
    """Unexplained absence flag message should match exact expected text."""
    records = [
        make_record("Frank", "2026-01-28", 0.0, ""),
    ]
    flags = check_unexplained_absence(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Frank"
    assert msg == "has no hours and no leave recorded for working day 2026-01-28."