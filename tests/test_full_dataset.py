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

    # Assert exact expected flags per employee
    # Alice: 1 weekend work (no overwork - only 2 working days with 12h+)
    assert "Alice" in by_emp
    alice_flags = by_emp["Alice"]
    weekend_flags = [f for f in alice_flags if "weekend" in f.lower()]
    assert len(weekend_flags) == 1, f"Alice should have 1 weekend work flag, got {len(weekend_flags)}: {alice_flags}"
    assert "4 weekend day(s)" in weekend_flags[0] or "weekend" in weekend_flags[0]
    # Alice should NOT have overwork flag (only 2 working days with 12h+)
    overwork_flags = [f for f in alice_flags if "11+ hours" in f]
    assert len(overwork_flags) == 0, f"Alice should NOT have overwork flag: {overwork_flags}"

    # Bob: 1 short-hours + 1 weekend work
    assert "Bob" in by_emp
    bob_flags = by_emp["Bob"]
    short_flags = [f for f in bob_flags if "under 4 hours" in f]
    weekend_flags = [f for f in bob_flags if "weekend" in f.lower()]
    assert len(short_flags) == 1, f"Bob should have 1 short-hours flag, got {len(short_flags)}: {bob_flags}"
    assert len(weekend_flags) == 1, f"Bob should have 1 weekend work flag, got {len(weekend_flags)}: {bob_flags}"
    assert "consecutive working days" in short_flags[0]

    # Carol: 1 leave-pattern (Mon/Fri) + 1 weekend work
    assert "Carol" in by_emp
    carol_flags = by_emp["Carol"]
    leave_flags = [f for f in carol_flags if "Mondays or Fridays" in f]
    weekend_flags = [f for f in carol_flags if "weekend" in f.lower()]
    assert len(leave_flags) == 1, f"Carol should have 1 leave-pattern flag, got {len(leave_flags)}: {carol_flags}"
    assert len(weekend_flags) == 1, f"Carol should have 1 weekend work flag, got {len(weekend_flags)}: {carol_flags}"
    assert "5" in leave_flags[0] or "annual" in leave_flags[0]

    # Dave: 1 bridge-leave + 1 weekend work
    assert "Dave" in by_emp
    dave_flags = by_emp["Dave"]
    bridge_flags = [f for f in dave_flags if "public holiday" in f]
    weekend_flags = [f for f in dave_flags if "weekend" in f.lower()]
    assert len(bridge_flags) == 1, f"Dave should have 1 bridge-leave flag, got {len(bridge_flags)}: {dave_flags}"
    assert len(weekend_flags) == 1, f"Dave should have 1 weekend work flag, got {len(weekend_flags)}: {dave_flags}"
    assert "2026-01-19" in bridge_flags[0]
    assert "2026-01-20" in bridge_flags[0]

    # Eve: 1 hours-on-leave + 1 weekend work
    assert "Eve" in by_emp
    eve_flags = by_emp["Eve"]
    hours_on_leave_flags = [f for f in eve_flags if "hours on" in f and "sick leave" in f]
    weekend_flags = [f for f in eve_flags if "weekend" in f.lower()]
    assert len(hours_on_leave_flags) == 1, f"Eve should have 1 hours-on-leave flag, got {len(hours_on_leave_flags)}: {eve_flags}"
    assert len(weekend_flags) == 1, f"Eve should have 1 weekend work flag, got {len(weekend_flags)}: {eve_flags}"
    assert "6.5 hours" in hours_on_leave_flags[0]
    assert "2026-01-19" in hours_on_leave_flags[0]

    # Frank: 1 unexplained absence + 1 weekend work
    assert "Frank" in by_emp
    frank_flags = by_emp["Frank"]
    absence_flags = [f for f in frank_flags if "no hours and no leave" in f]
    weekend_flags = [f for f in frank_flags if "weekend" in f.lower()]
    assert len(absence_flags) == 1, f"Frank should have 1 unexplained absence flag, got {len(absence_flags)}: {frank_flags}"
    assert len(weekend_flags) == 1, f"Frank should have 1 weekend work flag, got {len(weekend_flags)}: {frank_flags}"
    assert "2026-01-28" in absence_flags[0]

    # No other flags for these employees
    # (Alice, Bob, Carol, Dave, Eve, Frank should ONLY have the flags above)
    expected_counts = {
        "Alice": 1,  # weekend work
        "Bob": 2,    # short-hours + weekend work
        "Carol": 2,  # leave-pattern + weekend work
        "Dave": 2,   # bridge-leave + weekend work
        "Eve": 2,    # hours-on-leave + weekend work
        "Frank": 2,  # unexplained absence + weekend work
    }
    for emp, expected_count in expected_counts.items():
        actual_count = len(by_emp.get(emp, []))
        assert actual_count == expected_count, (
            f"{emp} should have exactly {expected_count} flag(s), got {actual_count}: {by_emp.get(emp, [])}"
        )

    # Check duplicate-row warning for Eve on 2026-01-24
    duplicate_warnings = [w for w in warnings if "duplicate" in w.lower() and "Eve" in w and "2026-01-24" in w]
    assert len(duplicate_warnings) == 1, f"Expected 1 duplicate warning for Eve on 2026-01-24, got {duplicate_warnings}"