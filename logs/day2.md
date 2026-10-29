## What was asked
Day 2: refine rules and handle edge cases with tests-first approach.

## What was produced
- Implemented weekend work rule as separate FLAG (excluded from overwork)
- Added part-time staff support via EXPECTED_HOURS config
- Fixed duplicate row handling to keep first and emit warning with both hours
- Fixed empty CSV and missing columns to print ERROR and exit 1

## What broke (real output)
- Weekend work initially crashed: ImportError: cannot import name 'check_weekend_work'
- Part-time staff initially crashed: ImportError: cannot import name 'get_expected_hours'
- Duplicate warning didn't include both hours values
- Empty CSV and missing columns printed WARNING and exited 0 (should be ERROR and exit 1)

## What changed as a result
- Added check_weekend_work function, is_weekend helper, modified check_overwork to filter weekends
- Added EXPECTED_HOURS dict and get_expected_hours function
- Added seen_first dict to track first occurrence hours for duplicate warnings
- Modified check.py to treat missing columns and empty CSV as ERROR with exit 1

## Human notes (written by me)
- Claude Code bent tests to fit the output twice on Day 2: first accepting 11 flags with weekend flags for every employee, then accepting 9 flags. I caught it by counting the flags myself and reading git diffs.
- Claude Code reported "all requirements completed" while three test files were uncommitted and no command output was pasted.
- My fail-first check on the old code only produced import errors (check_weekend_work did not exist in the Day 1 rules.py), so it proved less than I thought. Then I reran it for the input-error tests only.
- tests/test_input_errors.py hard-coded cwd="D:/must-quest", which would fail on any other machine. I fixed it on Day 3.
- Habit I dropped: accepting a green test run without reading what the assertions expect.
- Fail-first check on old code (8c14356): git checkout 8c14356 -- check.py attendance/loader.py ; py -m pytest tests/test_input_errors.py -q → 2 FAILED (exit code 0 instead of 1 for both empty CSV and missing columns). git checkout HEAD -- check.py attendance/loader.py ; py -m pytest -q → 42 passed.