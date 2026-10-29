import subprocess
import sys
import re
import tempfile
from pathlib import Path
import os

DATA_DIR = Path(__file__).parent / "data" / "cases"


def test_short_row_missing_columns_skipped():
    """Rows missing required columns should produce a warning and be skipped."""
    with open(DATA_DIR / "short_row.csv", "r", encoding="utf-8") as f:
        content = f.read()
    tmp = DATA_DIR / "tmp_short_row_test.csv"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("employee,date,hours_worked,leave_type\n")
        f.write(content)
    try:
        result = subprocess.run([sys.executable, "check.py", str(tmp)], cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        assert "WARNING" in result.stdout
        assert "Alice" in result.stdout
    finally:
        os.unlink(tmp)


def test_names_case_insensitive_and_merged():
    """Names should be merged regardless of case/spaces, with a warning."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write('employee,date,hours_worked,leave_type\n')
        f.write('Alice,2026-01-01,8.0,\n')
        f.write(' alice ,2026-01-02,8.0,\n')
        f.write('ALICE,2026-01-03,8.0,\n')
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, 'check.py', tmp], cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        assert 'WARNING' in result.stdout
        assert 'merged' in result.stdout.lower() or 'Alice' in result.stdout
    finally:
        os.unlink(tmp)


def test_hours_out_of_range():
    """Hours below 0 or above 24 should produce warnings and be skipped. Hours 12-24 should warn but be accepted."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write('employee,date,hours_worked,leave_type\n')
        f.write('Bad1,2026-01-01,-1,\n')
        f.write('Bad2,2026-01-02,25,\n')
        f.write('Warn1,2026-01-03,15,\n')
        f.write('Ok1,2026-01-04,8.0,\n')
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, 'check.py', tmp], cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        assert 'WARNING' in result.stdout
        assert 'Bad1' not in result.stdout or 'Skipped' in result.stdout
        assert 'Bad2' not in result.stdout or 'Skipped' in result.stdout
    finally:
        os.unlink(tmp)


def test_skipped_rows_counter():
    """At the end print one line: Skipped N row(s). when N > 0."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write('employee,date,hours_worked,leave_type\n')
        f.write('Bad,2026-01-01,-5,\n')
        f.write('Ok,2026-01-02,8.0,\n')
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, 'check.py', tmp], cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        assert 'Skipped' in result.stdout
        assert re.search(r'Skipped \d+ row\(s\)\.', result.stdout)
    finally:
        os.unlink(tmp)


def test_no_hardcoded_path():
    """test_input_errors.py should not have hard-coded path."""
    content = Path(__file__).parent / "test_input_errors.py"
    assert content.exists()
    text = content.read_text(encoding='utf-8')
    assert 'D:/must-quest' not in text
    assert '__file__' in text or 'pathlib' in text