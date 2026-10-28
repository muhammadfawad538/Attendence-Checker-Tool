# CLAUDE.md: Attendance Checker (Option B)

Claude Code reads this file at the start of every session. Follow it. If a rule here conflicts with a one-off request, ask me before breaking it.

## Project

A small Python command-line tool that reads a CSV of work hours and leave, flags unusual attendance patterns, and explains each flag in one sentence.

Run: `python check.py data/hours.csv`

Input columns: `employee, date, hours_worked, leave_type`
(`leave_type` is empty when the person worked a normal day. Values: `annual`, `sick`, `public_holiday`, or empty.)

## This is a 5-day AI-first assessment

What is judged: how much my way of working changes, not how much I already know. So:

- I direct and review. You write the code. Do not ask me to hand-write code.
- Never build before `intent.md` exists and I have approved it.
- Show your plan in a few lines before large changes, then do it.
- Everything must be checkable: run the code, run the tests, show me the output. Never say "this should work" without running it.

## Working rules

1. **Tests first.** Write a failing test for each rule, then the code. Use `pytest`.
2. **Small functions.** One rule = one function. No function over ~30 lines. Clear names, type hints, short docstrings.
3. **Standard library plus pytest only**, unless I approve a dependency.
4. **Every flag has exactly one plain-English sentence** that names the person, the pattern, and the evidence (dates or counts). No vague text like "unusual activity".
5. **Never silently fix or drop data.** Bad rows (bad date, negative hours, missing fields, duplicates) must be reported as data-quality warnings, not hidden. The tool must not crash on messy input.
6. **Deterministic output.** Same input gives the same output, sorted by employee then date.
7. **Rules are configurable** in one place (e.g. `config.py`): thresholds such as overwork hours, streak length, weekday-leave count.
8. **No invented facts.** If you are unsure of a rule's meaning, ask me.

## Flag rules (starting set; I will tune them)

- Overwork: 11+ hours on N or more days in a rolling window
- Short or late pattern: under 4 hours on N consecutive working days
- Leave pattern: leave on Monday or Friday repeatedly
- Bridge leave: leave the day before or after a public holiday
- Hours on leave: hours logged on a day marked as leave (data error)
- Unexplained absence: a working day with no hours and no leave record

## Folder layout

```
check.py            entry point
attendance/         rules, loader, config
data/               sample CSVs (clean + messy)
tests/              pytest tests
intent.md           written BEFORE code
directive.md        final standing instructions (refined daily)
README.md           how to run
logs/day1.md ... day5.md
notes/prompts.md    my prompts and your mistakes (see below)
```

## Logging (this is graded, so keep it up)

At the end of every session, append to `logs/dayN.md`:
- What I asked for
- What you produced
- What was wrong or broke (be specific, with the actual error or wrong output)
- What changed as a result
- Which old habit I dropped today

Also keep `notes/prompts.md`: each important prompt, what you got back, and every mistake I caught. Never tidy a failure into a success. Record what really happened.

## Raise the Load (Day 4)

Deliberately make the task harder, then report honestly what broke:
- Messy CSVs: missing columns, bad dates, mixed date formats, duplicates, blank rows, non-numeric hours, extra whitespace and casing
- Large file: 10x to 100x more rows, and note the runtime
- Stricter rules and more edge cases (overlapping leave, weekends, part-time staff)

Record failures in the log before fixing them.

## Honesty rules

- If a test fails, say so. Do not weaken the test to make it pass without telling me.
- If you made an assumption, list it.
- If something is unfinished or only partly working, say so plainly.
- Never report a task as done without pasted command output that proves it.

## Done means

- `pytest` passes
- `python check.py data/hours.csv` runs and prints flags with one-sentence explanations
- Messy input produces warnings, not crashes
- README explains how to run the tool and the tests
- Logs exist for all 5 days
