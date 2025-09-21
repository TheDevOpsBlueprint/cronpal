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


def test_day_of_month_field_parsing():
    """Test that day of month field is parsed."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1,15 * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Day of month field: 1,15" in output
    assert "Values: [1, 15]" in output


def test_all_three_fields_parsing():
    """Test parsing minute, hour, and day fields."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["*/30 9-17 1-7 * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Minute field: */30" in output
    assert "Values: [0, 30]" in output
    assert "Hour field: 9-17" in output
    assert "Values: [9, 10, 11, 12, 13, 14, 15, 16, 17]" in output
    assert "Day of month field: 1-7" in output
    assert "Values: [1, 2, 3, 4, 5, 6, 7]" in output


def test_day_field_wildcard_parsing():
    """Test parsing day field with wildcard."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Day of month field: *" in output
    # Should show truncated list for 31 values
    assert "Total: 31 values" in output


def test_day_field_range_parsing():
    """Test parsing day field with range."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 10-20 * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Day of month field: 10-20" in output
    assert "Values: [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]" in output


def test_day_field_step_parsing():
    """Test parsing day field with step."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 */5 * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Day of month field: */5" in output
    assert "Values: [1, 6, 11, 16, 21, 26, 31]" in output


def test_day_field_list_parsing():
    """Test parsing day field with list."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1,10,20,30 * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Day of month field: 1,10,20,30" in output
    assert "Values: [1, 10, 20, 30]" in output


def test_day_field_invalid_value_zero():
    """Test invalid day field value (0)."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["0 0 0 * *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "day of month" in error_output.lower()
    assert "out of range" in error_output.lower()


def test_day_field_invalid_value_high():
    """Test invalid day field value (32)."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["0 0 32 * *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "day of month" in error_output.lower()
    assert "out of range" in error_output.lower()


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
        result = main(["0 0 1 * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Raw expression:" in output
    assert "Validation: PASSED" in output
    assert "Minute field:" in output
    assert "Hour field:" in output
    assert "Day of month field:" in output


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


def test_month_field_parsing():
    """Test that month field is parsed."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1 6 *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Month field: 6" in output
    assert "Values: [6]" in output
    assert "Months: Jun" in output


def test_month_field_name_parsing():
    """Test that month field with names is parsed."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1 JAN *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Month field: JAN" in output
    assert "Values: [1]" in output
    assert "Months: Jan" in output


def test_month_field_range_parsing():
    """Test parsing month field with range."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1 1-3 *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Month field: 1-3" in output
    assert "Values: [1, 2, 3]" in output
    assert "Months: Jan, Feb, Mar" in output


def test_month_field_name_range_parsing():
    """Test parsing month field with name range."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1 JAN-MAR *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Month field: JAN-MAR" in output
    assert "Values: [1, 2, 3]" in output
    assert "Months: Jan, Feb, Mar" in output


def test_month_field_list_parsing():
    """Test parsing month field with list."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1 1,6,12 *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Month field: 1,6,12" in output
    assert "Values: [1, 6, 12]" in output
    assert "Months: Jan, Jun, Dec" in output


def test_month_field_name_list_parsing():
    """Test parsing month field with name list."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1 JAN,JUN,DEC *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Month field: JAN,JUN,DEC" in output
    assert "Values: [1, 6, 12]" in output
    assert "Months: Jan, Jun, Dec" in output


def test_month_field_step_parsing():
    """Test parsing month field with step."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1 */3 *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Month field: */3" in output
    assert "Values: [1, 4, 7, 10]" in output
    assert "Months: Jan, Apr, Jul, Oct" in output


def test_month_field_wildcard_parsing():
    """Test parsing month field with wildcard."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1 * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Month field: *" in output
    # Should show all 12 months
    assert "Total: 12 values" in output


def test_month_field_invalid_value_zero():
    """Test invalid month field value (0)."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["0 0 1 0 *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "month" in error_output.lower()
    assert "out of range" in error_output.lower()


def test_month_field_invalid_value_high():
    """Test invalid month field value (13)."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["0 0 1 13 *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "month" in error_output.lower()
    assert "out of range" in error_output.lower()


def test_month_field_invalid_name():
    """Test invalid month name."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["0 0 1 JANUARY *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "month" in error_output.lower()
    assert "not a number" in error_output.lower()


def test_month_field_mixed_parsing():
    """Test parsing month field with mixed names and numbers."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 1 1,FEB,3,APR *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Month field: 1,FEB,3,APR" in output
    assert "Values: [1, 2, 3, 4]" in output
    assert "Months: Jan, Feb, Mar, Apr" in output


def test_all_four_fields_parsing():
    """Test parsing minute, hour, day, and month fields."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["30 2 15 JAN-MAR *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Minute field: 30" in output
    assert "Hour field: 2" in output
    assert "Day of month field: 15" in output
    assert "Month field: JAN-MAR" in output
    assert "Months: Jan, Feb, Mar" in output