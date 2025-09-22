"""Tests for CLI pretty print functionality."""

import subprocess
import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.cli import main


class TestCLIPrettyPrint:
    """Tests for CLI --pretty flag functionality."""

    def test_pretty_flag_basic(self):
        """Test --pretty flag with basic expression."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "┌" in output  # Table border
        assert "│" in output  # Table border
        assert "└" in output  # Table border
        assert "Cron Expression Analysis" in output
        assert "Field" in output
        assert "Value" in output
        assert "Description" in output
        assert "Summary: Runs daily at 00:00" in output

    def test_pretty_flag_with_every_minute(self):
        """Test --pretty flag with every minute expression."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["* * * * *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Summary: Runs every minute" in output

    def test_pretty_flag_with_hourly(self):
        """Test --pretty flag with hourly expression."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["30 * * * *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Summary: Runs every hour at minute 30" in output

    def test_pretty_flag_with_ranges(self):
        """Test --pretty flag with range expressions."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 9-17 * * *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "9-17" in output
        assert "From 9 to 17" in output

    def test_pretty_flag_with_lists(self):
        """Test --pretty flag with list expressions."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0,15,30,45 12 * * *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "0,15,30,45" in output
        assert "At minutes 0, 15, 30, 45" in output

    def test_pretty_flag_with_steps(self):
        """Test --pretty flag with step expressions."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/10 * * * *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "*/10" in output
        assert "Every 10 minutes" in output

    def test_pretty_flag_with_month_names(self):
        """Test --pretty flag with month names."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 1 JAN,JUL *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "JAN,JUL" in output
        assert "January" in output or "July" in output

    def test_pretty_flag_with_day_names(self):
        """Test --pretty flag with day names."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * MON-FRI", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "MON-FRI" in output
        assert "From 1 to 5" in output or "Monday" in output

    def test_pretty_flag_with_verbose(self):
        """Test --pretty flag with --verbose."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--pretty", "--verbose"])

        output = f.getvalue()
        assert result == 0
        # Should have both table and detailed output
        assert "Cron Expression Analysis" in output  # Table
        assert "═" * 80 in output  # Detailed header
        assert "CRON EXPRESSION: 0 0 * * *" in output
        assert "▸ MINUTE" in output
        assert "Raw Value:" in output
        assert "Range:" in output
        assert "Values:" in output

    def test_pretty_flag_with_special_string_daily(self):
        """Test --pretty flag with @daily."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@daily", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Summary: Runs daily at 00:00" in output

    def test_pretty_flag_with_special_string_hourly(self):
        """Test --pretty flag with @hourly."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@hourly", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Summary: Runs every hour at minute 00" in output

    def test_pretty_flag_with_special_string_weekly(self):
        """Test --pretty flag with @weekly."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@weekly", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Summary: Runs every Sunday at 00:00" in output

    def test_pretty_flag_with_special_string_monthly(self):
        """Test --pretty flag with @monthly."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@monthly", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Summary: Runs on day 1 of every month at 00:00" in output

    def test_pretty_flag_with_special_string_yearly(self):
        """Test --pretty flag with @yearly."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@yearly", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Summary: Runs on January 1 at 00:00" in output

    def test_pretty_flag_with_special_string_reboot(self):
        """Test --pretty flag with @reboot."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@reboot", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Valid cron expression: @reboot" in output
        assert "system startup" in output

    def test_pretty_flag_complex_expression(self):
        """Test --pretty flag with complex expression."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/15 9-17 1,15 * MON-FRI", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "*/15" in output
        assert "9-17" in output
        assert "1,15" in output
        assert "MON-FRI" in output
        assert "Summary:" in output

    def test_pretty_flag_with_next_runs(self):
        """Test --pretty flag combined with --next."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--pretty", "--next", "2"])

        output = f.getvalue()
        assert result == 0
        assert "Cron Expression Analysis" in output
        assert "Summary:" in output
        assert "Next 2 runs:" in output

    def test_pretty_flag_with_previous_runs(self):
        """Test --pretty flag combined with --previous."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--pretty", "--previous", "2"])

        output = f.getvalue()
        assert result == 0
        assert "Cron Expression Analysis" in output
        assert "Summary:" in output
        assert "Previous 2 runs" in output

    def test_pretty_flag_with_timezone(self):
        """Test --pretty flag combined with --timezone."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--pretty", "--timezone", "UTC"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: UTC" in output
        assert "Cron Expression Analysis" in output

    def test_pretty_flag_table_formatting(self):
        """Test that table formatting is correct."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["30 14 1 6 3", "--pretty"])

        output = f.getvalue()
        assert result == 0

        # Check table structure
        assert "├" in output  # Table separator
        assert "┼" in output  # Column separator
        assert "─" in output  # Horizontal line

        # Check all fields are present
        assert "Minute" in output
        assert "Hour" in output
        assert "Day of Month" in output
        assert "Month" in output
        assert "Day of Week" in output

        # Check values
        assert "30" in output
        assert "14" in output
        assert "1" in output
        assert "6" in output
        assert "3" in output

    def test_pretty_flag_field_descriptions(self):
        """Test that field descriptions are accurate."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 */4 * * *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Every 4 hours" in output

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 15 * *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "At day 15" in output or "day of month 15" in output

    def test_pretty_flag_summary_accuracy(self):
        """Test that summaries are accurate for various patterns."""
        import io
        import contextlib

        # Test weekly pattern
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            main(["0 9 * * 1", "--pretty"])
        output = f.getvalue()
        assert "Runs every Monday at 09:00" in output

        # Test monthly pattern
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            main(["0 0 15 * *", "--pretty"])
        output = f.getvalue()
        assert "Runs on day 15 of every month at 00:00" in output

        # Test yearly pattern
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            main(["0 0 25 12 *", "--pretty"])
        output = f.getvalue()
        assert "Runs on December 25 at 00:00" in output

    def test_pretty_flag_invalid_expression(self):
        """Test --pretty flag with invalid expression."""
        import io
        import contextlib

        f_err = io.StringIO()
        with contextlib.redirect_stderr(f_err):
            result = main(["invalid", "--pretty"])

        error_output = f_err.getvalue()
        assert result == 1
        assert "Invalid" in error_output
        # Should not show pretty output for invalid expression