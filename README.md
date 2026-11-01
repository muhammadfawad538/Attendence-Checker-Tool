Attendance Checker

A small Python command-line tool. It reads a CSV of work hours and leave, flags unusual attendance patterns, and explains each flag in one sentence. Built over 5 days working AI-first with Claude Code (see logs/, intent.md and directive.md).

Requirements
Python 3.9 or newer
pytest, for the tests: py -m pip install pytest
No other dependencies

On Windows use py. On macOS or Linux use python3.

Run the tool
py check.py data/hours.csv
py check.py data/hours.csv --strict
py check.py data/hours.csv --format json

Expected result on the sample file: 7 flags (one per employee), plus one data-quality warning for a deliberate duplicate row (Eve, 2026-01-22).

Options
--strict: exit with code 1 if any data-quality warning exists. On the sample file this exits 1, because of the deliberate duplicate row.
--format text|json: output format (default text).
Input format

A CSV with these exact columns:

column	meaning
employee	name. Matching ignores spaces and upper/lower case, and the first spelling seen is used
date	YYYY-MM-DD
hours_worked	number from 0 to 24
leave_type	annual, sick, public_holiday, or empty
What gets flagged
Overwork: 11+ hours on several days inside a rolling 7-day window (weekends are not counted here).
Short days: fewer than half of the person's expected hours (default 8, so under 4), on consecutive working days. A 0-hour day counts as an absence, not a short day.
Leave pattern: repeated leave on Mondays or Fridays over 8 weeks.
Bridge leave: leave the day before or after a public holiday.
Hours on leave: hours logged on a day marked as leave.
Unexplained absence: a working day with 0 hours and no leave.
Weekend work: hours logged on a Saturday or Sunday.

Exact thresholds, and the per-employee expected hours for part-time staff, are in attendance/config.py.

Messy data

Bad rows never crash the tool. Each one produces a WARNING with its line number, the row is skipped, and the run ends with Skipped N row(s).. Handled cases include missing or short rows, bad dates, hours outside 0 to 24, text hours, unknown leave types, duplicate rows (the first row is kept), names that differ only in case or spacing, and a UTF-8 BOM. A missing file, an empty file, or a missing column prints one ERROR line and exits with code 1.

Run the tests
py -m pytest -q

This also works from another folder (pytest.ini sets the path). The suite takes about a minute because it includes 100x-size performance tests.

Large-file testing (Day 4)

tools/make_big_csv.py generates big test files (they are not committed) and tools/measure.py measures time and memory. Measured at about 2 million rows: roughly 23 seconds and about 1.2 GB of memory, because the whole file is loaded at once.

Known problems (not fixed)
--format json prints an Analyzing ... records line before the JSON, so the output is not pure JSON.
Skipped 0 row(s). can print when no row was skipped.
The warning for a row with too few columns says "missing required field(s)" instead of naming the column count.
The tool does not stream large files. The 5-second goal at 100x was not met (the test allows 30 seconds).
The test suite is slow because of the 100x tests.
Project files
intent.md: what the tool does and what "done" means (written before the code)
directive.md: the final standing instructions given to the AI
logs/day1.md to logs/day5.md: daily logs, including what failed
evidence/: saved command outputs from Day 3
unlearning_note.md: what I unlearned