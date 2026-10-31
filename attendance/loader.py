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
    name_map: dict[str, str] = {}  # normalized name -> canonical name

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            warnings.append("Missing columns: {'employee', 'date', 'hours_worked', 'leave_type'}")
            return records, warnings

        required = {"employee", "date", "hours_worked", "leave_type"}
        if not required.issubset(set(header)):
            missing = required - set(header)
            warnings.append(f"Missing columns: {missing}")
            return records, warnings

        # Map column names to indices
        col_idx = {name: idx for idx, name in enumerate(header)}
        emp_idx = col_idx["employee"]
        date_idx = col_idx["date"]
        hours_idx = col_idx["hours_worked"]
        leave_idx = col_idx["leave_type"]
        max_required = max(emp_idx, date_idx, hours_idx, leave_idx)

        # Local refs for speed
        seen_add = seen.add
        seen_contains = seen.__contains__
        name_map_get = name_map.get
        warnings_append = warnings.append
        records_append = records.append
        date_fromiso = date.fromisoformat
        date_fromiso_split = date.fromisoformat  # alias, we'll optimize below
        seen_first_set = seen_first.__setitem__

        for i, row in enumerate(reader, start=2):  # line numbers (1=header)
            # Check if row has all 4 required fields
            if len(row) <= max_required:
                emp = row[emp_idx].strip() if emp_idx < len(row) else ""
                dt_str = row[date_idx].strip() if date_idx < len(row) else ""
                hrs_str = row[hours_idx].strip() if hours_idx < len(row) else ""
                warnings_append(f"Line {i}: missing required field(s) (employee={emp!r}, date={dt_str!r}, hours={hrs_str!r})")
                continue

            emp = row[emp_idx].strip()
            dt_str = row[date_idx].strip()
            hrs_str = row[hours_idx].strip()
            lt_str = row[leave_idx].strip()

            # Check for missing fields
            if not emp or not dt_str or not hrs_str:
                warnings_append(f"Line {i}: missing required field(s) (employee={emp!r}, date={dt_str!r}, hours={hrs_str!r})")
                continue

            # Normalize employee name - inline for speed
            emp_trimmed = emp
            norm = emp_trimmed.lower()
            canonical = name_map_get(norm)
            if canonical is None:
                canonical = emp_trimmed
                name_map[norm] = emp_trimmed
            elif canonical != emp_trimmed:
                warnings_append(f"Line {i}: merged employee name {emp_trimmed!r} -> {canonical!r}")

            # Parse leave type early for duplicate check
            lt = lt_str.strip().lower()

            # Check for duplicate (employee, date) - also detect different leave types on same day
            key = (canonical, dt_str)
            if seen_contains(key):
                first_row_info = seen_first.get(key)
                if first_row_info:
                    # Check if leave type differs from first row
                    if first_row_info['leave_type'] != lt and first_row_info['leave_type'] and lt:
                        warnings_append(f"Line {i}: employee={canonical!r}, date={dt_str!r} has multiple leave types: {first_row_info['leave_type']!r} and {lt!r}")
                    else:
                        warnings_append(f"Line {i}: duplicate entry for employee={canonical!r}, date={dt_str!r} (kept first row with {first_row_info['hours']!r} hours, dropped duplicate with {hrs_str!r} hours)")
                else:
                    warnings_append(f"Line {i}: duplicate entry for employee={canonical!r}, date={dt_str!r}")
                continue
            seen_add(key)

            # Parse date - inline
            try:
                dt = date_fromiso(dt_str)
            except (ValueError, AttributeError):
                warnings_append(f"Line {i}: invalid date {dt_str!r}")
                continue

            # Parse hours - inline
            try:
                hrs = float(hrs_str)
            except (ValueError, AttributeError):
                warnings_append(f"Line {i}: invalid hours {hrs_str!r} (must be 0-24)")
                continue

            # Validate hours range
            if hrs < 0 or hrs > 24:
                warnings_append(f"Line {i}: invalid hours {hrs_str!r} (must be 0-24)")
                continue
            if hrs > 12:
                warnings_append(f"Line {i}: unusual hours {hrs_str!r} (>12)")

            # Validate leave type
            if lt not in ("", "annual", "sick", "public_holiday"):
                warnings_append(f"Line {i}: invalid leave_type {lt_str!r} (must be empty, annual, sick, or public_holiday)")
                continue

            # Store first occurrence info for duplicate detection
            if key not in seen_first:
                seen_first[key] = {'hours': hrs_str, 'leave_type': lt_str}

            records_append(Record(employee=canonical, date=dt, hours_worked=hrs, leave_type=lt))

    # Sort deterministically by employee then date
    records.sort(key=lambda r: (r.employee, r.date))

    # Check for missing working-day rows (gaps in calendar)
    # Optimized: only check gaps between consecutive dates per employee
    from collections import defaultdict
    by_emp = defaultdict(list)
    for r in records:
        by_emp[r.employee].append(r)

    for emp, emp_records in by_emp.items():
        if not emp_records:
            continue
        # Sort dates per employee
        emp_dates = sorted(set(r.date for r in emp_records))
        if len(emp_dates) <= 1:
            continue
        for j in range(len(emp_dates) - 1):
            d1 = emp_dates[j]
            d2 = emp_dates[j+1]
            diff = (d2 - d1).days
            if diff > 1:
                current = d1 + timedelta(days=1)
                while current < d2:
                    if current.weekday() < 5:  # is_working_day inlined
                        warnings_append(f"Missing working day for {emp}: {current.isoformat()}")
                    current += timedelta(days=1)

    return records, warnings