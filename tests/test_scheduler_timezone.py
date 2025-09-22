"""Tests for scheduler timezone functionality."""

import sys
from datetime import datetime
from pathlib import Path

import pytest
import pytz

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.exceptions import CronPalError
from cronpal.field_parser import FieldParser
from cronpal.models import CronExpression
from cronpal.scheduler import CronScheduler


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


class TestCronSchedulerTimezone:
    """Tests for CronScheduler with timezone support."""

    def test_scheduler_with_utc(self):
        """Test scheduler with UTC timezone."""
        expr = create_cron_expression("0 0 * * *")
        scheduler = CronScheduler(expr, "UTC")

        assert scheduler.timezone == pytz.UTC

    def test_scheduler_with_us_eastern(self):
        """Test scheduler with US/Eastern timezone."""
        expr = create_cron_expression("0 0 * * *")
        scheduler = CronScheduler(expr, "US/Eastern")

        assert scheduler.timezone.zone == "US/Eastern"

    def test_scheduler_with_timezone_object(self):
        """Test scheduler with timezone object."""
        expr = create_cron_expression("0 0 * * *")
        tz = pytz.timezone("Europe/London")
        scheduler = CronScheduler(expr, tz)

        assert scheduler.timezone == tz

    def test_scheduler_without_timezone(self):
        """Test scheduler without timezone uses local."""
        expr = create_cron_expression("0 0 * * *")
        scheduler = CronScheduler(expr, None)

        assert scheduler.timezone is not None

    def test_next_run_with_timezone(self):
        """Test next run calculation with timezone."""
        expr = create_cron_expression("0 12 * * *")
        scheduler = CronScheduler(expr, "US/Eastern")

        # Start at 10 AM Eastern
        start = pytz.timezone("US/Eastern").localize(
            datetime(2024, 1, 15, 10, 0, 0)
        )
        next_run = scheduler.get_next_run(start)

        assert next_run.tzinfo.zone == "US/Eastern"
        assert next_run.hour == 12
        assert next_run.day == 15

    def test_next_run_timezone_conversion(self):
        """Test next run with timezone conversion."""
        expr = create_cron_expression("0 0 * * *")  # Midnight daily
        scheduler = CronScheduler(expr, "US/Eastern")

        # Start at 10 PM UTC (5 PM Eastern)
        start = pytz.UTC.localize(datetime(2024, 1, 15, 22, 0, 0))
        next_run = scheduler.get_next_run(start)

        # Should be midnight Eastern time
        assert next_run.tzinfo.zone == "US/Eastern"
        assert next_run.hour == 0
        assert next_run.day == 16  # Next day in Eastern

    def test_previous_run_with_timezone(self):
        """Test previous run calculation with timezone."""
        expr = create_cron_expression("0 12 * * *")
        scheduler = CronScheduler(expr, "Europe/London")

        # Start at 2 PM London time
        start = pytz.timezone("Europe/London").localize(
            datetime(2024, 1, 15, 14, 0, 0)
        )
        prev_run = scheduler.get_previous_run(start)

        assert prev_run.tzinfo.zone == "Europe/London"
        assert prev_run.hour == 12
        assert prev_run.day == 15

    def test_timezone_aware_datetime_input(self):
        """Test with timezone-aware datetime input."""
        expr = create_cron_expression("0 9 * * MON")
        scheduler = CronScheduler(expr, "Asia/Tokyo")

        # Start with UTC datetime
        start = pytz.UTC.localize(datetime(2024, 1, 16, 0, 0, 0))  # Tuesday UTC
        next_run = scheduler.get_next_run(start)

        # Should be next Monday at 9 AM Tokyo time
        assert next_run.tzinfo.zone == "Asia/Tokyo"
        assert next_run.hour == 9
        assert next_run.weekday() == 0  # Monday

    def test_naive_datetime_input(self):
        """Test with naive datetime input."""
        expr = create_cron_expression("30 14 * * *")
        scheduler = CronScheduler(expr, "US/Pacific")

        # Start with naive datetime (assumes scheduler's timezone)
        start = datetime(2024, 1, 15, 10, 0, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run.tzinfo.zone == "US/Pacific"
        assert next_run.hour == 14
        assert next_run.minute == 30

    def test_dst_transition_spring_forward(self):
        """Test handling of DST transition (spring forward)."""
        expr = create_cron_expression("0 2 * * *")  # 2 AM daily
        scheduler = CronScheduler(expr, "US/Eastern")

        # Start on March 9, 2024 (DST starts March 10)
        start = pytz.timezone("US/Eastern").localize(
            datetime(2024, 3, 9, 0, 0, 0)
        )

        runs = scheduler.get_next_runs(3, start)

        # March 9: 2 AM EST exists
        assert runs[0].day == 9
        assert runs[0].hour == 2

        # March 10: 2 AM doesn't exist (skips to 3 AM EDT)
        # Scheduler should handle this gracefully
        assert runs[1].day == 11  # Skips to March 11

        # March 11: 2 AM EDT exists
        assert runs[2].day == 12

    def test_dst_transition_fall_back(self):
        """Test handling of DST transition (fall back)."""
        expr = create_cron_expression("0 1 * * *")  # 1 AM daily
        scheduler = CronScheduler(expr, "US/Eastern")

        # Start on November 2, 2024 (DST ends November 3)
        start = pytz.timezone("US/Eastern").localize(
            datetime(2024, 11, 2, 0, 0, 0)
        )

        runs = scheduler.get_next_runs(3, start)

        # Should handle the repeated hour correctly
        assert runs[0].day == 2
        assert runs[1].day == 3
        assert runs[2].day == 4

    def test_multiple_timezones_comparison(self):
        """Test same cron in different timezones."""
        expr = create_cron_expression("0 12 * * *")  # Noon daily

        # Create schedulers for different timezones
        scheduler_utc = CronScheduler(expr, "UTC")
        scheduler_eastern = CronScheduler(expr, "US/Eastern")
        scheduler_tokyo = CronScheduler(expr, "Asia/Tokyo")

        # Same starting point in UTC
        start = pytz.UTC.localize(datetime(2024, 1, 15, 0, 0, 0))

        # Get next runs
        run_utc = scheduler_utc.get_next_run(start)
        run_eastern = scheduler_eastern.get_next_run(start)
        run_tokyo = scheduler_tokyo.get_next_run(start)

        # All should be at noon in their respective timezones
        assert run_utc.hour == 12
        assert run_eastern.hour == 12
        assert run_tokyo.hour == 12

        # But different when converted to UTC
        run_eastern_utc = run_eastern.astimezone(pytz.UTC)
        run_tokyo_utc = run_tokyo.astimezone(pytz.UTC)

        assert run_eastern_utc.hour == 17  # 12 PM EST = 5 PM UTC
        assert run_tokyo_utc.hour == 3  # 12 PM JST = 3 AM UTC

    def test_get_next_runs_with_timezone(self):
        """Test getting multiple next runs with timezone."""
        expr = create_cron_expression("0 */6 * * *")  # Every 6 hours
        scheduler = CronScheduler(expr, "Australia/Sydney")

        start = pytz.timezone("Australia/Sydney").localize(
            datetime(2024, 1, 15, 3, 0, 0)
        )

        runs = scheduler.get_next_runs(4, start)

        assert len(runs) == 4
        assert all(r.tzinfo.zone == "Australia/Sydney" for r in runs)
        assert runs[0].hour == 6
        assert runs[1].hour == 12
        assert runs[2].hour == 18
        assert runs[3].hour == 0  # Next day

    def test_get_previous_runs_with_timezone(self):
        """Test getting multiple previous runs with timezone."""
        expr = create_cron_expression("30 */4 * * *")  # Every 4 hours at 30 minutes
        scheduler = CronScheduler(expr, "Europe/Paris")

        start = pytz.timezone("Europe/Paris").localize(
            datetime(2024, 1, 15, 10, 0, 0)
        )

        runs = scheduler.get_previous_runs(3, start)

        assert len(runs) == 3
        assert all(r.tzinfo.zone == "Europe/Paris" for r in runs)
        assert all(r.minute == 30 for r in runs)
        assert runs[0].hour == 8
        assert runs[1].hour == 4
        assert runs[2].hour == 0

    def test_weekday_calculation_with_timezone(self):
        """Test that weekday calculations work correctly with timezones."""
        expr = create_cron_expression("0 0 * * MON")  # Midnight on Mondays
        scheduler = CronScheduler(expr, "Pacific/Auckland")

        # Start on Sunday in Auckland (still Saturday in some places)
        start = pytz.timezone("Pacific/Auckland").localize(
            datetime(2024, 1, 14, 12, 0, 0)  # Sunday noon
        )

        next_run = scheduler.get_next_run(start)

        # Should be Monday midnight Auckland time
        assert next_run.weekday() == 0  # Monday
        assert next_run.hour == 0
        assert next_run.tzinfo.zone == "Pacific/Auckland"

    def test_month_boundary_with_timezone(self):
        """Test month boundary handling with timezone."""
        expr = create_cron_expression("0 0 1 * *")  # First of month at midnight
        scheduler = CronScheduler(expr, "US/Hawaii")

        # Start at end of January
        start = pytz.timezone("US/Hawaii").localize(
            datetime(2024, 1, 31, 12, 0, 0)
        )

        next_run = scheduler.get_next_run(start)

        assert next_run.month == 2
        assert next_run.day == 1
        assert next_run.hour == 0
        assert next_run.tzinfo.zone == "US/Hawaii"

    def test_leap_year_with_timezone(self):
        """Test leap year handling with timezone."""
        expr = create_cron_expression("0 0 29 2 *")  # Feb 29
        scheduler = CronScheduler(expr, "Europe/Rome")

        # Start in January 2024 (leap year)
        start = pytz.timezone("Europe/Rome").localize(
            datetime(2024, 1, 1, 0, 0, 0)
        )

        next_run = scheduler.get_next_run(start)

        assert next_run.year == 2024
        assert next_run.month == 2
        assert next_run.day == 29
        assert next_run.tzinfo.zone == "Europe/Rome"

    def test_timezone_offset_changes(self):
        """Test that timezone offset changes are handled."""
        expr = create_cron_expression("0 12 * * *")  # Noon daily
        scheduler = CronScheduler(expr, "US/Eastern")

        # Get runs across DST change
        start = pytz.timezone("US/Eastern").localize(
            datetime(2024, 3, 9, 0, 0, 0)
        )

        runs = scheduler.get_next_runs(3, start)

        # Convert to UTC to check offset changes
        run1_utc = runs[0].astimezone(pytz.UTC)
        run2_utc = runs[1].astimezone(pytz.UTC)  # After DST starts
        run3_utc = runs[2].astimezone(pytz.UTC)

        # Before DST: 12 PM EST = 5 PM UTC
        assert run1_utc.hour == 17

        # After DST: 12 PM EDT = 4 PM UTC
        assert run2_utc.hour == 16
        assert run3_utc.hour == 16