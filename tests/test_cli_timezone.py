"""Tests for CLI timezone functionality."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
import pytz

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.cli import main


class TestCLITimezone:
    """Tests for CLI timezone functionality."""

    def test_timezone_flag_utc(self):
        """Test --timezone flag with UTC."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "UTC"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: UTC" in output
        assert "Valid cron expression" in output

    def test_timezone_flag_us_eastern(self):
        """Test --timezone flag with US/Eastern."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "US/Eastern"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: US/Eastern" in output
        assert "EST" in output or "EDT" in output

    def test_timezone_flag_europe_london(self):
        """Test --timezone flag with Europe/London."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "Europe/London"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: Europe/London" in output
        assert "GMT" in output or "BST" in output

    def test_timezone_flag_asia_tokyo(self):
        """Test --timezone flag with Asia/Tokyo."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "Asia/Tokyo"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: Asia/Tokyo" in output
        assert "JST" in output

    def test_timezone_flag_invalid(self):
        """Test --timezone flag with invalid timezone."""
        import io
        import contextlib

        f_err = io.StringIO()
        with contextlib.redirect_stderr(f_err):
            result = main(["0 0 * * *", "--timezone", "Invalid/Zone"])

        error_output = f_err.getvalue()
        assert result == 1
        assert "Invalid timezone" in error_output

    def test_timezone_with_next_runs(self):
        """Test timezone affects next run calculations."""
        import io
        import contextlib

        # Mock datetime to fix the time
        with patch('cronpal.timezone_utils.datetime') as mock_datetime:
            # Fix time to noon UTC
            fixed_time = datetime(2024, 1, 15, 12, 0, 0)
            mock_datetime.now.return_value = fixed_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                result = main(["0 14 * * *", "--timezone", "UTC", "--next", "1"])

            output = f.getvalue()
            assert result == 0
            assert "Using timezone: UTC" in output
            assert "Next 1 run:" in output
            # Should show 14:00 UTC

    def test_timezone_with_previous_runs(self):
        """Test timezone affects previous run calculations."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "US/Pacific", "--previous", "1"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: US/Pacific" in output
        assert "Previous 1 run" in output

    def test_list_timezones_flag(self):
        """Test --list-timezones flag."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["--list-timezones"])

        output = f.getvalue()
        assert result == 0
        assert "Available timezones:" in output
        assert "UTC" in output
        assert "US/Eastern" in output
        assert "Europe/London" in output
        assert "Total:" in output
        assert "timezones" in output

    def test_timezone_offset_display(self):
        """Test that timezone offset is displayed."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "US/Eastern"])

        output = f.getvalue()
        assert result == 0
        # Should show offset like (-05:00) or (-04:00) depending on DST
        assert "(-0" in output or "(+0" in output

    def test_timezone_abbreviation_display(self):
        """Test that timezone abbreviation is displayed."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "US/Eastern"])

        output = f.getvalue()
        assert result == 0
        # Should show EST or EDT
        assert "EST" in output or "EDT" in output

    def test_timezone_with_verbose(self):
        """Test timezone with verbose output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "Europe/Paris", "--verbose"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: Europe/Paris" in output
        assert "Minute field:" in output
        assert "Hour field:" in output

    def test_timezone_with_special_string(self):
        """Test timezone with special string."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@daily", "--timezone", "Asia/Shanghai", "--next", "2"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: Asia/Shanghai" in output
        assert "Valid cron expression: @daily" in output
        assert "Next 2 runs:" in output

    def test_timezone_affects_relative_time(self):
        """Test that timezone affects relative time display."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["* * * * *", "--timezone", "UTC", "--next", "1"])

        output = f.getvalue()
        assert result == 0
        # Should show relative time like "in X minutes"
        assert "in" in output.lower() or "minute" in output.lower()

    def test_timezone_with_complex_expression(self):
        """Test timezone with complex cron expression."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/15 9-17 * * MON-FRI", "--timezone", "US/Central", "--next", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: US/Central" in output
        assert "CST" in output or "CDT" in output

    def test_timezone_case_sensitive(self):
        """Test that timezone names are case-sensitive."""
        import io
        import contextlib

        # Try with wrong case
        f_err = io.StringIO()
        with contextlib.redirect_stderr(f_err):
            result = main(["0 0 * * *", "--timezone", "us/eastern"])

        error_output = f_err.getvalue()
        assert result == 1
        assert "Invalid timezone" in error_output

    def test_timezone_with_dst_transition(self):
        """Test timezone handling around DST transitions."""
        import io
        import contextlib

        # Use a date around DST transition (March for US)
        with patch('cronpal.timezone_utils.datetime') as mock_datetime:
            # Set to March 10, 2024 (around DST change)
            fixed_time = datetime(2024, 3, 10, 7, 0, 0)
            mock_datetime.now.return_value = fixed_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                result = main(["0 2 * * *", "--timezone", "US/Eastern", "--next", "1"])

            output = f.getvalue()
            assert result == 0
            # Should handle DST transition correctly

    def test_timezone_formatting_in_output(self):
        """Test that timezone is properly formatted in run times."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 12 * * *", "--timezone", "Australia/Sydney", "--next", "1"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: Australia/Sydney" in output
        # Should show AEDT or AEST
        assert "AEDT" in output or "AEST" in output
        # Should show offset
        assert "(+" in output

    def test_timezone_with_both_next_and_previous(self):
        """Test timezone with both next and previous runs."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "Europe/Berlin",
                          "--next", "1", "--previous", "1"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: Europe/Berlin" in output
        assert "Next 1 run:" in output
        assert "Previous 1 run" in output
        assert "CET" in output or "CEST" in output

    def test_timezone_with_yearly_expression(self):
        """Test timezone with yearly cron expression."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@yearly", "--timezone", "Pacific/Auckland", "--next", "2"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: Pacific/Auckland" in output
        assert "NZDT" in output or "NZST" in output
        # Should show January 1st in Auckland timezone

    def test_timezone_display_consistency(self):
        """Test that timezone display is consistent throughout output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "US/Mountain",
                          "--next", "2", "--verbose"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone: US/Mountain" in output
        # All times should show Mountain time zone
        assert "MST" in output or "MDT" in output
        # Offset should be consistent
        assert "(-07:00)" in output or "(-06:00)" in output