"""Tests for the cron scheduler."""

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


class TestCronScheduler:
    """Tests for CronScheduler class."""

    def test_initialization(self):
        """Test scheduler initialization."""
        expr = create_cron_expression("0 0 * * *")
        scheduler = CronScheduler(expr)
        assert scheduler.cron_expr == expr

    def test_initialization_invalid_expression(self):
        """Test scheduler with invalid expression."""
        expr = CronExpression("0 0 * * *")
        # Expression without parsed fields
        with pytest.raises(CronPalError, match="Invalid or incomplete"):
            CronScheduler(expr)

    def test_every_minute(self):
        """Test expression that runs every minute."""
        expr = create_cron_expression("* * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 30, 0)
        next_run = scheduler.get_next_run(start)

        # Should be the same time (already on a minute boundary)
        assert next_run == start

    def test_every_minute_with_seconds(self):
        """Test every minute with seconds in start time."""
        expr = create_cron_expression("* * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 30, 45)
        next_run = scheduler.get_next_run(start)

        # Should round up to next minute
        assert next_run == datetime(2024, 1, 15, 10, 31, 0)

    def test_specific_minute(self):
        """Test specific minute of every hour."""
        expr = create_cron_expression("15 * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 0, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2024, 1, 15, 10, 15, 0)

    def test_specific_minute_next_hour(self):
        """Test specific minute when current minute is past."""
        expr = create_cron_expression("15 * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 30, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2024, 1, 15, 11, 15, 0)

    def test_specific_hour(self):
        """Test specific hour of every day."""
        expr = create_cron_expression("0 14 * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 0, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2024, 1, 15, 14, 0, 0)

    def test_specific_hour_next_day(self):
        """Test specific hour when current hour is past."""
        expr = create_cron_expression("0 14 * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 16, 0, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2024, 1, 16, 14, 0, 0)

    def test_specific_day_of_month(self):
        """Test specific day of month."""
        expr = create_cron_expression("0 0 15 * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 1, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2024, 1, 15, 0, 0, 0)

    def test_specific_day_of_month_next_month(self):
        """Test specific day when current day is past."""
        expr = create_cron_expression("0 0 15 * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 20, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2024, 2, 15, 0, 0, 0)

    def test_specific_month(self):
        """Test specific month."""
        expr = create_cron_expression("0 0 1 6 *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 1, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2024, 6, 1, 0, 0, 0)

    def test_specific_month_next_year(self):
        """Test specific month when current month is past."""
        expr = create_cron_expression("0 0 1 6 *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 7, 1, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2025, 6, 1, 0, 0, 0)

    def test_specific_weekday(self):
        """Test specific day of week (Monday)."""
        expr = create_cron_expression("0 0 * * 1")
        scheduler = CronScheduler(expr)

        # Start on Sunday, January 14, 2024
        start = datetime(2024, 1, 14, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        # Next Monday is January 15
        assert next_run == datetime(2024, 1, 15, 0, 0, 0)
        assert next_run.weekday() == 0  # Monday in Python

    def test_weekday_and_monthday(self):
        """Test expression with both day of month and day of week."""
        # Run on 15th OR Mondays (OR logic)
        expr = create_cron_expression("0 0 15 * 1")
        scheduler = CronScheduler(expr)

        # Start on January 13 (Saturday)
        start = datetime(2024, 1, 13, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        # Next should be January 15 (Monday) - matches both
        assert next_run == datetime(2024, 1, 15, 0, 0, 0)

    def test_every_15_minutes(self):
        """Test every 15 minutes."""
        expr = create_cron_expression("*/15 * * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 5, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2024, 1, 15, 10, 15, 0)

    def test_business_hours(self):
        """Test business hours (9-17 on weekdays)."""
        expr = create_cron_expression("0 9-17 * * 1-5")
        scheduler = CronScheduler(expr)

        # Start Friday afternoon
        start = datetime(2024, 1, 12, 16, 30, 0)  # Friday
        next_run = scheduler.get_next_run(start)

        # Next is 5 PM same day
        assert next_run == datetime(2024, 1, 12, 17, 0, 0)

    def test_business_hours_weekend_skip(self):
        """Test business hours skipping weekend."""
        expr = create_cron_expression("0 9 * * 1-5")
        scheduler = CronScheduler(expr)

        # Start Friday after business hours
        start = datetime(2024, 1, 12, 18, 0, 0)  # Friday evening
        next_run = scheduler.get_next_run(start)

        # Next is Monday morning
        assert next_run == datetime(2024, 1, 15, 9, 0, 0)
        assert next_run.weekday() == 0  # Monday

    def test_last_day_of_month(self):
        """Test handling of last day of month."""
        expr = create_cron_expression("0 0 31 * *")
        scheduler = CronScheduler(expr)

        # Start in February (no 31st)
        start = datetime(2024, 2, 1, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        # Should skip to March 31
        assert next_run == datetime(2024, 3, 31, 0, 0, 0)

    def test_february_29(self):
        """Test February 29 in leap year."""
        expr = create_cron_expression("0 0 29 2 *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 1, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        # 2024 is a leap year
        assert next_run == datetime(2024, 2, 29, 0, 0, 0)

    def test_february_29_non_leap_year(self):
        """Test February 29 in non-leap year."""
        expr = create_cron_expression("0 0 29 2 *")
        scheduler = CronScheduler(expr)

        start = datetime(2023, 1, 1, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        # 2023 is not a leap year, skip to 2024
        assert next_run == datetime(2024, 2, 29, 0, 0, 0)

    def test_complex_expression(self):
        """Test complex expression with multiple constraints."""
        expr = create_cron_expression("30 2 1-15 * MON-FRI")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 1, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        # First occurrence is January 1 (Monday) at 2:30 AM
        assert next_run == datetime(2024, 1, 1, 2, 30, 0)

    def test_range_with_step(self):
        """Test range with step values."""
        expr = create_cron_expression("0 */4 * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 30, 0)
        next_run = scheduler.get_next_run(start)

        # Next 4-hour interval is 12:00
        assert next_run == datetime(2024, 1, 15, 12, 0, 0)

    def test_list_of_values(self):
        """Test list of specific values."""
        expr = create_cron_expression("0 9,12,15 * * *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 0, 0)
        next_run = scheduler.get_next_run(start)

        assert next_run == datetime(2024, 1, 15, 12, 0, 0)

    def test_current_time_matches(self):
        """Test when current time already matches."""
        expr = create_cron_expression("30 10 15 1 *")
        scheduler = CronScheduler(expr)

        start = datetime(2024, 1, 15, 10, 30, 0)
        next_run = scheduler.get_next_run(start)

        # Current time matches, so it should return the same time
        assert next_run == start

    def test_sunday_as_zero(self):
        """Test Sunday as day 0."""
        expr = create_cron_expression("0 0 * * 0")
        scheduler = CronScheduler(expr)

        # Start on Saturday
        start = datetime(2024, 1, 13, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        # Next Sunday is January 14
        assert next_run == datetime(2024, 1, 14, 0, 0, 0)
        assert next_run.weekday() == 6  # Sunday in Python

    def test_sunday_as_seven(self):
        """Test Sunday as day 7 (should be same as 0)."""
        expr = create_cron_expression("0 0 * * 7")
        scheduler = CronScheduler(expr)

        # Start on Saturday
        start = datetime(2024, 1, 13, 0, 0, 0)
        next_run = scheduler.get_next_run(start)

        # Next Sunday is January 14
        assert next_run == datetime(2024, 1, 14, 0, 0, 0)
        assert next_run.weekday() == 6  # Sunday in Python