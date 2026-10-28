"""
Flag rules for attendance patterns.
Each function returns a list of (employee, message) tuples.
"""
from collections import defaultdict
from datetime import date, timedelta

from attendance import config
from attendance.loader import Record


def is_working_day(d: date) -> bool:
    """Return True if date is a working day (Mon-Fri)."""
    return d.weekday() < 5  # Monday=0, Friday=4


def is_weekend(d: date) -> bool:
    """Return True if date is Saturday or Sunday."""
    return d.weekday() >= 5  # Saturday=5, Sunday=6


def get_expected_hours(employee: str) -> float:
    """Return expected hours per day for an employee (default 8.0)."""
    return config.EXPECTED_HOURS.get(employee, 8.0)


def check_overwork(records: list[Record]) -> list[tuple[str, str]]:
    """Check for 11+ hours on N or more days in a rolling window."""
    if not records:
        return []

    # Group by employee
    by_emp: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        # Only count working days toward overwork (exclude weekends)
        if not is_weekend(r.date):
            by_emp[r.employee].append(r)

    flags: list[tuple[str, str]] = []
    threshold_hours = config.OVERWORK_HOURS
    min_days = config.OVERWORK_MIN_DAYS
    window = config.OVERWORK_WINDOW_DAYS

    for emp, emp_records in by_emp.items():
        # Find all overwork days
        overwork_days = [r for r in emp_records if r.hours_worked >= threshold_hours]
        if len(overwork_days) < min_days:
            continue

        # Sort by date
        overwork_days.sort(key=lambda r: r.date)

        # Check each day as end of window, find the window with highest count
        best_count = 0
        best_end = None
        for end_record in overwork_days:
            window_start = end_record.date - timedelta(days=window - 1)
            count = sum(1 for r in overwork_days if window_start <= r.date <= end_record.date)
            if count > best_count:
                best_count = count
                best_end = end_record.date
            elif count == best_count and best_end is None:
                best_end = end_record.date

        if best_count >= min_days and best_end is not None:
            msg = (
                f"worked {threshold_hours:g}+ hours on {best_count} days "
                f"in the {window}-day window ending {best_end.isoformat()}."
            )
            flags.append((emp, msg))

    return flags


def check_short_or_late(records: list[Record]) -> list[tuple[str, str]]:
    """Check for 0 < hours < threshold on N consecutive working days.
    Threshold is half of expected hours per day per employee (default 4h for full-time 8h)."""
    if not records:
        return []

    by_emp: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        by_emp[r.employee].append(r)

    flags: list[tuple[str, str]] = []
    min_consecutive = config.SHORT_MIN_DAYS

    for emp, emp_records in by_emp.items():
        # Sort by date
        emp_records.sort(key=lambda r: r.date)

        # Filter to working days
        working_days = [r for r in emp_records if is_working_day(r.date)]

        # Get threshold for this employee (half of expected hours)
        expected = get_expected_hours(emp)
        threshold = expected / 2.0

        consecutive = 0
        streak_start = None

        for r in working_days:
            # Short day: 0 < hours < threshold (0-hour days are absences, not short days)
            if 0 < r.hours_worked < threshold:
                if consecutive == 0:
                    streak_start = r.date
                consecutive += 1
                if consecutive >= min_consecutive:
                    msg = (
                        f"worked under {threshold:g} hours for {consecutive} consecutive working days "
                        f"from {streak_start.isoformat()} to {r.date.isoformat()}."
                    )
                    flags.append((emp, msg))
                    break  # One flag per employee
            else:
                consecutive = 0
                streak_start = None

    return flags


def check_leave_pattern(records: list[Record]) -> list[tuple[str, str]]:
    """Check for leave on Monday or Friday repeatedly."""
    if not records:
        return []

    by_emp: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        by_emp[r.employee].append(r)

    flags: list[tuple[str, str]] = []
    min_count = config.LEAVE_PATTERN_MIN_COUNT
    lookback_weeks = config.LEAVE_PATTERN_WEEKS
    lookback_days = lookback_weeks * 7

    for emp, emp_records in by_emp.items():
        # Find leave records (annual, sick, etc., but not public_holiday)
        leave_records = [r for r in emp_records if r.leave_type in ("annual", "sick")]
        if not leave_records:
            continue

        # Find the latest date to anchor the lookback window
        latest_date = max(r.date for r in leave_records)
        window_start = latest_date - timedelta(days=lookback_days)

        # Count Monday/Friday leaves in window
        mf_leaves = [
            r for r in leave_records
            if window_start <= r.date <= latest_date
            and r.date.weekday() in (0, 4)  # Monday=0, Friday=4
        ]

        if len(mf_leaves) >= min_count:
            # Count by type for message
            annual_count = sum(1 for r in mf_leaves if r.leave_type == "annual")
            sick_count = sum(1 for r in mf_leaves if r.leave_type == "sick")

            # Determine leave type string for message
            if annual_count and sick_count:
                leave_type_str = f"{annual_count} annual or {sick_count} sick"
            elif annual_count:
                leave_type_str = "annual"
            elif sick_count:
                leave_type_str = "sick"
            else:
                leave_type_str = "leave"

            msg = (
                f"took {leave_type_str} leave on {len(mf_leaves)} Mondays or Fridays "
                f"in the {lookback_weeks} weeks ending {latest_date.isoformat()}."
            )
            flags.append((emp, msg))

    return flags


