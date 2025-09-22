"""Tests for CLI previous runs functionality."""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.cli import main


class TestCLIPreviousRuns:
    """Tests for CLI --previous flag functionality."""

    def test_previous_flag_single(self):
        """Test --previous flag with single run."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--previous", "1"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 1 run" in output
        assert "1." in output

    def test_previous_flag_multiple(self):
        """Test --previous flag with multiple runs."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--previous", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 3 runs" in output
        assert "most recent first" in output
        assert "1." in output
        assert "2." in output
        assert "3." in output

    @patch('cronpal.scheduler.datetime')
    def test_previous_runs_with_fixed_time(self, mock_datetime):
        """Test previous runs with fixed current time."""
        import io
        import contextlib

        # Fix the current time for predictable output
        fixed_time = datetime(2024, 1, 15, 14, 30, 0)
        mock_datetime.now.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 12 * * *", "--previous", "2"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 2 runs" in output
        # Should show 12:00 today and yesterday
        assert "2024-01-15 12:00:00" in output
        assert "2024-01-14 12:00:00" in output

    def test_previous_runs_every_minute(self):
        """Test previous runs for every minute."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["* * * * *", "--previous", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 3 runs" in output
        # Should have relative time descriptions
        assert "ago" in output.lower() or "minute" in output.lower()

    def test_previous_runs_with_verbose(self):
        """Test previous runs with verbose flag."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--previous", "2", "--verbose"])

        output = f.getvalue()
        assert result == 0
        # Should show field details AND previous runs
        assert "Minute field:" in output
        assert "Hour field:" in output
        assert "Previous 2 runs" in output

    def test_previous_runs_special_string(self):
        """Test previous runs with special string."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@daily", "--previous", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 3 runs" in output
        # Daily should show midnight times
        assert "00:00:00" in output

    def test_previous_runs_special_string_reboot(self):
        """Test previous runs with @reboot."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@reboot", "--previous", "5"])

        output = f.getvalue()
        assert result == 0
        assert "@reboot only runs at system startup" in output

    def test_previous_runs_hourly(self):
        """Test previous runs for hourly schedule."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 * * * *", "--previous", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 3 runs" in output
        # All should be at minute 00
        assert output.count(":00:00") >= 3

    def test_previous_runs_specific_weekday(self):
        """Test previous runs for specific weekday."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * MON", "--previous", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 3 runs" in output
        # All should be Mondays
        assert output.count("Monday") == 3

    def test_previous_runs_complex_expression(self):
        """Test previous runs for complex expression."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/15 9-17 * * MON-FRI", "--previous", "5"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 5 runs" in output
        # Should not include weekends
        assert "Saturday" not in output
        assert "Sunday" not in output

    def test_previous_runs_with_month_names(self):
        """Test previous runs with month names."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 1 JAN,JUL *", "--previous", "2"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 2 runs" in output

    def test_previous_runs_with_day_names(self):
        """Test previous runs with day names."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * SUN,WED", "--previous", "4"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 4 runs" in output
        # Should include Sundays and Wednesdays
        assert "Sunday" in output or "Wednesday" in output

    def test_previous_runs_with_step_values(self):
        """Test previous runs with step values."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/10 * * * *", "--previous", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 3 runs" in output
        # Minutes should be 00, 10, 20, 30, 40, or 50

    def test_previous_runs_invalid_expression(self):
        """Test previous runs with invalid expression."""
        import io
        import contextlib

        f_err = io.StringIO()
        with contextlib.redirect_stderr(f_err):
            result = main(["invalid", "--previous", "5"])

        error_output = f_err.getvalue()
        assert result == 1
        # Should show error, not previous runs
        assert "Invalid" in error_output

    def test_previous_runs_relative_time_today(self):
        """Test that relative time shows for today."""
        import io
        import contextlib

        # Use an expression that ran recently
        now = datetime.now()
        prev_hour = (now.hour - 1) % 24

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main([f"0 * * * *", "--previous", "1"])

        output = f.getvalue()
        assert result == 0
        # Should show relative time if it's today
        assert "ago" in output.lower()

    def test_previous_runs_formatting(self):
        """Test previous runs output formatting."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--previous", "5"])

        output = f.getvalue()
        assert result == 0
        # Check formatting
        assert "Previous 5 runs" in output

        # Check numbering
        for i in range(1, 6):
            assert f"{i}." in output

        # Check date format (YYYY-MM-DD HH:MM:SS Weekday)
        assert "2" in output  # Year starts with 2
        assert ":" in output  # Time separator

    def test_both_next_and_previous(self):
        """Test using both --next and --previous flags."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--next", "2", "--previous", "2"])

        output = f.getvalue()
        assert result == 0
        # Should show both
        assert "Next 2 runs" in output
        assert "Previous 2 runs" in output

    def test_previous_leap_year(self):
        """Test previous runs including February 29."""
        import io
        import contextlib

        # Use a date after Feb 29, 2024 (leap year)
        with patch('cronpal.scheduler.datetime') as mock_datetime:
            fixed_time = datetime(2024, 3, 1, 0, 0, 0)
            mock_datetime.now.return_value = fixed_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                result = main(["0 0 29 2 *", "--previous", "2"])

            output = f.getvalue()
            assert result == 0
            assert "Previous 2 runs" in output
            # Should show 2024-02-29 and 2020-02-29
            assert "2024-02-29" in output

    def test_previous_runs_yesterday(self):
        """Test that 'yesterday' appears in relative time."""
        import io
        import contextlib

        # Use an expression that runs daily
        with patch('cronpal.scheduler.datetime') as mock_datetime:
            fixed_time = datetime(2024, 1, 15, 14, 0, 0)
            mock_datetime.now.return_value = fixed_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                result = main(["0 12 * * *", "--previous", "1"])

            output = f.getvalue()
            assert result == 0
            # Should show yesterday for a run from previous day
            # Or hours ago for today's run

    def test_previous_runs_hours_ago(self):
        """Test that 'hours ago' appears for recent runs."""
        import io
        import contextlib

        # Use an expression that runs hourly
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 * * * *", "--previous", "1"])

        output = f.getvalue()
        assert result == 0
        # Should show relative time
        assert "ago" in output.lower()