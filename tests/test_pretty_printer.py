"""Tests for pretty printer functionality."""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.field_parser import FieldParser
from cronpal.models import CronExpression
from cronpal.pretty_printer import PrettyPrinter


def create_cron_expression(expr_str: str) -> CronExpression:
    """Helper to create a parsed CronExpression."""
    fields = expr_str.split()
    expr = CronExpression(expr_str)
    parser = FieldParser()

    expr.minute = parser.parse_minute(fields[0])
    expr.hour = parser.parse_hour(fields[1])
    expr.day_of_month = parser.parse_day_of_month(fields[2])
    expr.month = parser.parse_month(fields[3])
    expr.day_of_week = parser.parse_day_of_week(fields[4])

    return expr


class TestPrettyPrinterTable:
    """Tests for table printing functionality."""

    def test_print_table_basic(self):
        """Test basic table printing."""
        expr = create_cron_expression("0 0 * * *")
        printer = PrettyPrinter(expr)

        result = printer.print_table()

        assert "Cron Expression Analysis" in result
        assert "Expression: 0 0 * * *" in result
        assert "Field" in result
        assert "Value" in result
        assert "Description" in result
        assert "Minute" in result
        assert "Hour" in result
        assert "Day of Month" in result
        assert "Month" in result
        assert "Day of Week" in result

    def test_print_table_with_ranges(self):
        """Test table printing with ranges."""
        expr = create_cron_expression("0 9-17 * * *")
        printer = PrettyPrinter(expr)

        result = printer.print_table()

        assert "9-17" in result
        assert "From 9 to 17" in result

    def test_print_table_with_lists(self):
        """Test table printing with lists."""
        expr = create_cron_expression("0,15,30,45 * * * *")
        printer = PrettyPrinter(expr)

        result = printer.print_table()

        assert "0,15,30,45" in result
        assert "At minutes 0, 15, 30, 45" in result

    def test_print_table_with_steps(self):
        """Test table printing with step values."""
        expr = create_cron_expression("*/15 * * * *")
        printer = PrettyPrinter(expr)

        result = printer.print_table()

        assert "*/15" in result
        assert "Every 15 minutes" in result

    def test_print_table_with_names(self):
        """Test table printing with month and day names."""
        expr = create_cron_expression("0 0 1 JAN MON")
        printer = PrettyPrinter(expr)

        result = printer.print_table()

        assert "JAN" in result
        assert "January" in result
        assert "MON" in result
        assert "Monday" in result


class TestPrettyPrinterSimple:
    """Tests for simple printing functionality."""

    def test_print_simple_basic(self):
        """Test simple printing."""
        expr = create_cron_expression("0 0 * * *")
        printer = PrettyPrinter(expr)

        result = printer.print_simple()

        assert "Cron Expression: 0 0 * * *" in result
        assert "Minute:" in result
        assert "Hour:" in result
        assert "Day of Month:" in result
        assert "Month:" in result
        assert "Day of Week:" in result

    def test_print_simple_with_descriptions(self):
        """Test simple printing includes descriptions."""
        expr = create_cron_expression("*/5 * * * *")
        printer = PrettyPrinter(expr)

        result = printer.print_simple()

        assert "*/5" in result
        assert "Every 5 minutes" in result

    def test_print_simple_formatting(self):
        """Test simple printing formatting."""
        expr = create_cron_expression("30 2 15 6 3")
        printer = PrettyPrinter(expr)

        result = printer.print_simple()

        lines = result.split("\n")
        assert len(lines) >= 6  # Header + separator + 5 fields
        assert "-" * 50 in result


