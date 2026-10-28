# Attendance Checker - README.md

## Overview
The Attendance Checker is a Python command-line tool that analyzes employee attendance data to identify unusual patterns that may need follow-up. It reads a CSV file with employee work hours and leave records, applies configurable flag rules, and outputs one-sentence explanations for each flag found.

## Requirements
- Python 3.6+
- pytest (for running tests)

## Installation
```bash
# Clone or copy this repository
cd your/project/directory

# Install dependencies (none required - uses standard library)
```

## Usage
```bash
python check.py data/hours.csv
```

## Input Format
The CSV file must have these exact columns:
- `employee` (string) - employee identifier
- `date` (YYYY-MM-DD) - work date in ISO format
- `hours_worked` (float) - hours logged for that day
- `leave_type` (string) - one of: `annual`, `sick`, `public_holiday`, or empty string

## Flag Rules
The tool checks for these patterns:

1. **Overwork**: 11+ hours on 3+ days in a 7-day rolling window
2. **Short or late pattern**: < 4 hours on 3 consecutive working days
3. **Leave pattern**: 3+ annual/sick leaves on Mondays or Fridays in 8 weeks
4. **Bridge leave**: Leave taken the day before or after a public holiday
5. **Hours on leave**: Hours logged on a day marked as leave (data error)
6. **Unexplained absence**: Working day with no hours and no leave record

## Output
The tool prints warnings for data quality issues, then lists each flag with a one-sentence explanation:
```
FLAG: Alice: Alice has no hours and no leave recorded for working day 2026-01-06.
FLAG: Alice: Alice worked 11+ hours on 4 days in the 7-day window ending 2026-01-11.
```

## Configuration
Thresholds are configurable in `attendance/config.py`:
- `OVERWORK_HOURS`: 11.0 (default)
- `OVERWORK_MIN_DAYS`: 3 (default)
- `OVERWORK_WINDOW_DAYS`: 7 (default)
- `SHORT_HOURS`: 4.0 (default)
- `SHORT_MIN_DAYS`: 3 (default)

## Testing
```bash
pytest tests/ -v
```

## Logs
Daily logs are maintained in the `logs/` directory (day1.md through day5.md).

## Example Output
FLAG: Alice: Alice has no hours and no leave recorded for working day 2026-01-06.
FLAG: Alice: Alice has no hours and no leave recorded for working day 2026-01-07.
FLAG: Alice: Alice worked 11+ hours on 4 days in the 7-day window ending 2026-01-11.
FLAG: Bob: Bob has no hours and no leave recorded for working day 2026-01-06.
FLAG: Bob: Bob worked under 4 hours for 3 consecutive working days from 2026-01-06 to 2026-01-08.