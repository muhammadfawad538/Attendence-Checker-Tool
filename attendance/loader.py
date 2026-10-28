"""
CSV loader and data validation.
Returns (records, warnings) where records is a list of dicts with parsed fields,
and warnings is a list of data-quality warning strings.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional


@dataclass
class Record:
    employee: str
    date: date
    hours_worked: float
    leave_type: str  # "", "annual", "sick", "public_holiday"


def is_working_day(d: date) -> bool:
    """Return True if date is a working day (Mon-Fri)."""
    return d.weekday() < 5  # Monday=0, Friday=4


def parse_date(s: str) -> Optional[date]:
    """Parse ISO date YYYY-MM-DD, return None on failure."""
    try:
        return date.fromisoformat(s.strip())
    except (ValueError, AttributeError):
        return None


def parse_hours(s: str) -> Optional[float]:
    """Parse hours as float, return None on failure."""
    try:
        val = float(s.strip())
        if val < 0:
            return None
        return val
    except (ValueError, AttributeError):
        return None


def validate_leave_type(s: str) -> Optional[str]:
    """Validate leave_type, return normalized or None if invalid."""
    s = s.strip().lower()
    if s in ("", "annual", "sick", "public_holiday"):
        return s
    return None


def load_csv(path: str) -> tuple[list[Record], list[str]]:
    """
    Load CSV and return (records, warnings).
    Bad rows are reported as warnings but not included in records.
    """
    import csv

    records: list[Record] = []
    warnings: list[str] = []
    seen: set[tuple[str, str]] = set()
    seen_first: dict[tuple[str, str], dict] = {}  # track first occurrence of duplicates

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"employee", "date", "hours_worked", "leave_type"}
        if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
            missing = required - set(reader.fieldnames or [])
            warnings.append(f"Missing columns: {missing}")
            return records, warnings

        for i, row in enumerate(reader, start=2):  # line numbers (1=header)
            emp = row.get("employee", "").strip()
            dt_str = row.get("date", "").strip()
            hrs_str = row.get("hours_worked", "").strip()
            lt_str = row.get("leave_type", "").strip()

            # Check for missing fields
            if not emp or not dt_str or not hrs_str:
                warnings.append(f"Line {i}: missing required field(s) (employee={emp!r}, date={dt_str!r}, hours={hrs_str!r})")
                continue

            # Check for duplicate (employee, date)
            key = (emp, dt_str)
            if key in seen:
                # Find the first row's hours
                first_row_info = seen_first.get(key)
                if first_row_info:
                    warnings.append(f"Line {i}: duplicate entry for employee={emp!r}, date={dt_str!r} (kept first row with {first_row_info['hours']!r} hours, dropped duplicate with {hrs_str!r} hours)")
                else:
                    warnings.append(f"Line {i}: duplicate entry for employee={emp!r}, date={dt_str!r}")
                continue
            seen.add(key)

            # Parse and validate
            dt = parse_date(dt_str)
            if dt is None:
                warnings.append(f"Line {i}: invalid date {dt_str!r}")
                continue

            hrs = parse_hours(hrs_str)
            if hrs is None:
                warnings.append(f"Line {i}: invalid hours {hrs_str!r} (must be non-negative number)")
                continue

            lt = validate_leave_type(lt_str)
            if lt is None:
                warnings.append(f"Line {i}: invalid leave_type {lt_str!r} (must be empty, annual, sick, or public_holiday)")
                continue

            # Store first occurrence info for duplicate detection
            if key not in seen_first:
                seen_first[key] = {'hours': hrs_str, 'leave_type': lt_str}

            records.append(Record(employee=emp, date=dt, hours_worked=hrs, leave_type=lt))

    # Sort deterministically by employee then date
    records.sort(key=lambda r: (r.employee, r.date))

    # Check for missing working-day rows (gaps in calendar)
    from collections import defaultdict
    by_emp = defaultdict(list)
    for r in records:
        by_emp[r.employee].append(r)

    for emp, emp_records in by_emp.items():
        if not emp_records:
            continue
        dates = {r.date for r in emp_records}
        min_date = min(dates)
        max_date = max(dates)
        current = min_date
        while current <= max_date:
            if is_working_day(current) and current not in dates:
                warnings.append(f"Missing working day for {emp}: {current.isoformat()}")
            current += timedelta(days=1)

    return records, warnings