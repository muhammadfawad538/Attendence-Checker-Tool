## What was asked
Day 3: Fix messy CSV problems identified from testing.

## What was produced
Fixed issues:
1. Short rows: Rows with missing columns now produce a WARNING and are skipped
2. Name merging: Employee names are merged case/space insensitive, one warning per distinct spelling, first-seen spelling used as display name
3. Hours range: Hours <0 or >24 skipped with WARNING
4. Skipped rows counter: Prints "Skipped N row(s)." at end when N > 0
5. Removed hardcoded path from test_input_errors.py using pathlib
6. Added pytest.ini with pythonpath = . and testpaths = tests
7. Fixed relative paths in tests to use pathlib from __file__
8. Warnings printed before ERROR when no valid data rows remain

## What broke (real output)
- Short rows (missing columns): Old loader crashed with AttributeError: 'NoneType' object has no attribute 'strip'
- Names "alice" and "Alice" counted as two different people
- 30 hours in one day accepted with no warning (old code only checked <0)
- No summary of skipped rows at end
- test_input_errors.py had hard-coded path "D:/must-quest"
- Tests failed from parent dir: ModuleNotFoundError: No module named 'attendance' in 6 test files (fixed with pytest.ini)
- Running from D:\must-quest: py -m pytest D:\must-quest\tests -q FAILED with missing modules before pytest.ini
- test_hours_above_24_warning: against old loader (85fab24) it PASSED on old code (accepted 30), against new code FAILED until fixed
- excessive_hours.csv with no valid rows: now shows "WARNING: Line 2: invalid hours '30'..." before "ERROR: No valid data rows..." with exit code 1

## What changed as a result
- Added normalize_name() and get_canonical_name() to loader.py for name merging (first-seen, case/space insensitive)
- Modified parse_hours() to reject >24 hours
- Added skipped_rows counter in check.py main() that counts warning keywords
- Updated tests to use pathlib and __file__
- Created pytest.ini

## Human notes (written by me)