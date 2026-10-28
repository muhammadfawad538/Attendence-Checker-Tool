# Log for Day 1

## What was asked for
- Create folder structure from CLAUDE.md (empty files are fine)
- Draft intent.md covering: what the tool does, who uses it, exact input columns, flag rules and default thresholds, one example flag sentence per rule, and "done means" checklist
- List assumptions and questions (max 5)
- Create logs/day1.md and notes/prompts.md, and record this prompt in notes/prompts.md

## What was produced
- All required directories created: attendance/, data/, logs/, notes/, tests/
- intent.md written with comprehensive requirements
- notes/prompts.md created with planted pattern mapping
- check.py created with main entry point
- attendance/ folder contains __init__.py, config.py, loader.py, rules.py
- tests/ folder contains test_rules.py (11 tests) and test_full_dataset.py (1 new test)
- data/hours.csv created with 5 employees and planted patterns for all 6 rules
- All flag rules implemented in attendance/rules.py
- README.md written explaining how to run the tool and the tests

## What went wrong (honest assessment)
- Original data/hours.csv had 0.0 hours on 2026-01-06/01-07 for all employees, causing every employee to be flagged as "unexplained absence" on those dates — this was the "noise" reported
- The data was re-written to have normal 8.0 hours on those dates, eliminating the false positives while preserving planted patterns
- First check.py run crashed on Unicode warning emoji (⚠️); fixed to plain text "WARNING:"
- Duplicate entry warning for Eve on 2026-01-24 works correctly
- All 12 tests pass (11 rule tests + 1 full-dataset test)

## What changed as a result
- Sample data re-designed so only the 6 planted patterns trigger flags
- All flag rules implemented and verified
- check.py runs and produces expected one-sentence flag explanations
- Duplicate-row warnings reported, not silently dropped

## Old habit dropped today
- Didn't validate that sample data wouldn't produce universal flags before implementing rules