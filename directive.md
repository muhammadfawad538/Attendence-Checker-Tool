# directive.md: final standing instructions for Claude Code

This is the final version of the rules I give the AI (it grew out of CLAUDE.md over 5 days). Each rule exists because something went wrong without it.

## Project
Attendance checker (Option B). Reads a CSV of work hours and leave (`employee, date, hours_worked, leave_type`), flags unusual patterns, and explains each flag in one sentence.
Run: `py check.py data/hours.csv`. Test: `py -m pytest -q`.

## How we work
1. `intent.md` is written and approved before any code.
2. The AI writes the code. I direct and review.
3. Tests first. Write the failing test, paste the real FAIL output, fix, paste the real PASS output, one commit per fix.
4. Commit before and after every AI session so `git diff` shows exactly what changed.

## Rules learned the hard way
- **Evidence for every claim.** "Done" with no pasted command output counts as not done. (Day 1: two fixes were reported done and were not.)
- **Exact assertions only.** No `or` in asserts. A test must be able to fail. (Day 3: two tests passed against the old buggy code.)
- **Never change an existing test or sample data to make a result pass** without saying what it was, what it is now, and why. (Days 1 and 2: tests and data were bent to fit the output.)
- **Commit messages must describe only what the diff contains.** (Day 3: a commit message claimed code fixes that were not in the diff.)
- **Predictions are not results.** Never write "would warn" or "would pass" as a finding. Run it.
- **Never silently fix, pad or drop data.** Bad rows produce a WARNING with the line number, and the row is skipped.
- **Do not write my "Human notes" sections.** I write those.
- **Do not touch files I said not to touch.** If you did, say so in the log.
- **Report failures in the log before fixing them.** Do not tidy a failure into a success.

## Flag rules
Overwork (11+ hours on several days in a window), short days (0 < hours < expected/2 on consecutive working days), Monday/Friday leave pattern, leave next to a public holiday, hours logged on a leave day, unexplained absence (working day, 0 hours, no leave), weekend work. Thresholds live in `attendance/config.py`.

## Done means
`py -m pytest -q` passes, `py check.py data/hours.csv` prints the expected 7 flags, messy input produces warnings instead of crashes, and every known failure is written in the logs.
