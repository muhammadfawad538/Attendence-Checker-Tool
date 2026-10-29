#!/usr/bin/env python3
"""Generate individual messy CSV test cases in tests/data/cases/"""
import os

cases_dir = r"D:/must-quest/tests/data/cases"
os.makedirs(cases_dir, exist_ok=True)

# Fix short_row.csv to have all required columns
cases = {
    "short_row.csv": "employee,date,hours_worked,leave_type\nAlice,2026-01-01,8.0,sick\nBob,2026-01-02,3.0,annual\n",
    "truly_empty_line.csv": "employee,date,hours_worked,leave_type\n\nAlice,2026-01-01,8.0,sick\n",
    "empty_comma_row.csv": "employee,date,hours_worked,leave_type\n,\n,\nAlice,2026-01-01,8.0,sick\n",
    "mixed_dates.csv": "employee,date,hours_worked,leave_type\nAlice,01/02/2026,8.0,\nBob,2026-01-02,30.0,\n",
    "blank_only_header.csv": "employee,date,hours_worked,leave_type\n",
    "trailing_spaces.csv": "employee,date,hours_worked,leave_type\n Alice ,2026-01-03,8.0,\n Alice ,2026-01-04,8.0,\n",
    "mixed_names.csv": "employee,date,hours_worked,leave_type\nalice,2026-01-02,8.0,\nAlice,2026-01-03,8.0,\nALICE,2026-01-04,8.0,\n",
    "text_hours.csv": "employee,date,hours_worked,leave_type\nBob,2026-01-02,8h,\nCarol,2026-01-03,eight,\n",
    "negative_hours.csv": "employee,date,hours_worked,leave_type\nDave,2026-01-04,-2,\nEve,2026-01-05,0.0,\n",
    "excessive_hours.csv": "employee,date,hours_worked,leave_type\nFrank,2026-01-06,30,\nGrace,2026-01-07,25,\n",
    "unknown_leave.csv": "employee,date,hours_worked,leave_type\nHenry,2026-01-08,8.0,bereavement\nIvy,2026-01-09,8.0,plenary\n",
    "non_numeric_hours.csv": "employee,date,hours_worked,leave_type\nJack,2026-01-10,14.5,sick\n",
    "utf8_bom.csv": "Unicode BOM\nemployee,date,hours_worked,leave_type\nHenry,2026-01-08,8.0,\nJack,2026-01-09,8.0,\n",
    "duplicate_header.csv": "employee,date,hours_worked,leave_type\nKate,2026-01-11,8.0,\nemployee,date,hours_worked,leave_type\nFrank,2026-01-12,8.0,\n",
}

for fname, content in cases.items():
    path = os.path.join(cases_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Created " + path)