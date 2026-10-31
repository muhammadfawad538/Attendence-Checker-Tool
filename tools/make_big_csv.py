#!/usr/bin/env python3
"""Generate large CSV files with planted patterns for performance testing."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

# Fixed random seed for reproducibility
random.seed(42)

# Public holidays in the date range
PUBLIC_HOLIDAYS = {
    date(2026, 1, 1),   # New Year's Day
    date(2026, 1, 20),  # MLK Day
    date(2026, 2, 16),  # Presidents Day
    date(2026, 5, 25),  # Memorial Day
    date(2026, 7, 3),   # Independence Day (observed)
    date(2026, 9, 7),   # Labor Day
    date(2026, 10, 12), # Columbus Day
    date(2026, 11, 11), # Veterans Day
    date(2026, 11, 26), # Thanksgiving
    date(2026, 12, 25), # Christmas
}

LEAVE_TYPES = ["", "annual", "sick", "public_holiday"]


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5


def is_working_day(d: date) -> bool:
    return d.weekday() < 5 and d not in PUBLIC_HOLIDAYS


def generate_csv(num_employees: int, num_days: int, output_path: Path) -> None:
    """Generate CSV with num_employees and num_days of data, with planted patterns."""
    start_date = date(2026, 1, 1)
    end_date = start_date + timedelta(days=num_days - 1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["employee", "date", "hours_worked", "leave_type"])

        # Generate employee names
        employees = [f"Emp{i:04d}" for i in range(1, num_employees + 1)]

        # Plant patterns for specific employees
        # Employee 0: Overwork pattern (11+ hours on 4+ days in 7-day window)
        # Employee 1: Short hours pattern (under 4h for 3+ consecutive working days)
        # Employee 2: Leave pattern (Mon/Fri leave 5+ times in 8 weeks)
        # Employee 3: Bridge leave (leave day before/after public holiday)
        # Employee 4: Hours on leave (hours > 0 on annual/sick day)
        # Employee 5: Unexplained absence (0 hours, no leave on working day)
        # Employee 6: Weekend work (hours > 0 on weekend)
        # Employee 7: Duplicate rows (same employee, date)
        # Employee 8: Part-time (expected hours = 4)
        # Employee 9: Mixed casing (Emp9, emp9, EMP9)

        for emp_idx, emp in enumerate(employees):
            current_date = start_date
            consecutive_short = 0

            while current_date <= end_date:
                # Default values
                hours = 8.0
                leave_type = ""

                if emp_idx == 0:  # Overwork pattern
                    # Plant 4 days with 12h in a 7-day window around day 10
                    day_offset = (current_date - start_date).days
                    if 8 <= day_offset <= 14 and day_offset % 2 == 0:
                        hours = 12.0

                elif emp_idx == 1:  # Short hours pattern
                    # Plant 3 consecutive working days with 3h around day 20
                    day_offset = (current_date - start_date).days
                    if is_working_day(current_date) and 18 <= day_offset <= 22:
                        hours = 3.0
                        consecutive_short += 1
                    else:
                        consecutive_short = 0

                elif emp_idx == 2:  # Leave pattern (Mon/Fri)
                    # Plant 5 Mon/Fri annual leaves in first 8 weeks
                    if current_date.weekday() in (0, 4):  # Mon or Fri
                        week_num = (current_date - start_date).days // 7
                        if week_num < 8 and week_num % 1 == 0:
                            leave_type = "annual"
                            hours = 0.0

                elif emp_idx == 3:  # Bridge leave
                    # Leave day before public holiday
                    if current_date + timedelta(days=1) in PUBLIC_HOLIDAYS:
                        leave_type = "annual"
                        hours = 0.0

                elif emp_idx == 4:  # Hours on leave
                    # One sick day with hours
                    day_offset = (current_date - start_date).days
                    if day_offset == 30:
                        leave_type = "sick"
                        hours = 6.5

                elif emp_idx == 5:  # Unexplained absence
                    # One working day with 0 hours, no leave
                    day_offset = (current_date - start_date).days
                    if is_working_day(current_date) and day_offset == 40:
                        hours = 0.0
                        leave_type = ""

                elif emp_idx == 6:  # Weekend work
                    if is_weekend(current_date):
                        hours = 8.0

                elif emp_idx == 7:  # Duplicate rows - will write twice
                    pass  # Normal row, will duplicate after

                elif emp_idx == 8:  # Part-time
                    hours = 4.0

                elif emp_idx == 9:  # Mixed casing - vary the name
                    # Handle name variation in the employee name itself
                    pass

                # Write row (possibly multiple times for duplicates)
                write_count = 2 if emp_idx == 7 else 1
                for _ in range(write_count):
                    # For mixed casing employee, vary the name
                    if emp_idx == 9:
                        if current_date.day % 3 == 0:
                            actual_emp = emp.lower()
                        elif current_date.day % 3 == 1:
                            actual_emp = emp.upper()
                        else:
                            actual_emp = emp
                    else:
                        actual_emp = emp

                    writer.writerow([actual_emp, current_date.isoformat(), hours, leave_type])

                current_date += timedelta(days=1)


if __name__ == "__main__":
    import sys

    # Default: 1x size (~140 rows = 7 employees * 20 days)
    multiplier = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    base_employees = 10
    base_days = 20

    num_employees = base_employees * multiplier
    num_days = base_days * multiplier

    output_dir = Path(__file__).parent.parent / "tests" / "data" / "big"
    output_path = output_dir / f"hours_{multiplier}x.csv"

    generate_csv(num_employees, num_days, output_path)
    print(f"Generated {output_path} with {num_employees} employees over {num_days} days")