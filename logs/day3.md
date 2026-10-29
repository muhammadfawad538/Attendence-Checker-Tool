## What was asked
Day 3: Fix messy CSV problems identified from testing.

## What was produced
Fixed 4 issues:
1. Short rows: Rows with missing columns now produce a WARNING and are skipped
2. Name merging: Employee names are normalized (case/space insensitive) with WARNING when merged
3. Hours range: Hours <0 or >24 skipped with WARNING; hours 12-24 accepted with WARNING
4. Skipped rows counter: Prints "Skipped N row(s)." at end when N > 0
5. Removed hardcoded path from test_input_errors.py using pathlib

## What broke (real output)
- Short rows (missing columns): Old loader crashed with AttributeError: 'NoneType' object has no attribute 'strip'
- Names "alice" and "Alice" counted as two different people
- 30 hours in one day accepted with no warning
- No summary of skipped rows at end
- test_input_errors.py had hard-coded path "D:/must-quest"

## What changed as a result
- Added normalize_name() and get_canonical_name() to loader.py for name merging
- Modified parse_hours() to reject >24 hours, added validate_hours_range() for 12-24 warning
- Added skipped_rows counter in check.py main() that counts warning keywords
- Updated test_input_errors.py to use pathlib and __file__

## Human notes (written by me)