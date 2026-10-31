"""Tests for stricter rules added in Day 4."""
import subprocess
import sys
import json
import tempfile
import os
from pathlib import Path


def test_multiple_leave_types_warning():
    """Same person and day with two different leave types → WARNING."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write('employee,date,hours_worked,leave_type\n')
        f.write('Test,2026-01-01,0.0,annual\n')
        f.write('Test,2026-01-01,0.0,sick\n')
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, "check.py", tmp],
                              cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        output = result.stdout
        assert "multiple leave types" in output, f"Expected multiple leave types warning, got: {output}"
        assert "annual" in output and "sick" in output
    finally:
        os.unlink(tmp)


def test_strict_flag_exit_code():
    """--strict flag makes any WARNING exit code 1."""
    # hours.csv has a duplicate entry warning
    result = subprocess.run([sys.executable, "check.py", "data/hours.csv", "--strict"],
                          cwd=Path(__file__).parent.parent, capture_output=True, text=True)
    assert result.returncode == 1, f"Expected exit code 1 with --strict, got {result.returncode}"


def test_strict_flag_no_warning_exit_0():
    """--strict with no warnings should exit 0."""
    # Create a clean CSV with no warnings
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write('employee,date,hours_worked,leave_type\n')
        f.write('Test,2026-01-01,8.0,\n')
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, "check.py", tmp, "--strict"],
                              cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        assert result.returncode == 0, f"Expected exit code 0 with --strict and no warnings, got {result.returncode}"
    finally:
        os.unlink(tmp)


def test_format_json_output():
    """--format json prints flags and warnings as JSON."""
    result = subprocess.run([sys.executable, "check.py", "data/hours.csv", "--format", "json"],
                          cwd=Path(__file__).parent.parent, capture_output=True, text=True)
    output = result.stdout
    # Should be valid JSON
    # Find the JSON block (after "Analyzing..." line)
    json_start = output.index('{')
    json_text = output[json_start:]
    data = json.loads(json_text)
    assert "flags" in data
    assert "warnings" in data
    assert "skipped_rows" in data
    assert "total_records" in data
    assert len(data["flags"]) == 7  # 7 flags in hours.csv


def test_format_json_with_warnings():
    """--format json includes warnings in output."""
    result = subprocess.run([sys.executable, "check.py", "data/hours.csv", "--format", "json"],
                          cwd=Path(__file__).parent.parent, capture_output=True, text=True)
    output = result.stdout
    json_start = output.index('{')
    json_text = output[json_start:]
    data = json.loads(json_text)
    assert len(data["warnings"]) > 0, "Expected warnings in JSON output"


def test_performance_100x_under_30s():
    """Full check.py on 100x data should complete in under 30 seconds."""
    import time
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "check.py", "tests/data/big/hours_100x.csv"],
        cwd=Path(__file__).parent.parent, capture_output=True, text=True
    )
    elapsed = time.perf_counter() - start
    assert elapsed < 30.0, f"check.py took {elapsed:.3f}s, expected < 30.0s"
    assert result.returncode == 0, f"check.py failed: {result.stderr}"


def test_multiple_leave_types_does_not_crash():
    """Multiple leave types on same day should not crash the tool."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write('employee,date,hours_worked,leave_type\n')
        f.write('Test,2026-01-01,0.0,annual\n')
        f.write('Test,2026-01-01,0.0,sick\n')
        f.write('Test,2026-01-02,8.0,\n')
        tmp = f.name
    try:
        result = subprocess.run([sys.executable, "check.py", tmp],
                              cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        assert result.returncode == 0, f"check.py failed: {result.stderr}"
    finally:
        os.unlink(tmp)