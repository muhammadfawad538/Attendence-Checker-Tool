## Human notes (written by me)

- You (Claude Code) bent tests to fit the output twice on Day 2: first accepting 11 flags with weekend flags for every employee, then accepting 9 flags. I caught it by counting the flags myself and reading git diffs.
- You reported "all requirements completed" while three test files were uncommitted and no command output was pasted.
- My fail-first check on the old code only produced import errors (check_weekend_work did not exist in the Day 1 rules.py), so it proved less than I thought. Then I reran it for the input-error tests only.
- tests/test_input_errors.py hard-codes cwd="D:/must-quest", which would fail on any other machine. I am fixing it on Day 3.
- Habit I dropped: accepting a green test run without reading what the assertions expect.