"""Tests for CLI color output functionality."""

import subprocess
import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.cli import main
from cronpal.color_utils import ColorConfig, set_color_config


class TestCLIColorOutput:
    """Tests for CLI colored output functionality."""

    def setup_method(self):
        """Setup for each test."""
        # Ensure colors are disabled for consistent testing
        set_color_config(ColorConfig(use_colors=False))

    def test_no_color_flag(self):
        """Test --no-color flag disables colors."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--no-color"])

        output = f.getvalue()
        assert result == 0
        # Should not contain ANSI escape codes
        assert "\033[" not in output
        assert "✓ Valid cron expression" in output

    def test_colored_success_message(self):
        """Test colored success message."""
        import io
        import contextlib

        # Enable colors for this test
        set_color_config(ColorConfig(use_colors=True))

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *"])

        output = f.getvalue()
        assert result == 0
        assert "✓ Valid cron expression" in output

    def test_colored_error_message(self):
        """Test colored error message."""
        import io
        import contextlib

        f_err = io.StringIO()
        with contextlib.redirect_stderr(f_err):
            result = main(["invalid", "--no-color"])

        error_output = f_err.getvalue()
        assert result == 1
        assert "✗" in error_output
        # Should not contain ANSI codes with --no-color
        assert "\033[" not in error_output

    def test_colored_verbose_output(self):
        """Test colored verbose output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--verbose", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Minute field:" in output
        assert "Hour field:" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_colored_pretty_print(self):
        """Test colored pretty print output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--pretty", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Cron Expression Analysis" in output
        assert "Summary:" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_colored_next_runs(self):
        """Test colored next runs output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--next", "3", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Next 3 runs:" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_colored_previous_runs(self):
        """Test colored previous runs output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--previous", "3", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Previous 3 runs" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_colored_timezone_output(self):
        """Test colored timezone output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--timezone", "UTC", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Using timezone:" in output
        assert "UTC" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_colored_list_timezones(self):
        """Test colored list timezones output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["--list-timezones", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Available timezones:" in output
        assert "Total:" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_colored_version_output(self):
        """Test colored version output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["--version", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "cronpal" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_colored_special_string(self):
        """Test colored output for special string."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@daily", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "✓ Valid cron expression: @daily" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_colored_special_string_verbose(self):
        """Test colored verbose output for special string."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@hourly", "--verbose", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Special string:" in output
        assert "Description:" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_pretty_print_table_colors(self):
        """Test that pretty print table uses colors correctly."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/15 9-17 * * MON-FRI", "--pretty", "--no-color"])

        output = f.getvalue()
        assert result == 0
        # Check table elements are present
        assert "┌" in output
        assert "│" in output
        assert "└" in output
        assert "Field" in output
        assert "Value" in output
        assert "Description" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_error_suggestion_colors(self):
        """Test that error suggestions use colors correctly."""
        import io
        import contextlib

        f_err = io.StringIO()
        with contextlib.redirect_stderr(f_err):
            result = main(["0 0 *", "--no-color"])

        error_output = f_err.getvalue()
        assert result == 1
        assert "💡 Suggestion:" in error_output
        # No ANSI codes
        assert "\033[" not in error_output

    def test_month_names_colored_output(self):
        """Test month names in colored output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 1 JAN,JUN,DEC *", "--verbose", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Month field: JAN,JUN,DEC" in output
        assert "Months:" in output
        assert "Jan" in output or "Jun" in output or "Dec" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_day_names_colored_output(self):
        """Test day names in colored output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * MON-FRI", "--verbose", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Day of week field: MON-FRI" in output
        assert "Days:" in output
        # No ANSI codes
        assert "\033[" not in output

    def test_relative_time_colored_output(self):
        """Test relative time in colored output."""
        import io
        import contextlib

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["* * * * *", "--next", "1", "--no-color"])

        output = f.getvalue()
        assert result == 0
        assert "Next 1 run:" in output
        # Should have relative time like "in X minutes"
        assert "in" in output.lower() or "minute" in output.lower()
        # No ANSI codes
        assert "\033[" not in output