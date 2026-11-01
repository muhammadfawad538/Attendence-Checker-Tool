# What I unlearned

## The habit I started with
I started the week trusting what the AI told me. If it said "all done" and the tests were green, I believed it.

## What broke that belief
- **Day 1:** Claude Code said everything was done and 11 tests passed. When I ran the tool myself it printed 27 flags where I expected 6. Two fixes it reported as done had not been done, and it had edited the sample data to hide a rule bug.
- **Day 1:** I had not started git, so I could not see what it changed. I started committing before and after every session.
- **Day 2:** it bent the tests to match the output a second time (accepting 11 flags, then 9). I only caught it by counting flags and reading `git diff`.
- **Day 3:** a commit message claimed code fixes, but `git diff --stat` showed no code changed. Two tests used `or` in their asserts and passed against the old buggy code. A file named `short_row.csv` did not contain a short row.
- **Day 4:** the log said the JSON output was fixed. My own check showed it still printed a stray line and failed to parse. The AI also wrote "None observed" and "all requirements met" in my notes.

## What I do now
- I run the commands myself and read the output, and I do not accept a summary.
- I read `git diff --stat` before accepting "done".
- I run the old code against the new tests to see whether a test can actually fail (on Day 3, 2 of 5 new tests failed against the old code, which proved those fixes).
- I ask for exact assertions, and I count anything without pasted output as not done.
- I write my own notes, because the AI shades the story.

## Raising the load
At about 2 million rows the tool took about 23 seconds and about 1.2 GB of memory, because it loads the whole file at once. I did not make it stream. My target was 5 seconds, and the test uses 30 seconds, so I missed my own target.

## What is still not fixed
- `--format json` still prints an "Analyzing..." line before the JSON, so it does not parse as pure JSON.
- The full test suite takes about a minute because of the 100x tests.
- The 5-second goal at 100x was not met.

## One sentence
I stopped asking "does it say it works?" and started asking "what does the output show?"
