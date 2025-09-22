"""Scheduler for calculating cron expression run times."""

from datetime import datetime, timedelta
from typing import Optional

from cronpal.exceptions import CronPalError
from cronpal.models import CronExpression
from cronpal.time_utils import (
    get_next_day,
    get_next_hour,
    get_next_minute,
    get_next_month,
    get_weekday,
    is_valid_day_in_month,
    round_to_next_minute,
)


class CronScheduler:
    """Calculator for cron expression run times."""

    def __init__(self, cron_expr: CronExpression):
        """
        Initialize the scheduler with a cron expression.

        Args:
            cron_expr: The CronExpression to calculate times for.
        """
        self.cron_expr = cron_expr
        self._validate_expression()

    def _validate_expression(self):
        """Validate that the expression has all required fields."""
        if not self.cron_expr.is_valid():
            raise CronPalError("Invalid or incomplete cron expression")

    def get_next_run(self, after: Optional[datetime] = None) -> datetime:
        """
        Calculate the next run time for the cron expression.

        Args:
            after: The datetime to start searching from.
                   Defaults to current time if not provided.

        Returns:
            The next datetime when the cron expression will run.
        """
        if after is None:
            after = datetime.now()

        # Round up to next minute if needed
        current = round_to_next_minute(after)

        # Maximum iterations to prevent infinite loops
        max_iterations = 10000
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            # Check if current time matches the cron expression
            if self._matches_time(current):
                return current

            # Move to next possible time
            current = self._advance_to_next_possible(current)

        raise CronPalError("Could not find next run time within reasonable limits")

    def _matches_time(self, dt: datetime) -> bool:
        """
        Check if a datetime matches the cron expression.

        Args:
            dt: The datetime to check.

        Returns:
            True if the datetime matches all cron fields.
        """
        # Check minute
        if dt.minute not in self.cron_expr.minute.parsed_values:
            return False

        # Check hour
        if dt.hour not in self.cron_expr.hour.parsed_values:
            return False

        # Check month
        if dt.month not in self.cron_expr.month.parsed_values:
            return False

        # Check day of month - but only if it's valid for this month
        if not is_valid_day_in_month(dt.year, dt.month, dt.day):
            return False

        # For day fields, we need to check if EITHER day of month OR day of week matches
        # This is the standard cron behavior
        day_of_month_match = dt.day in self.cron_expr.day_of_month.parsed_values
        day_of_week_match = get_weekday(dt) in self.cron_expr.day_of_week.parsed_values

        # If both day of month and day of week are restricted (not wildcards),
        # then we match if EITHER matches (OR logic)
        if not self.cron_expr.day_of_month.is_wildcard() and not self.cron_expr.day_of_week.is_wildcard():
            return day_of_month_match or day_of_week_match

        # Otherwise both must match
        return day_of_month_match and day_of_week_match

    def _advance_to_next_possible(self, dt: datetime) -> datetime:
        """
        Advance datetime to the next possible matching time.

        Args:
            dt: The current datetime.

        Returns:
            The next datetime that could potentially match.
        """
        # Try to advance minute first
        next_minute = self._get_next_minute(dt)
        if next_minute is not None:
            return next_minute

        # If no valid minute in this hour, try next hour
        next_hour = self._get_next_hour(dt)
        if next_hour is not None:
            return next_hour

        # If no valid hour today, try next day
        next_day = self._get_next_day(dt)
        if next_day is not None:
            return next_day

        # If no valid day this month, try next month
        return self._get_next_month(dt)

    def _get_next_minute(self, dt: datetime) -> Optional[datetime]:
        """
        Get the next valid minute after the current time.

        Args:
            dt: The current datetime.

        Returns:
            Next valid minute in the same hour, or None if no valid minute.
        """
        current_minute = dt.minute
        valid_minutes = sorted(self.cron_expr.minute.parsed_values)

        for minute in valid_minutes:
            if minute > current_minute:
                return dt.replace(minute=minute, second=0, microsecond=0)

        return None

    def _get_next_hour(self, dt: datetime) -> Optional[datetime]:
        """
        Get the next valid hour after the current time.

        Args:
            dt: The current datetime.

        Returns:
            Next valid hour in the same day, or None if no valid hour.
        """
        current_hour = dt.hour
        valid_hours = sorted(self.cron_expr.hour.parsed_values)
        valid_minutes = sorted(self.cron_expr.minute.parsed_values)

        # First minute of the next valid hour
        first_minute = valid_minutes[0] if valid_minutes else 0

        for hour in valid_hours:
            if hour > current_hour:
                return dt.replace(hour=hour, minute=first_minute, second=0, microsecond=0)

        return None

    def _get_next_day(self, dt: datetime) -> Optional[datetime]:
        """
        Get the next valid day after the current time.

        Args:
            dt: The current datetime.

        Returns:
            Next valid day in the same month, or None if no valid day.
        """
        current_day = dt.day
        valid_hours = sorted(self.cron_expr.hour.parsed_values)
        valid_minutes = sorted(self.cron_expr.minute.parsed_values)

        # First time of the day
        first_hour = valid_hours[0] if valid_hours else 0
        first_minute = valid_minutes[0] if valid_minutes else 0

        # Check remaining days in the month
        for day in range(current_day + 1, 32):
            if not is_valid_day_in_month(dt.year, dt.month, day):
                break

            test_dt = dt.replace(day=day, hour=first_hour, minute=first_minute,
                                 second=0, microsecond=0)

            # Check if this day matches day constraints
            day_of_month_match = day in self.cron_expr.day_of_month.parsed_values
            day_of_week_match = get_weekday(test_dt) in self.cron_expr.day_of_week.parsed_values

            # Apply OR logic for day fields if both are restricted
            if not self.cron_expr.day_of_month.is_wildcard() and not self.cron_expr.day_of_week.is_wildcard():
                if day_of_month_match or day_of_week_match:
                    return test_dt
            else:
                if day_of_month_match and day_of_week_match:
                    return test_dt

        return None

    def _get_next_month(self, dt: datetime) -> datetime:
        """
        Get the first valid time in the next valid month.

        Args:
            dt: The current datetime.

        Returns:
            First valid time in the next valid month.
        """
        valid_months = sorted(self.cron_expr.month.parsed_values)
        valid_hours = sorted(self.cron_expr.hour.parsed_values)
        valid_minutes = sorted(self.cron_expr.minute.parsed_values)

        # First time of any day
        first_hour = valid_hours[0] if valid_hours else 0
        first_minute = valid_minutes[0] if valid_minutes else 0

        # Try remaining months this year
        for month in valid_months:
            if month > dt.month:
                # Find first valid day in this month
                for day in range(1, 32):
                    if not is_valid_day_in_month(dt.year, month, day):
                        break

                    test_dt = datetime(dt.year, month, day, first_hour, first_minute, 0, 0)

                    # Check day constraints
                    day_of_month_match = day in self.cron_expr.day_of_month.parsed_values
                    day_of_week_match = get_weekday(test_dt) in self.cron_expr.day_of_week.parsed_values

                    if not self.cron_expr.day_of_month.is_wildcard() and not self.cron_expr.day_of_week.is_wildcard():
                        if day_of_month_match or day_of_week_match:
                            return test_dt
                    else:
                        if day_of_month_match and day_of_week_match:
                            return test_dt

        # No valid month found this year, try next year
        next_year = dt.year + 1
        first_month = valid_months[0]

        # Find first valid day in the first month of next year
        for day in range(1, 32):
            if not is_valid_day_in_month(next_year, first_month, day):
                break

            test_dt = datetime(next_year, first_month, day, first_hour, first_minute, 0, 0)

            # Check day constraints
            day_of_month_match = day in self.cron_expr.day_of_month.parsed_values
            day_of_week_match = get_weekday(test_dt) in self.cron_expr.day_of_week.parsed_values

            if not self.cron_expr.day_of_month.is_wildcard() and not self.cron_expr.day_of_week.is_wildcard():
                if day_of_month_match or day_of_week_match:
                    return test_dt
            else:
                if day_of_month_match and day_of_week_match:
                    return test_dt

        # This should rarely happen unless the cron expression is very restrictive
        raise CronPalError("Could not find valid next month")