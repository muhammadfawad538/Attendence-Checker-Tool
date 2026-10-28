"""Test for noisy dataset - reproduces original noisy situation as regression case."""
from attendance.loader import load_csv
from attendance.rules import (
    check_overwork,
    check_short_or_late,
    check_leave_pattern,
    check_bridge_leave,
    check_hours_on_leave,
    check_unexplained_absence,
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

    # Group by employee
    by_emp = {}
    for emp, msg in all_flags:
        by_emp.setdefault(emp, []).append(msg)

    # Assert expected flags per employee from noisy data
    # Alice: 2 absence (Jan 6, 7) + 1 overwork = 3 flags
    assert "Alice" in by_emp
    alice_flags = by_emp["Alice"]
    assert len(alice_flags) == 3
    absence_alice = [f for f in alice_flags if "no hours and no leave" in f]
    overwork_alice = [f for f in alice_flags if "11+ hours" in f]
    assert len(absence_alice) == 2, f"Alice should have 2 absence flags: {absence_alice}"
    assert len(overwork_alice) == 1, f"Alice should have 1 overwork flag: {overwork_alice}"
    assert "2026-01-06" in absence_alice[0] or "2026-01-06" in absence_alice[1]
    assert "2026-01-07" in absence_alice[0] or "2026-01-07" in absence_alice[1]

    # Bob: 2 absence (Jan 6, 7) + 0 short-hours (0-hour days not counted) = 2 flags
    assert "Bob" in by_emp
    bob_flags = by_emp["Bob"]
    assert len(bob_flags) == 2
    absence_bob = [f for f in bob_flags if "no hours and no leave" in f]
    assert len(absence_bob) == 2, f"Bob should have 2 absence flags: {absence_bob}"
    short_bob = [f for f in bob_flags if "under 4 hours" in f]
    assert len(short_bob) == 0, f"Bob should NOT have short-hours flag (0-hour days excluded): {short_bob}"

    # Carol: 2 absence (Jan 6, 7) + 1 leave-pattern = 3 flags
    assert "Carol" in by_emp
    carol_flags = by_emp["Carol"]
    assert len(carol_flags) == 3
    absence_carol = [f for f in carol_flags if "no hours and no leave" in f]
    leave_carol = [f for f in carol_flags if "Mondays or Fridays" in f]
    assert len(absence_carol) == 2, f"Carol should have 2 absence flags: {absence_carol}"
    assert len(leave_carol) == 1, f"Carol should have 1 leave-pattern flag: {leave_carol}"

    # Dave: 4 absence (Jan 6, 7, 26, 27) + 1 bridge = 5 flags
    assert "Dave" in by_emp
    dave_flags = by_emp["Dave"]
    assert len(dave_flags) == 5
    absence_dave = [f for f in dave_flags if "no hours and no leave" in f]
    bridge_dave = [f for f in dave_flags if "public holiday" in f]
    assert len(absence_dave) == 4, f"Dave should have 4 absence flags: {absence_dave}"
    assert len(bridge_dave) == 1, f"Dave should have 1 bridge flag: {bridge_dave}"

    # Eve: 4 absence (Jan 6, 7, 26, 27) + 1 hours-on-leave + duplicate warning = 5 flags + warning
    assert "Eve" in by_emp
    eve_flags = by_emp["Eve"]
    assert len(eve_flags) == 5
    absence_eve = [f for f in eve_flags if "no hours and no leave" in f]
    hours_eve = [f for f in eve_flags if "hours on" in f and "sick leave" in f]
    assert len(absence_eve) == 4, f"Eve should have 4 absence flags: {absence_eve}"
    assert len(hours_eve) == 1, f"Eve should have 1 hours-on-leave flag: {hours_eve}"

    # Duplicate warning for Eve on 2026-01-24
    duplicate_warnings = [w for w in warnings if "duplicate" in w.lower() and "Eve" in w and "2026-01-24" in w]
    assert len(duplicate_warnings) == 1, f"Expected 1 duplicate warning for Eve on 2026-01-24, got {duplicate_warnings}"

    # Frank: 7 absence (Jan 6, 7, 26, 27, 28, 29, 30) = 7 flags
    assert "Frank" in by_emp
    frank_flags = by_emp["Frank"]
    assert len(frank_flags) == 7
    absence_frank = [f for f in frank_flags if "no hours and no leave" in f]
    assert len(absence_frank) == 7, f"Frank should have 7 absence flags: {absence_frank}"
    short_frank = [f for f in frank_flags if "under 4 hours" in f]
    assert len(short_frank) == 0, f"Frank should NOT have short-hours flag (0-hour days excluded): {short_frank}"

    # Total flags should be 3+2+3+5+5+7 = 25
    total_flags = sum(len(flags) for flags in by_emp.values())
    assert total_flags == 25, f"Total flags should be 25, got {total_flags}"