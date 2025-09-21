"""Tests for the CLI module."""

import subprocess
import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.cli import main


def test_main_function():
    """Test that the main function runs without error."""
    result = main([])
    assert result == 0


def test_cli_execution():
    """Test that the CLI can be executed as a module."""
    result = subprocess.run(
        [sys.executable, "-m", "cronpal.cli"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent / "src"
    )
    assert result.returncode == 0
    assert "cronpal" in result.stdout.lower()


def test_version_flag():
    """Test the --version flag."""
    result = main(["--version"])
    assert result == 0


def test_version_flag_short():
    """Test the -v flag."""
    result = main(["-v"])
    assert result == 0


def test_help_output():
    """Test that help is shown when no arguments provided."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main([])

    output = f.getvalue()
    assert "usage:" in output.lower()
    assert "cronpal" in output.lower()


def test_valid_expression():
    """Test parsing a valid cron expression."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 * * *"])

    output = f.getvalue()
    assert result == 0
    assert "✓ Valid" in output
    assert "0 0 * * *" in output


def test_minute_field_parsing():
    """Test that minute field is parsed."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["*/15 0 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Minute field: */15" in output
    assert "Values: [0, 15, 30, 45]" in output


def test_hour_field_parsing():
    """Test that hour field is parsed."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 */4 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Hour field: */4" in output
    assert "Values: [0, 4, 8, 12, 16, 20]" in output


def test_both_minute_and_hour_parsing():
    """Test parsing both minute and hour fields."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["*/30 9-17 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Minute field: */30" in output
    assert "Values: [0, 30]" in output
    assert "Hour field: 9-17" in output
    assert "Values: [9, 10, 11, 12, 13, 14, 15, 16, 17]" in output


def test_minute_field_range_parsing():
    """Test parsing minute field with range."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0-5 0 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Minute field: 0-5" in output
    assert "Values: [0, 1, 2, 3, 4, 5]" in output


def test_hour_field_range_parsing():
    """Test parsing hour field with range."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 8-18/2 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Hour field: 8-18/2" in output
    assert "Values: [8, 10, 12, 14, 16, 18]" in output


def test_minute_field_list_parsing():
    """Test parsing minute field with list."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0,15,30,45 0 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Minute field: 0,15,30,45" in output
    assert "Values: [0, 15, 30, 45]" in output


def test_hour_field_list_parsing():
    """Test parsing hour field with list."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0,6,12,18 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Hour field: 0,6,12,18" in output
    assert "Values: [0, 6, 12, 18]" in output


def test_minute_field_wildcard_parsing():
    """Test parsing minute field with wildcard."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["* 0 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Minute field: *" in output
    # Should show truncated list for 60 values
    assert "Total: 60 values" in output


def test_hour_field_wildcard_parsing():
    """Test parsing hour field with wildcard."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 * * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Hour field: *" in output
    # Should show truncated list for 24 values
    assert "Total: 24 values" in output


def test_minute_field_invalid_value():
    """Test invalid minute field value."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["60 0 * * *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "minute" in error_output.lower()
    assert "out of range" in error_output.lower()


def test_hour_field_invalid_value():
    """Test invalid hour field value."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["0 24 * * *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "hour" in error_output.lower()
    assert "out of range" in error_output.lower()


def test_invalid_expression_with_suggestion():
    """Test parsing an invalid expression with suggestion."""
    import io
    import contextlib

    f_out = io.StringIO()
    f_err = io.StringIO()

    with contextlib.redirect_stdout(f_out), contextlib.redirect_stderr(f_err):
        result = main(["0 0 *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "✗ Invalid" in error_output
    assert "💡 Suggestion:" in error_output
    assert "Add missing fields" in error_output


def test_invalid_character_with_suggestion():
    """Test invalid character with suggestion."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["0 0 * * $"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "✗ Validation failed" in error_output
    assert "💡 Suggestion:" in error_output


def test_verbose_flag_valid():
    """Test the --verbose flag with valid expression."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Raw expression:" in output
    assert "Validation: PASSED" in output
    assert "Minute field:" in output
    assert "Hour field:" in output


def test_verbose_flag_invalid():
    """Test the --verbose flag with invalid expression."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stderr(f):
        result = main(["invalid", "--verbose"])

    output = f.getvalue()
    assert result == 1
    assert "Expression: 'invalid'" in output
    assert "Expected format:" in output


def test_next_flag():
    """Test the --next flag."""
    result = main(["0 0 * * *", "--next", "10"])
    assert result == 0


def test_special_string():
    """Test parsing a special string."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["@daily"])

    output = f.getvalue()
    assert result == 0
    assert "✓ Valid" in output
    assert "@daily" in output