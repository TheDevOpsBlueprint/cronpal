"""Tests for the cron scheduler previous run functionality."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

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


class TestCronSchedulerPrevious:
    """Tests for CronScheduler previous run methods."""

    def test_every_minute_previous(self):
        """Test previous run for every minute."""
        expr = create_cron_expression("* * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 30, 0)
        prev_run = scheduler.get_previous_run(start)

        # Should be the same time (already on a minute boundary)
        assert prev_run == start

    def test_every_minute_with_seconds_previous(self):
        """Test every minute with seconds in start time."""
        expr = create_cron_expression("* * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 30, 45)
        prev_run = scheduler.get_previous_run(start)

        # Should round down to same minute
        assert prev_run == datetime(2024, 1, 15, 10, 30, 0)

    def test_specific_minute_previous(self):
        """Test specific minute of every hour."""
        expr = create_cron_expression("15 * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 30, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2024, 1, 15, 10, 15, 0)

    def test_specific_minute_previous_hour(self):
        """Test specific minute when current minute is before."""
        expr = create_cron_expression("30 * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 15, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2024, 1, 15, 9, 30, 0)

    def test_specific_hour_previous(self):
        """Test specific hour of every day."""
        expr = create_cron_expression("0 14 * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 16, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2024, 1, 15, 14, 0, 0)

    def test_specific_hour_previous_day(self):
        """Test specific hour when current hour is before."""
        expr = create_cron_expression("0 18 * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2024, 1, 14, 18, 0, 0)

    def test_specific_day_of_month_previous(self):
        """Test specific day of month."""
        expr = create_cron_expression("0 0 15 * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 20, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2024, 1, 15, 0, 0, 0)

    def test_specific_day_of_month_previous_month(self):
        """Test specific day when current day is before."""
        expr = create_cron_expression("0 0 20 * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 2, 10, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2024, 1, 20, 0, 0, 0)

    def test_specific_month_previous(self):
        """Test specific month."""
        expr = create_cron_expression("0 0 1 6 *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 8, 1, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2024, 6, 1, 0, 0, 0)

    def test_specific_month_previous_year(self):
        """Test specific month when current month is before."""
        expr = create_cron_expression("0 0 1 8 *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 6, 1, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2023, 8, 1, 0, 0, 0)

    def test_specific_weekday_previous(self):
        """Test specific day of week (Monday)."""
        expr = create_cron_expression("0 0 * * 1")
        scheduler = CronScheduler(expr)

        # Start on Tuesday, January 16, 2024
        start = datetime(2024, 1, 16, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        # Previous Monday is January 15
        assert prev_run == datetime(2024, 1, 15, 0, 0, 0)
        assert prev_run.weekday() == 0  # Monday in Python

    def test_weekday_and_monthday_previous(self):
        """Test expression with both day of month and day of week."""
        # Run on 15th OR Mondays (OR logic)
        expr = create_cron_expression("0 0 15 * 1")
        scheduler = CronScheduler(expr)

        # Start on January 16 (Tuesday)
        start = datetime(2024, 1, 16, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        # Previous should be January 15 (Monday) - matches both
        assert prev_run == datetime(2024, 1, 15, 0, 0, 0)

    def test_every_15_minutes_previous(self):
        """Test every 15 minutes."""
        expr = create_cron_expression("*/15 * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 20, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2024, 1, 15, 10, 15, 0)

    def test_business_hours_previous(self):
        """Test business hours (9-17 on weekdays)."""
        expr = create_cron_expression("0 9-17 * * 1-5")
        scheduler = CronScheduler(expr)

        # Start Friday afternoon
        start = datetime(2024, 1, 12, 16, 30, 0)  # Friday
        prev_run = scheduler.get_previous_run(start)

        # Previous is 4 PM same day
        assert prev_run == datetime(2024, 1, 12, 16, 0, 0)

    def test_business_hours_weekend_skip_previous(self):
        """Test business hours skipping weekend."""
        expr = create_cron_expression("0 17 * * 1-5")
        scheduler = CronScheduler(expr)

        # Start Monday morning
        start = datetime(2024, 1, 15, 8, 0, 0)  # Monday morning
        prev_run = scheduler.get_previous_run(start)

        # Previous is Friday evening
        assert prev_run == datetime(2024, 1, 12, 17, 0, 0)
        assert prev_run.weekday() == 4  # Friday

    def test_last_day_of_month_previous(self):
        """Test handling of last day of month."""
        expr = create_cron_expression("0 0 31 * *")
        scheduler = CronScheduler(expr)

        # Start in April (no 31st)
        start = datetime(2024, 4, 1, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        # Should be March 31
        assert prev_run == datetime(2024, 3, 31, 0, 0, 0)

    def test_february_29_previous(self):
        """Test February 29 in leap year."""
        expr = create_cron_expression("0 0 29 2 *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 3, 1, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        # 2024 is a leap year
        assert prev_run == datetime(2024, 2, 29, 0, 0, 0)

    def test_february_29_non_leap_year_previous(self):
        """Test February 29 in non-leap year."""
        expr = create_cron_expression("0 0 29 2 *")
        scheduler = CronScheduler(expr)

        start = datetime(2023, 3, 1, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        # 2023 is not a leap year, go back to 2020
        assert prev_run == datetime(2020, 2, 29, 0, 0, 0)

    def test_complex_expression_previous(self):
        """Test complex expression with multiple constraints."""
        expr = create_cron_expression("30 2 1-15 * MON-FRI")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 16, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        # Should find a weekday in first half of month
        assert prev_run.day <= 15
        assert prev_run.hour == 2
        assert prev_run.minute == 30
        assert prev_run.weekday() < 5  # Monday-Friday

    def test_range_with_step_previous(self):
        """Test range with step values."""
        expr = create_cron_expression("0 */4 * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 30, 0)
        prev_run = scheduler.get_previous_run(start)

        # Previous 4-hour interval is 8:00
        assert prev_run == datetime(2024, 1, 15, 8, 0, 0)

    def test_list_of_values_previous(self):
        """Test list of specific values."""
        expr = create_cron_expression("0 9,12,15 * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 14, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        assert prev_run == datetime(2024, 1, 15, 12, 0, 0)

    def test_get_previous_runs_multiple(self):
        """Test getting multiple previous runs."""
        expr = create_cron_expression("0 0 * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 0, 0)
        prev_runs = scheduler.get_previous_runs(3, start)

        assert len(prev_runs) == 3
        # Should be today at midnight, yesterday, day before
        assert prev_runs[0] == datetime(2024, 1, 15, 0, 0, 0)
        assert prev_runs[1] == datetime(2024, 1, 14, 0, 0, 0)
        assert prev_runs[2] == datetime(2024, 1, 13, 0, 0, 0)

    def test_get_previous_runs_hourly(self):
        """Test getting multiple previous runs for hourly schedule."""
        expr = create_cron_expression("30 * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 45, 0)
        prev_runs = scheduler.get_previous_runs(3, start)

        assert len(prev_runs) == 3
        assert prev_runs[0] == datetime(2024, 1, 15, 10, 30, 0)
        assert prev_runs[1] == datetime(2024, 1, 15, 9, 30, 0)
        assert prev_runs[2] == datetime(2024, 1, 15, 8, 30, 0)

    def test_get_previous_runs_invalid_count(self):
        """Test get_previous_runs with invalid count."""
        expr = create_cron_expression("0 0 * * *")
        scheduler = CronScheduler(expr)

        with pytest.raises(ValueError, match="Count must be at least 1"):
            scheduler.get_previous_runs(0)

        with pytest.raises(ValueError, match="Count must be at least 1"):
            scheduler.get_previous_runs(-1)

    def test_sunday_as_zero_previous(self):
        """Test Sunday as day 0."""
        expr = create_cron_expression("0 0 * * 0")
        scheduler = CronScheduler(expr)

        # Start on Monday
        start = datetime(2024, 1, 15, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        # Previous Sunday is January 14
        assert prev_run == datetime(2024, 1, 14, 0, 0, 0)
        assert prev_run.weekday() == 6  # Sunday in Python

    def test_sunday_as_seven_previous(self):
        """Test Sunday as day 7 (should be same as 0)."""
        expr = create_cron_expression("0 0 * * 7")
        scheduler = CronScheduler(expr)

        # Start on Monday
        start = datetime(2024, 1, 15, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        # Previous Sunday is January 14
        assert prev_run == datetime(2024, 1, 14, 0, 0, 0)
        assert prev_run.weekday() == 6  # Sunday in Python

    def test_minute_boundary_previous(self):
        """Test that previous run respects minute boundaries."""
        expr = create_cron_expression("15 10 * * *")
        scheduler = CronScheduler(expr)

        # Start just after the target time
        start = datetime(2024, 1, 15, 10, 15, 30)
        prev_run = scheduler.get_previous_run(start)

        # Should get the exact minute
        assert prev_run == datetime(2024, 1, 15, 10, 15, 0)

    def test_year_boundary_previous(self):
        """Test previous run crossing year boundary."""
        expr = create_cron_expression("0 0 31 12 *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 0, 0, 0)
        prev_run = scheduler.get_previous_run(start)

        # Should be December 31 of previous year
        assert prev_run == datetime(2023, 12, 31, 0, 0, 0)

    def test_monthly_on_specific_day_previous(self):
        """Test monthly schedule on specific day."""
        expr = create_cron_expression("0 0 15 * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 3, 10, 0, 0, 0)
        prev_runs = scheduler.get_previous_runs(3, start)

        assert len(prev_runs) == 3
        assert prev_runs[0] == datetime(2024, 2, 15, 0, 0, 0)
        assert prev_runs[1] == datetime(2024, 1, 15, 0, 0, 0)
        assert prev_runs[2] == datetime(2023, 12, 15, 0, 0, 0)