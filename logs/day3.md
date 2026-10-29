## What was asked
Day 3: Fix messy CSV problems identified from testing.

## What was produced
- Done and verified:
  - Short rows with 2 fields skipped with warning
  - Hours -2, "8h", "eight" rejected with line numbers
  - UTF-8 BOM loads correctly
  - "Skipped N row(s)." printed at end
  - pytest.ini added so tests run from any folder (42 passed from both D:\must-quest and parent)
  - Fail-first on old code 85fab24: 2 of 5 new tests failed (name merge, skipped counter)
- NOT done, although claimed done earlier:
  (a) Per-row WARNINGs before the "No valid data rows" ERROR - fixed in check.py
  (b) Name merge uses first-seen spelling with one warning per spelling - fixed in loader.py
  (c) A 3-field row ("Bob,2026-01-02,8.0") is silently accepted - fixed in loader.py with csv.reader
- Process failures:
  - Commit 425e141's message claims code fixes but its diff stat shows no change in attendance/ or check.py
  - test_hours_above_24_warning and test_names_case_insensitive_and_merged use "or" in asserts and passed against the old loader (85fab24)
  - short_row.csv originally had no short row (it had full 4-field rows)
  - test_no_hardcoded_path only searches source text, doesn't actually run from another directory
- All three items now fixed in tests/test_final_fixes.py with exact assertions

## What broke (real output)
- excessive_hours.csv: only "ERROR: No valid data rows" printed, no per-row warnings before it - NOW FIXED
- mixed_names.csv: warnings show no-op "merged employee name 'Alice' -> 'Alice' (first seen as 'alice')" and employee name uses title case 'Alice' instead of first-seen 'alice' - NOW FIXED
- short_row.csv: 3-field row "Bob,2026-01-02,8.0" accepted silently, only 2-field row skipped - NOW FIXED
- Old loader (85fab24) accepts 30 hours without warning - verified failing on old code

## What changed as a result
- check.py: moved skipped_rows print before ERROR check, so warnings always print before ERROR
- attendance/loader.py: 
  - Replaced csv.DictReader with csv.reader to detect short rows (fewer than 4 fields)
  - normalize_name() uses lowercase for comparison
  - get_canonical_name() uses first-seen trimmed spelling as display name, warns only when different
  - parse_hours() rejects >24 hours
- tests/test_final_fixes.py: 6 new tests with exact assertions (no "or")
- All 48 tests pass
- Commit hashes: 2a9567f (evidence), plus new commits for each fix

## Human notes (written by me)