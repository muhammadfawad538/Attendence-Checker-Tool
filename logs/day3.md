What was asked
Day 3 setup: explore messy CSV handling, plan Day 3 improvements.

What was produced
- Created logs/day3.md
- Created tests/data/hours_messy.csv with comment line listing cases:
  # Line 3: blank line
  # Line 4: Mixed date format (DD/MM/YYYY)
  # Line 5: Extra spaces in name, mixed casing
  # Line 6: Hours as text "8h"
  # Line 7: Negative hours (-2)
  # Line 8: Excessive hours (30)
  # Line 9: Unknown leave_type "bereavement"
  # Line 10: Non-numeric hours "eight"
  # Line 11: Trailing spaces
  # Line 12: Multiple spaces between fields

What broke (real output)
```
Exit code 1
=== Messy CSV Output ===
Traceback (most recent call last):
  File "D:\must-quest\check.py", line 73, in <module>
    main(csv_path)
    ~~~~^^^^^^^^^^
  File "D:\must-quest\check.py", line 26, in main
    records, warnings = load_csv(csv_path)
                        ~~~~~~~~^^^^^^^^^^
  File "D:\must-quest\attendance\loader.py", line 75, in load_csv
    lt_str = row.get("leave_type", "").strip()
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'strip'
```

Case-by-case analysis (from csv.DictReader output):
- Line 2 (Alice, 2026-01-01, 8.0): VALID - would parse fine
- Line 3 (blank): CRASH - leave_type is None, .strip() fails on None
- Line 4 (Alice, 01/02/2026, 8.0): Would WARN - invalid date format (not ISO)
- Line 5 (  alice  , 2026-01-03, 8.0): Would VALIDATE - spaces stripped, lowercase name different employee
- Line 6 (Bob, 2026-01-02, 8h): Would WARN - invalid hours format (not numeric)
- Line 7 (Carol, 2026-01-03, -2): Would WARN - negative hours rejected
- Line 8 (Dave, 2026-01-04, 30): Would VALIDATE - 30h is non-negative float
- Line 9 (Eve, 2026-01-05, 8.0, bereavement): Would WARN - unknown leave_type
- Line 10 (Frank, 2026-01-06, eight): Would WARN - non-numeric hours
- Line 11 (Grace, 2026-01-07, 8.0 ): Would VALIDATE - trailing space stripped
- Line 12 (Henry ,  2026-01-08 ,  8.0 ): Would VALIDATE - spaces stripped

What changed as a result
- Need to fix loader.py: handle None values from csv.DictReader (blank rows return None for fields)
- Should add null-check before .strip() or use default "" in .get()
- Will implement fix after user confirmation

## Human notes (written by me)