"""Tests for data quality warnings - missing working-day rows."""
from attendance.loader import load_csv


def test_missing_working_day_row_warning():
    """A CSV that skips a working day should produce a WARNING (not a FLAG)."""
    import tempfile
    import os

    # CSV with a gap: Mon, Wed (missing Tue)
    csv_content = """employee,date,hours_worked,leave_type
Alice,2026-01-12,8.0,
Alice,2026-01-14,8.0,
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        tmp_path = f.name

    try:
        records, warnings = load_csv(tmp_path)
        # Should find the missing working day
        missing_warnings = [w for w in warnings if "missing working day" in w.lower() or "gap" in w.lower()]
        assert len(missing_warnings) >= 1, f"Expected warning about missing working day, got {warnings}"
    finally:
        os.unlink(tmp_path)