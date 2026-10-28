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
- tests/ folder contains test_rules.py with 11 tests, all passing
- data/hours.csv created with 5 employees and planted patterns for all 6 rules
- All flag rules implemented in attendance/rules.py
- README.md written explaining how to run the tool and the tests

## What was wrong or broke
- Initial attempts to write files were interrupted (session ended before completion)
- First run of check.py crashed due to Unicode encoding error in warning messages
- Fixed by replacing ⚠️ with "WARNING:" to avoid encoding issues
- Duplicate entry warning correctly caught instead of crashing

## What changed as a result
- All folder structure created and files written successfully
- First implementation of flag rules completed and tested
- check.py now runs without crashing and produces expected output
- All tests pass (11 passed)
- All 6 flag rules working correctly

## Old habit dropped today
- Didn't create files one at a time without checking the overall structure first

## Next steps for subsequent days
- Day 2: Refine rules based on output, handle edge cases
- Day 3: Add messy CSV handling, improve warnings
- Day 4: Increase data size, test runtime
- Day 5: Final review and polish