class TestPrettyPrinterDetailed:
    """Tests for detailed printing functionality."""

    def test_print_detailed_basic(self):
        """Test detailed printing."""
        expr = create_cron_expression("0 0 * * *")
        printer = PrettyPrinter(expr)

        result = printer.print_detailed()

        assert "CRON EXPRESSION: 0 0 * * *" in result
        assert "MINUTE" in result
        assert "HOUR" in result
        assert "DAY OF MONTH" in result
        assert "MONTH" in result
        assert "DAY OF WEEK" in result
        assert "Raw Value:" in result
        assert "Range:" in result
        assert "Description:" in result

    def test_print_detailed_with_values(self):
        """Test detailed printing with parsed values."""
        expr = create_cron_expression("0,30 9-17 * * MON-FRI")
        printer = PrettyPrinter(expr)

        result = printer.print_detailed()

        assert "Values:" in result
        assert "0, 30" in result
        assert "9, 10, 11, 12, 13, 14, 15, 16, 17" in result
        assert "1 (Monday), 2 (Tuesday)" in result

    def test_print_detailed_formatting(self):
        """Test detailed printing formatting."""
        expr = create_cron_expression("0 0 1 1 *")
        printer = PrettyPrinter(expr)

        result = printer.print_detailed()

        assert "═" * 80 in result
        assert "▸" in result
        assert "─" * 76 in result


class TestPrettyPrinterSummary:
    """Tests for summary generation functionality."""

    def test_get_summary_every_minute(self):
        """Test summary for every minute."""
        expr = create_cron_expression("* * * * *")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs every minute"

    def test_get_summary_hourly(self):
        """Test summary for hourly."""
        expr = create_cron_expression("0 * * * *")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs every hour at minute 00"

    def test_get_summary_daily(self):
        """Test summary for daily."""
        expr = create_cron_expression("0 0 * * *")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs daily at 00:00"

    def test_get_summary_daily_specific_time(self):
        """Test summary for daily at specific time."""
        expr = create_cron_expression("30 14 * * *")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs daily at 14:30"

    def test_get_summary_weekly(self):
        """Test summary for weekly."""
        expr = create_cron_expression("0 0 * * 0")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs every Sunday at 00:00"

    def test_get_summary_weekly_specific(self):
        """Test summary for weekly on specific day."""
        expr = create_cron_expression("30 9 * * 1")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs every Monday at 09:30"

    def test_get_summary_monthly(self):
        """Test summary for monthly."""
        expr = create_cron_expression("0 0 1 * *")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs on day 1 of every month at 00:00"

    def test_get_summary_monthly_specific_day(self):
        """Test summary for monthly on specific day."""
        expr = create_cron_expression("0 12 15 * *")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs on day 15 of every month at 12:00"

    def test_get_summary_yearly(self):
        """Test summary for yearly."""
        expr = create_cron_expression("0 0 1 1 *")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs on January 1 at 00:00"

    def test_get_summary_yearly_specific(self):
        """Test summary for yearly on specific date."""
        expr = create_cron_expression("30 23 31 12 *")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert result == "Runs on December 31 at 23:30"

    def test_get_summary_complex(self):
        """Test summary for complex expression."""
        expr = create_cron_expression("*/15 9-17 * * MON-FRI")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert "Complex schedule" in result or "selected" in result

    def test_get_summary_with_lists(self):
        """Test summary with list values."""
        expr = create_cron_expression("0 0 1,15 * *")
        printer = PrettyPrinter(expr)

        result = printer.get_summary()

        assert "at 00:00" in result
        assert "days 1, 15" in result


