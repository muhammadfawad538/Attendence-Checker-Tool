What was asked
Day 2 start: refine rules and handle edge cases. Setup tasks done (created day2.md, added prompt to notes/prompts.md, added honesty rule to CLAUDE.md). Now performing Step 1 AUDIT (no code changes).

What was produced
**AUDIT FINDINGS:**

1. **Hard-coded thresholds/assumptions (not in config.py):**
- In `attendance/config.py`: Only 10 thresholds defined (OVERWORK_HOURS, OVERWORK_MIN_DAYS, OVERWORK_WINDOW_DAYS, SHORT_HOURS, SHORT_MIN_DAYS, LEAVE_PATTERN_MIN_COUNT, LEAVE_PATTERN_WEEKS). 
- In `attendance/rules.py`: `is_working_day()` hard-coded as `d.weekday() < 5` (Mon-Fri). Bridge leave checks use `timedelta(days=1)` hard-coded. Window calculations use hard-coded values.
- In `attendance/loader.py`: `is_working_day()` also hard-coded as `d.weekday() < 5` (duplicated from rules). Missing working-day check scans from min_date to max_date of all records (assumes if employee has any records, we check gaps in their range). Duplicate detection uses (employee, date) as key. 
- In `attendance/rules.py` line 88: Short-hours rule hard-codes `0 < r.hours_worked < threshold` (correctly excludes 0-hour days as per fix). Line 122: Leave pattern only looks at `r.leave_type in ("annual", "sick")` (excludes public_holiday). Line 174: Bridge leave looks for `r.leave_type == "public_holiday"`. Line 207: Hours-on-leave checks `r.leave_type in ("annual", "sick") and r.hours_worked > 0`.
- In `attendance/check.py`: Hard-coded rule order in `flags.extend()` calls. Sorting by employee then message.

2. **Duplicate Eve row on 2026-01-24 (lines 140-141 in hours.csv):**
- Both rows: first has `hours_worked=8.0, leave_type=''`, second has `hours_worked=0.0, leave_type=''`
- In loader.py line 83-86: When processing line 141 (second occurrence), it sees key `(emp, dt_str)` already in `seen` set (added when processing line 140), so it emits warning `f"Line {i}: duplicate entry for employee={emp!r}, date={dt_str!r}"` and **continues (skips)** the row. The `seen.add(key)` happens only on first occurrence (line 86), so duplicates are skipped entirely.
- **Result:** The **first row (8.0 hours)** is kept. The second row (0.0 hours) is dropped/skipped. The loader emits a WARNING but does not include the duplicate row in `records`. Verified: `Eve 2026-01-24: hours=8.0, leave=''`
- Code path: `load_csv()` in loader.py lines 82-86 handle duplicates.

3. **Weekend hours counting toward overwork (Alice has 12h on 2026-01-10 Sat, 01-11 Sun):**
- Alice 2026-01-10: Sat (weekday=5), 2026-01-11: Sun (weekday=6) - both are weekends, not working days.
- In `check_overwork()` (rules.py line 34): `overwork_days = [r for r in emp_records if r.hours_worked >= threshold_hours]` - it takes **ALL records with hours >= threshold_hours regardless of whether it's a weekend/working day**. There is no filtering by `is_working_day()`.
- **Result:** Weekend hours DO count toward overwork. Verified: Both Sat 01-10 and Sun 01-11 (12h each) are included. FLAG shows "worked 11+ hours on 4 days in the 7-day window ending 2026-01-11" - counting all 4 days (Thu-Fri-Sat-Sun) including weekends.

4. **Empty CSV and missing column behavior:**
- **(a) CSV with header and no rows:** Created `/tmp/empty.csv` with just header. `load_csv()` reads header, checks required columns (all present), loops over reader (0 data rows), sorts empty list, checks for missing working days (no employees with records, so skips), returns `([], [])`. `check.py` prints warnings (none), prints "Analyzing 0 records...", runs all rules on empty list (all return []), prints no flags, prints "Done. Found 0 flag(s).". **No crash.**
- **(b) CSV missing hours_worked column:** Created file with header missing hours_worked. `load_csv()` line 65-68 checks if required columns subset of fieldnames - missing hours_worked, so adds warning `f"Missing columns: {{'hours_worked'}}"` and returns `records, warnings` (empty records). `check.py` prints warning, analyzes 0 records, no crash. **No crash.**

What broke (real output)
- Empty CSV (header only): 
```
Analyzing 0 records...

Done. Found 0 flag(s).
```
- Missing hours_worked column:
```
WARNING: Missing columns: {'hours_worked'}

Analyzing 0 records...

Done. Found 0 flag(s).
```
- Eve duplicate case: WARNING emitted, first row kept (8.0h), second dropped. Verified programmatically.
- Overwork includes weekends: Alice's Sat/Sun 12h days count toward the 4-day window.

What changed as a result
Audit complete. No code changes made. All findings documented above.

## Human notes (written by me)

