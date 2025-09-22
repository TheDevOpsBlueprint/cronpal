"""Tests for CLI next runs functionality."""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.cli import main


class TestCLINextRuns:
    """Tests for CLI --next flag functionality."""

    def test_next_flag_default(self):
        """Test --next flag with default value."""
        result = main(["0 0 * * *", "--next", "5"])
        assert result == 0

    def test_next_flag_single(self):
        """Test --next flag with single run."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--next", "1"])

        output = f.getvalue()
        assert result == 0
        assert "Next 1 run:" in output
        assert "1." in output

    def test_next_flag_multiple(self):
        """Test --next flag with multiple runs."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--next", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Next 3 runs:" in output
        assert "1." in output
        assert "2." in output
        assert "3." in output

    @patch('cronpal.scheduler.datetime')
    def test_next_runs_with_fixed_time(self, mock_datetime):
        """Test next runs with fixed current time."""
        import io
        import contextlib

        # Fix the current time for predictable output
        fixed_time = datetime(2024, 1, 15, 10, 30, 0)
        mock_datetime.now.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 12 * * *", "--next", "2"])

        output = f.getvalue()
        assert result == 0
        assert "Next 2 runs:" in output
        # Should show 12:00 today and tomorrow
        assert "2024-01-15 12:00:00" in output
        assert "2024-01-16 12:00:00" in output

    def test_next_runs_every_minute(self):
        """Test next runs for every minute."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["* * * * *", "--next", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Next 3 runs:" in output
        # Should have relative time descriptions
        assert "in" in output.lower() or "minute" in output.lower()

    def test_next_runs_with_verbose(self):
        """Test next runs with verbose flag."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--next", "2", "--verbose"])

        output = f.getvalue()
        assert result == 0
        # Should show field details AND next runs
        assert "Minute field:" in output
        assert "Hour field:" in output
        assert "Next 2 runs:" in output

    def test_next_runs_special_string(self):
        """Test next runs with special string."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@daily", "--next", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Next 3 runs:" in output
        # Daily should show midnight times
        assert "00:00:00" in output

    def test_next_runs_special_string_reboot(self):
        """Test next runs with @reboot."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@reboot", "--next", "5"])

        output = f.getvalue()
        assert result == 0
        assert "@reboot only runs at system startup" in output

    def test_next_runs_hourly(self):
        """Test next runs for hourly schedule."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 * * * *", "--next", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Next 3 runs:" in output
        # All should be at minute 00
        assert output.count(":00:00") >= 3

    def test_next_runs_specific_weekday(self):
        """Test next runs for specific weekday."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * MON", "--next", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Next 3 runs:" in output
        # All should be Mondays
        assert output.count("Monday") == 3

    def test_next_runs_complex_expression(self):
        """Test next runs for complex expression."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/15 9-17 * * MON-FRI", "--next", "5"])

        output = f.getvalue()
        assert result == 0
        assert "Next 5 runs:" in output
        # Should not include weekends
        assert "Saturday" not in output
        assert "Sunday" not in output

    def test_next_runs_with_month_names(self):
        """Test next runs with month names."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 1 JAN,JUL *", "--next", "2"])

        output = f.getvalue()
        assert result == 0
        assert "Next 2 runs:" in output
        # Should show January 1 and July 1

    def test_next_runs_with_day_names(self):
        """Test next runs with day names."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * SUN,WED", "--next", "4"])

        output = f.getvalue()
        assert result == 0
        assert "Next 4 runs:" in output
        # Should alternate between Sundays and Wednesdays
        assert "Sunday" in output
        assert "Wednesday" in output

    def test_next_runs_leap_year(self):
        """Test next runs including February 29."""
        import io
        import contextlib

        # Use a date before Feb 29, 2024 (leap year)
        with patch('cronpal.scheduler.datetime') as mock_datetime:
            fixed_time = datetime(2024, 2, 1, 0, 0, 0)
            mock_datetime.now.return_value = fixed_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                result = main(["0 0 29 2 *", "--next", "2"])

            output = f.getvalue()
            assert result == 0
            assert "Next 2 runs:" in output
            # Should show 2024-02-29 and 2028-02-29
            assert "2024-02-29" in output

    def test_next_runs_with_step_values(self):
        """Test next runs with step values."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/10 * * * *", "--next", "3"])

        output = f.getvalue()
        assert result == 0
        assert "Next 3 runs:" in output
        # Minutes should be 00, 10, 20, 30, 40, or 50

    def test_next_runs_invalid_expression(self):
        """Test next runs with invalid expression."""
        import io
        import contextlib

        f_err = io.StringIO()
        with contextlib.redirect_stderr(f_err):
            result = main(["invalid", "--next", "5"])

        error_output = f_err.getvalue()
        assert result == 1
        # Should show error, not next runs
        assert "Invalid" in error_output

    def test_next_runs_relative_time_today(self):
        """Test that relative time shows for today."""
        import io
        import contextlib

        # Use an expression that will run soon
        now = datetime.now()
        next_hour = (now.hour + 1) % 24

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main([f"0 {next_hour} * * *", "--next", "1"])

        output = f.getvalue()
        assert result == 0
        # Should show relative time if it's today
        if next_hour > now.hour:
            assert "in" in output.lower()

    def test_next_runs_formatting(self):
        """Test next runs output formatting."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--next", "5"])

        output = f.getvalue()
        assert result == 0
        # Check formatting
        assert "Next 5 runs:" in output

        # Check numbering
        for i in range(1, 6):
            assert f"{i}." in output

        # Check date format (YYYY-MM-DD HH:MM:SS Weekday)
        assert "2" in output  # Year starts with 2
        assert ":" in output  # Time separator