def check_bridge_leave(records: list[Record]) -> list[tuple[str, str]]:
    """Check for leave the day before or after a public holiday."""
    if not records:
        return []

    by_emp: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        by_emp[r.employee].append(r)

    flags: list[tuple[str, str]] = []

    for emp, emp_records in by_emp.items():
        # Find public holidays
        public_holidays = {r.date for r in emp_records if r.leave_type == "public_holiday"}
        if not public_holidays:
            continue

        # Find leave days (annual, sick)
        leave_days = [r for r in emp_records if r.leave_type in ("annual", "sick")]

        for leave in leave_days:
            # Check day before
            if leave.date - timedelta(days=1) in public_holidays:
                ph_date = leave.date - timedelta(days=1)
                msg = (
                    f"took {leave.leave_type} leave on {leave.date.isoformat()}, "
                    f"the day after public holiday {ph_date.isoformat()}."
                )
                flags.append((emp, msg))
            # Check day after
            elif leave.date + timedelta(days=1) in public_holidays:
                ph_date = leave.date + timedelta(days=1)
                msg = (
                    f"took {leave.leave_type} leave on {leave.date.isoformat()}, "
                    f"the day before public holiday {ph_date.isoformat()}."
                )
                flags.append((emp, msg))

    return flags


def check_hours_on_leave(records: list[Record]) -> list[tuple[str, str]]:
    """Check for hours logged on a day marked as leave."""
    flags: list[tuple[str, str]] = []

    for r in records:
        if r.leave_type in ("annual", "sick") and r.hours_worked > 0:
            msg = (
                f"logged {r.hours_worked:g} hours on {r.date.isoformat()} "
                f"but that day is marked as {r.leave_type} leave."
            )
            flags.append((r.employee, msg))

    # Sort by employee then date for deterministic output
    flags.sort(key=lambda x: (x[0], x[1]))
    return flags


def check_unexplained_absence(records: list[Record]) -> list[tuple[str, str]]:
    """Check for working day with no hours and no leave record."""
    if not records:
        return []

    by_emp: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        by_emp[r.employee].append(r)

    flags: list[tuple[str, str]] = []

    for emp, emp_records in by_emp.items():
        # Group by date (should be 1:1 from loader validation, but just in case)
        by_date: dict[date, Record] = {r.date: r for r in emp_records}

        for r in emp_records:
            # Only check working days (Mon-Fri, not public holiday)
            if not is_working_day(r.date):
                continue
            if r.leave_type == "public_holiday":
                continue
            if r.leave_type in ("annual", "sick"):
                continue
            # Working day with no leave
            if r.hours_worked == 0:
                msg = (
                    f"has no hours and no leave recorded for working day {r.date.isoformat()}."
                )
                flags.append((emp, msg))

    # Sort for deterministic output
    flags.sort(key=lambda x: (x[0], x[1]))
    return flags


def check_weekend_work(records: list[Record]) -> list[tuple[str, str]]:
    """Check for hours worked on weekends (Saturday/Sunday)."""
    if not records:
        return []

    by_emp: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        by_emp[r.employee].append(r)

    flags: list[tuple[str, str]] = []

    for emp, emp_records in by_emp.items():
        weekend_records = [r for r in emp_records if is_weekend(r.date) and r.hours_worked > 0]
        if not weekend_records:
            continue

        # Sort by date for deterministic output
        weekend_records.sort(key=lambda r: r.date)

        dates = [r.date.isoformat() for r in weekend_records]
        hours_str = ", ".join(f"{r.hours_worked:g}h on {r.date.isoformat()}" for r in weekend_records)

        if len(weekend_records) == 1:
            msg = f"worked {weekend_records[0].hours_worked:g} hours on weekend day {weekend_records[0].date.isoformat()}."
        else:
            msg = f"worked {len(weekend_records)} weekend day(s): {hours_str}."

        flags.append((emp, msg))

    # Sort by employee for deterministic output
    flags.sort(key=lambda x: x[0])
    return flags