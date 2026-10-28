"""
CSV loader and data validation.
Returns (records, warnings) where records is a list of dicts with parsed fields,
and warnings is a list of data-quality warning strings.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Record:
    employee: str
    date: date
    hours_worked: float
    leave_type: str  # "", "annual", "sick", "public_holiday"


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

            records.append(Record(employee=emp, date=dt, hours_worked=hrs, leave_type=lt))

    # Sort deterministically by employee then date
    records.sort(key=lambda r: (r.employee, r.date))
    return records, warnings