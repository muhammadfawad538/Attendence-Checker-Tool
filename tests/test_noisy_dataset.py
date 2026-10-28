"""Test for noisy dataset - reproduces original noisy situation as regression case."""
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


def test_noisy_dataset_expected_output():
    """Run the whole pipeline on data/hours_noisy.csv and assert exact expected output."""
    records, warnings = load_csv("data/hours_noisy.csv")

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

    # Assert expected flags per employee from noisy data
    # Alice: 2 absence (Jan 6, 7) + 1 weekend work (no overwork - only 2 working days with 12h+) = 3 flags
    assert "Alice" in by_emp
    alice_flags = by_emp["Alice"]
    assert len(alice_flags) == 3
    absence_alice = [f for f in alice_flags if "no hours and no leave" in f]
    weekend_alice = [f for f in alice_flags if "weekend" in f.lower()]
    overwork_alice = [f for f in alice_flags if "11+ hours" in f]
    assert len(absence_alice) == 2, f"Alice should have 2 absence flags: {absence_alice}"
    assert len(weekend_alice) == 1, f"Alice should have 1 weekend work flag: {weekend_alice}"
    assert len(overwork_alice) == 0, f"Alice should NOT have overwork flag (only 2 working days): {overwork_alice}"
    assert "2026-01-06" in absence_alice[0] or "2026-01-06" in absence_alice[1]
    assert "2026-01-07" in absence_alice[0] or "2026-01-07" in absence_alice[1]

    # Bob: 2 absence (Jan 6, 7) + 1 weekend work + 0 short-hours = 3 flags
    assert "Bob" in by_emp
    bob_flags = by_emp["Bob"]
    assert len(bob_flags) == 3
    absence_bob = [f for f in bob_flags if "no hours and no leave" in f]
    weekend_bob = [f for f in bob_flags if "weekend" in f.lower()]
    short_bob = [f for f in bob_flags if "under 4 hours" in f]
    assert len(absence_bob) == 2, f"Bob should have 2 absence flags: {absence_bob}"
    assert len(weekend_bob) == 1, f"Bob should have 1 weekend work flag: {weekend_bob}"
    assert len(short_bob) == 0, f"Bob should NOT have short-hours flag (0-hour days excluded): {short_bob}"

    # Carol: 2 absence (Jan 6, 7) + 1 leave-pattern + 1 weekend work = 4 flags
    assert "Carol" in by_emp
    carol_flags = by_emp["Carol"]
    assert len(carol_flags) == 4
    absence_carol = [f for f in carol_flags if "no hours and no leave" in f]
    leave_carol = [f for f in carol_flags if "Mondays or Fridays" in f]
    weekend_carol = [f for f in carol_flags if "weekend" in f.lower()]
    assert len(absence_carol) == 2, f"Carol should have 2 absence flags: {absence_carol}"
    assert len(leave_carol) == 1, f"Carol should have 1 leave-pattern flag: {leave_carol}"
    assert len(weekend_carol) == 1, f"Carol should have 1 weekend work flag: {weekend_carol}"

    # Dave: 4 absence (Jan 6, 7, 26, 27) + 1 bridge + 1 weekend work = 6 flags
    assert "Dave" in by_emp
    dave_flags = by_emp["Dave"]
    assert len(dave_flags) == 6
    absence_dave = [f for f in dave_flags if "no hours and no leave" in f]
    bridge_dave = [f for f in dave_flags if "public holiday" in f]
    weekend_dave = [f for f in dave_flags if "weekend" in f.lower()]
    assert len(absence_dave) == 4, f"Dave should have 4 absence flags: {absence_dave}"
    assert len(bridge_dave) == 1, f"Dave should have 1 bridge flag: {bridge_dave}"
    assert len(weekend_dave) == 1, f"Dave should have 1 weekend work flag: {weekend_dave}"

    # Eve: 4 absence (Jan 6, 7, 26, 27) + 1 hours-on-leave + 1 weekend work = 6 flags + warning
    assert "Eve" in by_emp
    eve_flags = by_emp["Eve"]
    assert len(eve_flags) == 6
    absence_eve = [f for f in eve_flags if "no hours and no leave" in f]
    hours_eve = [f for f in eve_flags if "hours on" in f and "sick leave" in f]
    weekend_eve = [f for f in eve_flags if "weekend" in f.lower()]
    assert len(absence_eve) == 4, f"Eve should have 4 absence flags: {absence_eve}"
    assert len(hours_eve) == 1, f"Eve should have 1 hours-on-leave flag: {hours_eve}"
    assert len(weekend_eve) == 1, f"Eve should have 1 weekend work flag: {weekend_eve}"

    # Duplicate warning for Eve on 2026-01-24
    duplicate_warnings = [w for w in warnings if "duplicate" in w.lower() and "Eve" in w and "2026-01-24" in w]
    assert len(duplicate_warnings) == 1, f"Expected 1 duplicate warning for Eve on 2026-01-24, got {duplicate_warnings}"

    # Frank: 7 absence (Jan 6, 7, 26, 27, 28, 29, 30) + 1 weekend work = 8 flags
    assert "Frank" in by_emp
    frank_flags = by_emp["Frank"]
    assert len(frank_flags) == 8
    absence_frank = [f for f in frank_flags if "no hours and no leave" in f]
    weekend_frank = [f for f in frank_flags if "weekend" in f.lower()]
    short_frank = [f for f in frank_flags if "under 4 hours" in f]
    assert len(absence_frank) == 7, f"Frank should have 7 absence flags: {absence_frank}"
    assert len(weekend_frank) == 1, f"Frank should have 1 weekend work flag: {weekend_frank}"
    assert len(short_frank) == 0, f"Frank should NOT have short-hours flag (0-hour days excluded): {short_frank}"

    # Total flags should be 3+3+4+6+6+8 = 30
    total_flags = sum(len(flags) for flags in by_emp.values())
    assert total_flags == 30, f"Total flags should be 30, got {total_flags}"