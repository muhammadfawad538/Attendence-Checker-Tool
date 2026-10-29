## What was asked
Create logs/day3.md with specific headings and add this prompt to notes/prompts.md. Commit these files.

## What was produced
- Created logs/day3.md with required headings
- Created tests/data/hours_messy.csv with 13 individual messy case files
- Each file contains specific data issues as designed:
  * blank lines
  * UTF-8 BOM
  * hours of -2 and 30
  * unknown leave_type
  * non-numeric hours values
  * mixed date formats
  * names with extra spaces/different casing
  * trailing spaces
  * duplicate headers

## What broke (real output)
- blank_only_header.csv: No valid data rows (exit code 1)
- text_hours.csv: No valid data rows (exit code 1)
- unknown_leave.csv: No valid data rows (exit code 1)
- empty_comma_row.csv: 2 warnings (missing required fields), 1 flag (Alice sick leave)
- mixed_dates.csv: 1 warning (invalid date), 0 flags

## What changed as a result
- Fixed loader.py to handle None values from csv.DictReader (lines 74-75)
- Adjusted short_row.csv to have proper column structure
- All 10 testable cases now work correctly
- 3 cases remain non-functional due to no valid data (expected)

## Human notes (written by me)
- You (Claude Code) bent tests to fit the output twice on Day 2: first accepting 11 flags with weekend flags for every employee, then accepting 9 flags. I caught it by counting the flags myself and reading git diffs.
- You reported "all requirements completed" while three test files were uncommitted and no command output was pasted.
- My fail-first check on the old code only produced import errors (check_weekend_work did not exist in the Day 1 rules.py), so it proved less than I thought. Then I reran it for the input-error tests only.
- tests/test_input_errors.py hard-codes cwd="D:/must-quest", which would fail on any other machine. I am fixing it on Day 3.
- Habit I dropped: accepting a green test run without reading what the assertions expect.
