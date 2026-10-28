# Intent: Attendance Checker (Option B)

## What the Tool Does
A Python command-line tool that reads a CSV of work hours and leave records, applies configurable flag rules to detect unusual attendance patterns, and outputs one-sentence plain-English explanations for each flag found.

## Who Uses It
An HR professional or team lead reviewing employee attendance data to identify patterns that may need follow-up (overwork, unexplained absences, leave abuse patterns, data quality issues).

## Input Columns
The tool expects a CSV file with these exact columns:
- `employee` (string) — employee identifier/name
- `date` (string, ISO format YYYY-MM-DD) — the work date
- `hours_worked` (float) — hours logged for that day
- `leave_type` (string) — one of: `annual`, `sick`, `public_holiday`, or empty string for normal work day

## Flag Rules and Default Thresholds

| Rule | Description | Default Threshold |
|------|-------------|-------------------|
| **Overwork** | Employee worked 11+ hours on N or more days in a rolling window | 11 hours, 3 days in 7-day window |
| **Short or late pattern** | Employee worked under 4 hours on N consecutive working days | < 4 hours, 3 consecutive days |
| **Leave pattern** | Leave taken on Monday or Friday repeatedly | 3+ Monday/Friday leaves in 8 weeks |
| **Bridge leave** | Leave taken the day before or after a public holiday | Any occurrence |
| **Hours on leave** | Hours logged on a day marked as leave (data error) | Any occurrence |
| **Unexplained absence** | Working day with no hours and no leave record | Any occurrence |

## Example Flag Sentences (One Per Rule)

1. **Overwork**: "Alice worked 11+ hours on 4 days in the 7-day window ending 2026-01-15."
2. **Short or late pattern**: "Bob worked under 4 hours for 3 consecutive working days from 2026-02-10 to 2026-02-12."
3. **Leave pattern**: "Carol took annual leave on 5 Mondays or Fridays in the 8 weeks ending 2026-03-01."
4. **Bridge leave**: "Dave took annual leave on 2026-04-18, the day before public holiday 2026-04-19."
5. **Hours on leave**: "Eve logged 6.5 hours on 2026-05-20 but that day is marked as sick leave."
6. **Unexplained absence**: "Frank has no hours and no leave recorded for working day 2026-06-05."

## "Done Means" Checklist
- [ ] `pytest` passes (all tests green)
- [ ] `python check.py data/hours.csv` runs and prints flags with one-sentence explanations
- [ ] Messy input produces warnings, not crashes (missing columns, bad dates, mixed formats, duplicates, blank rows, non-numeric hours, extra whitespace/casing)
- [ ] README explains how to run the tool and the tests
- [ ] Logs exist for all 5 days (logs/day1.md through logs/day5.md)
- [ ] Configuration in `attendance/config.py` with all thresholds adjustable
- [ ] Each rule implemented as a separate function (~30 lines max)
- [ ] Deterministic output sorted by employee then date
- [ ] Data quality warnings reported for bad rows (not silently dropped)

## Assumptions
1. Weekends (Saturday/Sunday) are not considered "working days" for the short/late pattern and unexplained absence rules
2. Public holidays are identified by `leave_type == "public_holiday"` in the data
3. The rolling window for overwork is calendar days (not working days)
4. The tool processes the entire CSV each run; no incremental/stateful processing
5. Employee names are used as-is for grouping (no normalization of case/whitespace in the config, but the loader may strip whitespace)
6. A "working day" for unexplained absence means any day that is not a weekend and not a public holiday

## Questions (Max 5)

1. **Weekend definition**: Should Saturday/Sunday be hardcoded as non-working, or should the config allow custom weekend days (e.g., Fri/Sat for some regions)?

2. **Public holiday list**: Are public holidays only identified via `leave_type == "public_holiday"` rows in the CSV, or should the tool also accept a separate calendar/config file of known holidays?

3. **Part-time employees**: Should thresholds (like 11 hours for overwork, 4 hours for short days) be adjustable per employee, or are global defaults sufficient for v1?

4. **Output format**: Should the tool print to stdout only, or also support JSON/CSV output for integration with other systems?

5. **Rolling window boundaries**: For the overwork rule, should the "7-day window" be strictly trailing (past 7 days including today) or centered, and should it slide day-by-day or be evaluated per employee per week?