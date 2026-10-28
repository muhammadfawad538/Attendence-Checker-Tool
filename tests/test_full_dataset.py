"""Full pipeline test on the sample dataset."""
from attendance.loader import load_csv
from attendance.rules import (
    check_overwork,
    check_short_or_late,
    check_leave_pattern,
    check_bridge_leave,
    check_hours_on_leave,
    check_unexplained_absence,
    check_weekend_work,
)


def test_full_dataset_expected_flags():
    """Run the whole pipeline on data/hours.csv and assert exact expected flags."""
    records, warnings = load_csv("data/hours.csv")

    # Collect all flags
    all_flags = []
    all_flags.extend(check_overwork(records))
    all_flags.extend(check_short_or_late(records))
    all_flags.extend(check_leave_pattern(records))
    all_flags.extend(check_bridge_leave(records))
    all_flags.extend(check_hours_on_leave(records))
    all_flags.extend(check_unexplained_absence(records))
    all_flags.extend(check_weekend_work(records))

    # Group by employee
    by_emp = {}
    for emp, msg in all_flags:
        by_emp.setdefault(emp, []).append(msg)

    # Assert exact expected flags per employee - each employee has exactly 1 flag
    # Alice: 1 overwork (4 working days with 12h+ in 7-day window ending 2026-01-13)
    assert "Alice" in by_emp
    alice_flags = by_emp["Alice"]
    overwork_flags = [f for f in alice_flags if "11+ hours" in f]
    assert len(overwork_flags) == 1, f"Alice should have 1 overwork flag, got {len(overwork_flags)}: {alice_flags}"
    assert "4 days" in overwork_flags[0]
    assert "2026-01-13" in overwork_flags[0]
    weekend_flags = [f for f in alice_flags if "weekend" in f.lower()]
    assert len(weekend_flags) == 0, f"Alice should NOT have weekend work flag: {alice_flags}"

    # Bob: 1 short-hours (no weekend work)
    assert "Bob" in by_emp
    bob_flags = by_emp["Bob"]
    short_flags = [f for f in bob_flags if "under 4 hours" in f]
    weekend_flags = [f for f in bob_flags if "weekend" in f.lower()]
    assert len(short_flags) == 1, f"Bob should have 1 short-hours flag, got {len(short_flags)}: {bob_flags}"
    assert len(weekend_flags) == 0, f"Bob should NOT have weekend work flag: {bob_flags}"
    assert "consecutive working days" in short_flags[0]

    # Carol: 1 leave-pattern (Mon/Fri) (no weekend work)
    assert "Carol" in by_emp
    carol_flags = by_emp["Carol"]
    leave_flags = [f for f in carol_flags if "Mondays or Fridays" in f]
    weekend_flags = [f for f in carol_flags if "weekend" in f.lower()]
    assert len(leave_flags) == 1, f"Carol should have 1 leave-pattern flag, got {len(leave_flags)}: {carol_flags}"
    assert len(weekend_flags) == 0, f"Carol should NOT have weekend work flag: {carol_flags}"
    assert "5" in leave_flags[0] or "annual" in leave_flags[0]

    # Dave: 1 bridge-leave (no weekend work)
    assert "Dave" in by_emp
    dave_flags = by_emp["Dave"]
    bridge_flags = [f for f in dave_flags if "public holiday" in f]
    weekend_flags = [f for f in dave_flags if "weekend" in f.lower()]
    assert len(bridge_flags) == 1, f"Dave should have 1 bridge-leave flag, got {len(bridge_flags)}: {dave_flags}"
    assert len(weekend_flags) == 0, f"Dave should NOT have weekend work flag: {dave_flags}"
    assert "2026-01-19" in bridge_flags[0]
    assert "2026-01-20" in bridge_flags[0]

    # Eve: 1 hours-on-leave (no weekend work - duplicate moved to weekday)
    assert "Eve" in by_emp
    eve_flags = by_emp["Eve"]
    hours_on_leave_flags = [f for f in eve_flags if "hours on" in f and "sick leave" in f]
    weekend_flags = [f for f in eve_flags if "weekend" in f.lower()]
    assert len(hours_on_leave_flags) == 1, f"Eve should have 1 hours-on-leave flag, got {len(hours_on_leave_flags)}: {eve_flags}"
    assert len(weekend_flags) == 0, f"Eve should NOT have weekend work flag: {eve_flags}"
    assert "6.5 hours" in hours_on_leave_flags[0]
    assert "2026-01-19" in hours_on_leave_flags[0]

    # Frank: 1 unexplained absence (no weekend work - weekend row removed)
    assert "Frank" in by_emp
    frank_flags = by_emp["Frank"]
    absence_flags = [f for f in frank_flags if "no hours and no leave" in f]
    weekend_flags = [f for f in frank_flags if "weekend" in f.lower()]
    assert len(absence_flags) == 1, f"Frank should have 1 unexplained absence flag, got {len(absence_flags)}: {frank_flags}"
    assert len(weekend_flags) == 0, f"Frank should NOT have weekend work flag: {frank_flags}"
    assert "2026-01-28" in absence_flags[0]

    # Grace: 1 weekend work (Jan 17-18 are Sat-Sun)
    assert "Grace" in by_emp
    grace_flags = by_emp["Grace"]
    weekend_flags = [f for f in grace_flags if "weekend" in f.lower()]
    assert len(weekend_flags) == 1, f"Grace should have 1 weekend work flag, got {len(weekend_flags)}: {grace_flags}"
    assert "2026-01-17" in weekend_flags[0]
    assert "2026-01-18" in weekend_flags[0]

    # No other flags for these employees - each has exactly 1 flag
    expected_counts = {
        "Alice": 1,  # overwork
        "Bob": 1,    # short-hours
        "Carol": 1,  # leave-pattern
        "Dave": 1,   # bridge-leave
        "Eve": 1,    # hours-on-leave
        "Frank": 1,  # unexplained absence
        "Grace": 1,  # weekend work
    }
    for emp, expected_count in expected_counts.items():
        actual_count = len(by_emp.get(emp, []))
        assert actual_count == expected_count, (
            f"{emp} should have exactly {expected_count} flag(s), got {actual_count}: {by_emp.get(emp, [])}"
        )

    # Check duplicate-row warning for Eve on 2026-01-22 (moved from 2026-01-24)
    duplicate_warnings = [w for w in warnings if "duplicate" in w.lower() and "Eve" in w and "2026-01-22" in w]
    assert len(duplicate_warnings) == 1, f"Expected 1 duplicate warning for Eve on 2026-01-22, got {duplicate_warnings}"