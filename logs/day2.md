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

## IMPLEMENTATION (Step 2)

### Change 1: Weekend work - separate FLAG, exclude from overwork
**Test written first:** `tests/test_rules.py::test_weekend_work_flagged`, `test_weekend_work_not_in_overwork`, `test_weekend_work_no_weekends`
- Test failure output: `ImportError: cannot import name 'check_weekend_work'`
- Fix: Added `is_weekend()` function, modified `check_overwork()` to filter out weekends, added `check_weekend_work()` function
- Test pass output: All 3 weekend tests PASSED
- Updated tests for overwork to use working days only (Thu-Fri-Mon-Tue instead of Thu-Fri-Sat-Sun)
- Modified `test_flag_messages.py` with exact message test for weekend work
- Updated `test_full_dataset.py` and `test_noisy_dataset.py` to include weekend work flags
- **Real output from check.py:**
```
FLAG: Alice: worked 4 weekend day(s): 8h on 2026-01-03, 8h on 2026-01-04, 12h on 2026-01-10, 12h on 2026-01-11.
```
- Commit: `2ca9fa6`

### Change 2: Part-time staff support - configurable expected hours per employee
**Test written first:** `test_part_time_staff_not_flagged_for_short_hours`, `test_part_time_staff_flagged_for_very_short_hours`, `test_full_time_staff_flagged_for_under_4_hours`, `test_get_expected_hours`
- Test failure output: `ImportError: cannot import name 'get_expected_hours'`
- Fix: Added `EXPECTED_HOURS` dict to `config.py`, added `get_expected_hours()` function to `rules.py`, modified `check_short_or_late()` to use per-employee threshold (half of expected hours)
- Test pass output: All 4 part-time tests PASSED
- **Real output from check.py:** Same as before (no part-timers in sample data)
- Commit: `0f35f84`

### Change 3: Duplicate rows - keep first, emit WARNING with both hours
**Test written first:** `test_duplicate_row_keeps_first_emits_warning`
- Test failure output: `assert '8.0' in "Line 3: duplicate entry for employee='Eve', date='2026-01-24'"` - warning didn't include hours
- Fix: Added `seen_first` dict to track first occurrence, updated warning message to include both hours
- Test pass output: Test PASSED
- **Real output from check.py:**
```
WARNING: Line 141: duplicate entry for employee='Eve', date='2026-01-24' (kept first row with '8.0' hours, dropped duplicate with '0.0' hours)
```
- Commit: `82f7334`

### Change 4: Fix empty CSV and missing columns - print clear error/warning, exit cleanly
**Test written first:** `test_empty_csv`, `test_missing_hours_column` (added to existing `test_missing_file.py`)
- Test failure output: Tests didn't exist yet
- Fix: Created test CSVs in `tests/data/`, updated test paths, verified existing behavior already correct (no crash, clear messages)
- Test pass output: All 3 tests PASSED
- **Real output from check.py:**
```
# Empty CSV:
Analyzing 0 records...
Done. Found 0 flag(s).
Exit code: 0

# Missing hours_worked:
WARNING: Missing columns: {'hours_worked'}
Analyzing 0 records...
Done. Found 0 flag(s).
Exit code: 0

# Missing file:
File not found: /path/to/nonexistent.csv
Exit code: 1
```
- Commit: `8c14356`

All 33 tests pass. `py -m pytest -v` output:
```
============================= 33 passed in 0.61s ==============================
```

### Corrections after implementation
**Decision B - Fix sample data (committed separately):**
- Removed all Sat/Sun rows from data/hours.csv (weekends removed from original employees)
- Moved Alice's overwork to 4 weekdays: 2026-01-08, 09, 12, 13 (Thu-Fri-Mon-Tue) with 12h each
- Added Grace employee with weekend work on 2026-01-17/18 (Sat-Sun) - 2 weekend days
- Added duplicate row for Eve on 2026-01-24 (8.0h then 0.0h) to preserve duplicate warning test
- Eve kept as working 8h on 2026-01-24 (Sat) - triggers weekend flag
- Frank kept as working 8h on 2026-01-31 (Sat) - triggers weekend flag
- Result: Alice now gets OVERWORK flag (not weekend), Bob/Carol/Dave get only their original planted flags, Eve/Frank get planted flags + weekend flags, Grace gets weekend flag

**Decision C - Restore test_full_dataset.py:**
- Updated test to expect Alice to have overwork flag (not weekend)
- Updated to expect Bob/Carol/Dave to have no weekend flags (only their original planted pattern)
- Updated to expect Eve/Frank to have planted flag + weekend flag
- Added Grace expectation (weekend work flag)
- Restored duplicate warning assertion for Eve on 2026-01-24
- Test now passes with corrected data

**Tests after corrections:**
```
============================= 33 passed in 0.62s ==============================
```

**check.py on corrected data:**
```
WARNING: Line 102: duplicate entry for employee='Eve', date='2026-01-24' (kept first row with '8.0' hours, dropped duplicate with '0.0' hours)

Analyzing 140 records...
FLAG: Alice: worked 11+ hours on 4 days in the 7-day window ending 2026-01-13.
FLAG: Bob: worked under 4 hours for 3 consecutive working days from 2026-01-12 to 2026-01-14.
FLAG: Carol: took annual leave on 5 Mondays or Fridays in the 8 weeks ending 2026-02-16.
FLAG: Dave: took annual leave on 2026-01-19, the day before public holiday 2026-01-20.
FLAG: Eve: logged 6.5 hours on 2026-01-19 but that day is marked as sick leave.
FLAG: Eve: worked 8 hours on weekend day 2026-01-24.
FLAG: Frank: has no hours and no leave recorded for working day 2026-01-28.
FLAG: Frank: worked 8 hours on weekend day 2026-01-31.
FLAG: Grace: worked 2 weekend day(s): 8h on 2026-01-17, 8h on 2026-01-18.

Done. Found 9 flag(s).
```

## Human notes (written by me)

