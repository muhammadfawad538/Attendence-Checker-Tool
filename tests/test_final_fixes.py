import subprocess
import sys
from pathlib import Path


def test_warnings_before_error_no_valid_rows():
    """If no valid rows remain, print every per-row WARNING before the ERROR line."""
    csv_path = Path(__file__).parent / "data" / "cases" / "excessive_hours.csv"
    result = subprocess.run([sys.executable, "check.py", str(csv_path)], cwd=Path(__file__).parent.parent, capture_output=True, text=True)

    assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"
    output = result.stdout

    # Must have WARNING lines before ERROR
    assert "WARNING: Line 2: invalid hours '30'" in output
    assert "WARNING: Line 3: invalid hours '25'" in output
    assert "ERROR: No valid data rows" in output

    # Check order: WARNINGs come before ERROR
    warning_idx = output.index("WARNING: Line 2")
    error_idx = output.index("ERROR: No valid data rows")
    assert warning_idx < error_idx, "WARNINGs must appear before ERROR"


def test_name_merge_first_seen_spelling():
    """Name merging: display name is first-seen spelling, one warning per distinct spelling."""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write('employee,date,hours_worked,leave_type\n')
        f.write('McDonald,2026-01-01,8.0,\n')  # First seen: McDonald (capital M, capital D)
        f.write('mcdonald,2026-01-02,8.0,\n')  # Different casing
        f.write('MCDONALD,2026-01-03,8.0,\n')  # All caps
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, "check.py", tmp], cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        output = result.stdout

        # Should have exactly 2 merge warnings (one per distinct spelling after first)
        merge_warnings = [line for line in output.split('\n') if 'merged employee name' in line]
        assert len(merge_warnings) == 2, f"Expected 2 merge warnings, got {len(merge_warnings)}: {merge_warnings}"

        # Employee name should be first-seen spelling "McDonald"
        assert "FLAG: McDonald:" in output
        assert "FLAG: mcdonald:" not in output
        assert "FLAG: MCDONALD:" not in output

        # Each warning should show merging TO the canonical name
        for w in merge_warnings:
            assert "-> 'McDonald'" in w, f"Warning should show merge to McDonald: {w}"

        # No no-op warnings (where input spelling equals canonical)
        noop_warnings = [w for w in merge_warnings if "merged employee name 'McDonald' -> 'McDonald'" in w]
        assert len(noop_warnings) == 0, "Should not warn when spelling equals display name"
    finally:
        os.unlink(tmp)


def test_name_merge_alice():
    """alice/ALICE/Alice gives one employee with exactly 2 merge warnings."""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write('employee,date,hours_worked,leave_type\n')
        f.write('alice,2026-01-01,8.0,\n')    # First seen: alice (lowercase)
        f.write('ALICE,2026-01-02,8.0,\n')    # All caps
        f.write('Alice,2026-01-03,8.0,\n')    # Title case
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, "check.py", tmp], cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        output = result.stdout

        # Should have exactly 2 merge warnings
        merge_warnings = [line for line in output.split('\n') if 'merged employee name' in line]
        assert len(merge_warnings) == 2, f"Expected 2 merge warnings, got {len(merge_warnings)}: {merge_warnings}"

        # Display name should be first-seen "alice"
        assert "alice:" in output.lower()  # The flag message should use the canonical name

        # No no-op warnings
        for w in merge_warnings:
            assert "-> 'alice'" in w or '-> "alice"' in w
    finally:
        os.unlink(tmp)


def test_short_row_3_fields_rejected():
    """A row with fewer than 4 fields gets a WARNING with its line number and is skipped."""
    csv_path = Path(__file__).parent / "data" / "cases" / "short_row.csv"
    result = subprocess.run([sys.executable, "check.py", str(csv_path)], cwd=Path(__file__).parent.parent, capture_output=True, text=True)

    output = result.stdout

    # Both rows should be rejected (2-field and 3-field)
    assert "WARNING: Line 2:" in output
    assert "WARNING: Line 3:" in output
    assert "Skipped 2 row(s)." in output

    # Zero records -> ERROR without "Analyzing..." line
    assert "ERROR: No valid data rows" in output
    assert "Analyzing 0 records..." not in output
    assert "Done. Found 0 flag(s)." not in output


def test_30_hours_only_problem():
    """A file with only a 30-hour row as problem should be rejected with warning."""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write('employee,date,hours_worked,leave_type\n')
        f.write('Bad,2026-01-01,30,\n')
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, "check.py", tmp], cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        output = result.stdout

        # Should reject 30 hours
        assert "WARNING" in output
        assert "30" in output or "Skipped" in output
        assert result.returncode == 1  # ERROR because no valid rows remain
        assert "ERROR: No valid data rows" in output
    finally:
        os.unlink(tmp)


def test_30_hours_fails_on_old_loader():
    """Show 30 hours test FAILS against old loader (85fab24)."""
    import subprocess
    import sys

    # Run with old loader
    result = subprocess.run([sys.executable, "check.py", "tests/data/cases/excessive_hours.csv"],
                          cwd=Path(__file__).parent.parent, capture_output=True, text=True)
    output = result.stdout

    # Old loader (85fab24) accepted 30 hours - no WARNING for invalid hours
    # New loader should have WARNING
    assert "WARNING" in output, "Old loader accepted 30 hours without warning"
    assert "invalid hours '30'" in output