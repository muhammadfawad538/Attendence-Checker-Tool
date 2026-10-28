"""Tests for attendance flag rules."""
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
    check_weekend_work,
)


def make_record(employee: str, d: str, hours: float, leave: str = "") -> Record:
    return Record(employee=employee, date=date.fromisoformat(d), hours_worked=hours, leave_type=leave)


# --- Overwork tests ---

def test_overwork_four_days_in_seven():
    """Alice has 4 days with 12h in a 7-day window (Jan 8-14). Should flag.
    Note: 2026-01-08=Thu, 01-09=Fri, 01-12=Mon, 01-13=Tue = 4 working days."""
    records = [
        make_record("Alice", "2026-01-08", 12.0),   # Thursday
        make_record("Alice", "2026-01-09", 12.0),   # Friday
        make_record("Alice", "2026-01-12", 12.0),   # Monday
        make_record("Alice", "2026-01-13", 12.0),   # Tuesday
        make_record("Alice", "2026-01-14", 8.0),    # Wednesday
    ]
    flags = check_overwork(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Alice"
    assert "11+ hours" in msg
    assert "4 days" in msg
    assert "7-day window" in msg
    assert "2026-01-13" in msg


def test_overwork_below_threshold():
    """Only 2 overwork days should not flag."""
    records = [
        make_record("Bob", "2026-01-08", 12.0),   # Thursday
        make_record("Bob", "2026-01-09", 12.0),   # Friday
        make_record("Bob", "2026-01-12", 8.0),    # Monday
    ]
    flags = check_overwork(records)
    assert flags == []


def test_overwork_exact_threshold():
    """Exactly 3 days with 11.0 hours in 7-day window should flag (>= 11).
    Using Thu-Fri-Mon (2026-01-08, 09, 12) as working days."""
    records = [
        make_record("Carol", "2026-01-08", 11.0),   # Thursday
        make_record("Carol", "2026-01-09", 11.0),   # Friday
        make_record("Carol", "2026-01-12", 11.0),   # Monday
    ]
    flags = check_overwork(records)
    assert len(flags) == 1
    assert "3 days" in flags[0][1]


# --- Short or late pattern tests ---

def test_short_three_consecutive():
    """Bob has 3 consecutive working days under 4h (Jan 12-14: Mon-Wed). Should flag."""
    records = [
        make_record("Bob", "2026-01-12", 3.0),   # Monday
        make_record("Bob", "2026-01-13", 3.0),   # Tuesday
        make_record("Bob", "2026-01-14", 3.0),   # Wednesday
        make_record("Bob", "2026-01-15", 8.0),   # Thursday
    ]
    flags = check_short_or_late(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Bob"
    assert "under 4 hours" in msg
    assert "consecutive working days" in msg
    assert "2026-01-14" in msg


def test_short_two_not_flagged():
    """Only 2 short days should not flag."""
    records = [
        make_record("Dave", "2026-01-12", 3.0),   # Monday
        make_record("Dave", "2026-01-13", 3.0),   # Tuesday
    ]
    flags = check_short_or_late(records)
    assert flags == []


def test_short_zero_hour_days_not_counted():
    """0-hour days should NOT count as short days; they trigger absence, not short-hours.
    Bob has hours 0, 0, 3 on consecutive working days - should give 2 absence flags and NO short-hours flag."""
    records = [
        make_record("Bob", "2026-01-12", 0.0),   # Monday
        make_record("Bob", "2026-01-13", 0.0),   # Tuesday
        make_record("Bob", "2026-01-14", 3.0),   # Wednesday
        make_record("Bob", "2026-01-15", 8.0),   # Thursday
    ]
    short_flags = check_short_or_late(records)
    absence_flags = check_unexplained_absence(records)

    # Short-hours should NOT flag because 0-hour days are not "short" (0 < hours < 4)
    assert short_flags == [], f"Expected no short-hours flag, got {short_flags}"

    # Unexplained absence should flag the two 0-hour days
    assert len(absence_flags) == 2, f"Expected 2 absence flags, got {len(absence_flags)}: {absence_flags}"


# --- Leave pattern tests ---

def test_leave_pattern_five_monday_friday():
    """Carol has 5 annual leaves on Mondays/Fridays. Should flag."""
    leaves = [
        make_record("Carol", "2026-01-16", 8.0, "annual"),   # Friday
        make_record("Carol", "2026-01-19", 8.0, "annual"),   # Monday
        make_record("Carol", "2026-01-23", 8.0, "annual"),   # Friday
        make_record("Carol", "2026-01-26", 8.0, "annual"),   # Monday
        make_record("Carol", "2026-01-30", 8.0, "annual"),   # Friday
    ]
    flags = check_leave_pattern(leaves)
    assert len(flags) >= 1
    msg = flags[0][1]
    assert "Mondays or Fridays" in msg
    assert "5" in msg or "annual" in msg


# --- Bridge leave tests ---

def test_bridge_leave_before_public_holiday():
    """Dave has annual leave on day before public holiday. Should flag."""
    records = [
        make_record("Dave", "2026-01-19", 8.0, "annual"),
        make_record("Dave", "2026-01-20", 0.0, "public_holiday"),
    ]
    flags = check_bridge_leave(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Dave"
    assert "2026-01-19" in msg
    assert "2026-01-20" in msg
    assert "public holiday" in msg


def test_bridge_leave_after_public_holiday():
    """Leave the day after a public holiday should also flag."""
    records = [
        make_record("Eve", "2026-01-20", 8.0, "public_holiday"),
        make_record("Eve", "2026-01-21", 8.0, "annual"),
    ]
    flags = check_bridge_leave(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Eve"
    assert "2026-01-20" in msg
    assert "2026-01-21" in msg


# --- Hours on leave tests ---

def test_hours_on_sick_leave():
    """Eve logged 6.5 hours on sick leave. Should flag."""
    records = [
        make_record("Eve", "2026-01-19", 6.5, "sick"),
    ]
    flags = check_hours_on_leave(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Eve"
    assert "6.5 hours" in msg
    assert "sick leave" in msg


def test_hours_no_match():
    """Hours logged on normal work days should not flag."""
    records = [
        make_record("Frank", "2026-01-19", 8.0, ""),
    ]
    flags = check_hours_on_leave(records)
    assert flags == []


# --- Unexplained absence tests ---

def test_unexplained_absence():
    """Frank has 0.0 hours on a working day with no leave. Should flag."""
    records = [
        make_record("Frank", "2026-01-28", 0.0, ""),
    ]
    flags = check_unexplained_absence(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Frank"
    assert "no hours" in msg
    assert "no leave" in msg
    assert "2026-01-28" in msg


# --- Weekend work tests ---

def test_weekend_work_flagged():
    """Hours on Saturday/Sunday should be flagged separately, not count as overwork."""
    records = [
        make_record("Alice", "2026-01-10", 12.0),   # Saturday
        make_record("Alice", "2026-01-11", 8.0),    # Sunday
    ]
    flags = check_weekend_work(records)
    assert len(flags) == 1
    emp, msg = flags[0]
    assert emp == "Alice"
    assert "weekend" in msg.lower()
    assert "2026-01-10" in msg
    assert "2026-01-11" in msg
    assert "12" in msg or "8" in msg


def test_weekend_work_not_in_overwork():
    """Weekend hours should not be counted by overwork rule."""
    records = [
        make_record("Alice", "2026-01-08", 12.0),   # Thursday
        make_record("Alice", "2026-01-09", 12.0),   # Friday
        make_record("Alice", "2026-01-10", 12.0),   # Saturday
        make_record("Alice", "2026-01-11", 12.0),   # Sunday
    ]
    overwork_flags = check_overwork(records)
    weekend_flags = check_weekend_work(records)

    # Overwork should only see Thu+Fri = 2 days, so no flag (needs 3)
    assert overwork_flags == [], f"Overwork should not count weekends: {overwork_flags}"

    # Weekend work should flag (4 weekend days in this test)
    assert len(weekend_flags) == 1
    emp, msg = weekend_flags[0]
    assert emp == "Alice"
    assert "weekend" in msg.lower()


def test_weekend_work_no_weekends():
    """No weekend days should produce no flag."""
    records = [
        make_record("Bob", "2026-01-12", 8.0),   # Monday
        make_record("Bob", "2026-01-13", 8.0),   # Tuesday
    ]
    flags = check_weekend_work(records)
    assert flags == []