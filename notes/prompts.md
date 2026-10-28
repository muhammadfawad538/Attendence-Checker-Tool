# Planted Patterns in data/hours.csv

## Rule-to-Employee Mapping

1. **Overwork** → Alice: 4 days with 12.0 hours (2026-01-08 to 2026-01-11)
2. **Short or late pattern** → Bob: 3 consecutive days with 3.0 hours (2026-01-08 to 2026-01-10)
3. **Leave pattern** → Carol: 5 annual leaves on Mondays/Fridays (2026-01-19, 2026-01-26, 2026-02-01, 2026-02-08, 2026-02-15)
4. **Bridge leave** → Dave: Leave on 2026-01-19 (day before public holiday 2026-01-20)
5. **Hours on leave** → Eve: 6.5 hours logged on 2026-01-19 marked as sick leave
6. **Unexplained absence** → Frank: 0.0 hours on 2026-01-28 with no leave record

## Notes on Data Design

- Each employee has exactly one planted pattern so flag rules can be verified independently.
- Carol's leave dates span Mondays and Sundays; the tool should flag at least 3 Monday/Friday leaves for the Leave pattern rule.
- Dave's 2026-01-20 is marked `public_holiday`; 2026-01-19 is the day before, triggering Bridge leave.
- Eve's 6.5 hours on sick leave should trigger "Hours on leave" before "Unexplained absence" would.
- Frank's 0.0-hour days with no leave_type should trigger "Unexplained absence".