class TestPrettyPrinterHelpers:
    """Tests for helper functions."""

    def test_is_range(self):
        """Test range detection."""
        expr = create_cron_expression("0 9-17 * * *")
        printer = PrettyPrinter(expr)

        # 9-17 should be detected as a range
        hour_values = expr.hour.parsed_values
        assert printer._is_range(hour_values) is True

        # Non-continuous values should not be a range
        assert printer._is_range({1, 3, 5}) is False
        assert printer._is_range({1}) is False

    def test_is_step(self):
        """Test step pattern detection."""
        expr = create_cron_expression("*/15 * * * *")
        printer = PrettyPrinter(expr)

        # Every 15 minutes should be detected as a step
        minute_values = expr.minute.parsed_values
        assert printer._is_step(minute_values, 0, 59) is True

        # Non-step pattern
        assert printer._is_step({1, 2, 4}, 0, 59) is False

    def test_get_step_value(self):
        """Test getting step value."""
        expr = create_cron_expression("*/10 * * * *")
        printer = PrettyPrinter(expr)

        minute_values = expr.minute.parsed_values
        assert printer._get_step_value(minute_values) == 10

    def test_get_month_name(self):
        """Test month name conversion."""
        expr = create_cron_expression("0 0 1 6 *")
        printer = PrettyPrinter(expr)

        assert printer._get_month_name(1) == "January"
        assert printer._get_month_name(6) == "June"
        assert printer._get_month_name(12) == "December"
        assert printer._get_month_name(13) == "13"  # Invalid month

    def test_get_weekday_name(self):
        """Test weekday name conversion."""
        expr = create_cron_expression("0 0 * * 1")
        printer = PrettyPrinter(expr)

        assert printer._get_weekday_name(0) == "Sunday"
        assert printer._get_weekday_name(1) == "Monday"
        assert printer._get_weekday_name(6) == "Saturday"
        assert printer._get_weekday_name(7) == "7"  # Invalid day

    def test_format_value_list_short(self):
        """Test formatting short value lists."""
        expr = create_cron_expression("0,15,30,45 * * * *")
        printer = PrettyPrinter(expr)

        from cronpal.models import FieldType

        result = printer._format_value_list({0, 15, 30, 45}, FieldType.MINUTE)
        assert "0, 15, 30, 45" in result

    def test_format_value_list_long(self):
        """Test formatting long value lists."""
        expr = create_cron_expression("* * * * *")
        printer = PrettyPrinter(expr)

        from cronpal.models import FieldType

        # Minutes has 60 values (0-59)
        minute_values = expr.minute.parsed_values
        result = printer._format_value_list(minute_values, FieldType.MINUTE)

        assert "..." in result
        assert "60 values" in result

    def test_format_value_list_months(self):
        """Test formatting month value lists."""
        expr = create_cron_expression("0 0 1 1,6,12 *")
        printer = PrettyPrinter(expr)

        from cronpal.models import FieldType

        month_values = expr.month.parsed_values
        result = printer._format_value_list(month_values, FieldType.MONTH)

        assert "1 (January)" in result
        assert "6 (June)" in result
        assert "12 (December)" in result

    def test_format_value_list_weekdays(self):
        """Test formatting weekday value lists."""
        expr = create_cron_expression("0 0 * * MON-FRI")
        printer = PrettyPrinter(expr)

        from cronpal.models import FieldType

        weekday_values = expr.day_of_week.parsed_values
        result = printer._format_value_list(weekday_values, FieldType.DAY_OF_WEEK)

        assert "1 (Monday)" in result
        assert "5 (Friday)" in result


class TestPrettyPrinterCLI:
    """Tests for pretty printer CLI integration."""

    def test_cli_pretty_flag(self):
        """Test --pretty flag in CLI."""
        import io
        import contextlib
        from cronpal.cli import main

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["0 0 * * *", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Cron Expression Analysis" in output
        assert "Summary:" in output

    def test_cli_pretty_with_verbose(self):
        """Test --pretty with --verbose."""
        import io
        import contextlib
        from cronpal.cli import main

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/15 * * * *", "--pretty", "--verbose"])

        output = f.getvalue()
        assert result == 0
        assert "CRON EXPRESSION:" in output
        assert "Raw Value:" in output
        assert "Values:" in output

    def test_cli_pretty_with_special_string(self):
        """Test --pretty with special string."""
        import io
        import contextlib
        from cronpal.cli import main

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@daily", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Summary: Runs daily at 00:00" in output

    def test_cli_pretty_with_complex_expression(self):
        """Test --pretty with complex expression."""
        import io
        import contextlib
        from cronpal.cli import main

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["*/5 9-17 1,15 * MON-FRI", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "*/5" in output
        assert "9-17" in output
        assert "1,15" in output
        assert "MON-FRI" in output

    def test_cli_pretty_with_reboot(self):
        """Test --pretty with @reboot."""
        import io
        import contextlib
        from cronpal.cli import main

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = main(["@reboot", "--pretty"])

        output = f.getvalue()
        assert result == 0
        assert "Valid cron expression: @reboot" in output
        assert "runs at system startup" in output