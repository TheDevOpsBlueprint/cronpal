"""Scheduler for calculating cron expression run times."""

from datetime import datetime, timedelta
from typing import List, Optional

from cronpal.exceptions import CronPalError
from cronpal.models import CronExpression
from cronpal.time_utils import (
    get_next_day,
    get_next_hour,
    get_next_minute,
    get_next_month,
    get_previous_day,
    get_previous_hour,
    get_previous_minute,
    get_previous_month,
    get_weekday,
    is_valid_day_in_month,
    round_to_next_minute,
    round_to_previous_minute,
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

    def get_next_runs(self, count: int, after: Optional[datetime] = None) -> List[datetime]:
        """
        Calculate multiple next run times for the cron expression.

        Args:
            count: Number of next run times to calculate.
            after: The datetime to start searching from.
                   Defaults to current time if not provided.

        Returns:
            List of next run times.

        Raises:
            ValueError: If count is less than 1.
        """
        if count < 1:
            raise ValueError("Count must be at least 1")

        if after is None:
            after = datetime.now()

        runs = []
        current = after

        for _ in range(count):
            next_run = self.get_next_run(current)
            runs.append(next_run)
            # Start next search 1 minute after the found time
            current = next_run + timedelta(minutes=1)

        return runs

    def get_previous_run(self, before: Optional[datetime] = None) -> datetime:
        """
        Calculate the previous run time for the cron expression.

        Args:
            before: The datetime to start searching from.
                    Defaults to current time if not provided.

        Returns:
            The previous datetime when the cron expression ran.
        """
        if before is None:
            before = datetime.now()

        # Round down to previous minute if needed
        current = round_to_previous_minute(before)

        # Maximum iterations to prevent infinite loops
        max_iterations = 10000
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            # Check if current time matches the cron expression
            if self._matches_time(current):
                return current

            # Move to previous possible time
            current = self._retreat_to_previous_possible(current)

        raise CronPalError("Could not find previous run time within reasonable limits")

    def get_previous_runs(self, count: int, before: Optional[datetime] = None) -> List[datetime]:
        """
        Calculate multiple previous run times for the cron expression.

        Args:
            count: Number of previous run times to calculate.
            before: The datetime to start searching from.
                    Defaults to current time if not provided.

        Returns:
            List of previous run times (most recent first).

        Raises:
            ValueError: If count is less than 1.
        """
        if count < 1:
            raise ValueError("Count must be at least 1")

        if before is None:
            before = datetime.now()

        runs = []
        current = before

        for _ in range(count):
            previous_run = self.get_previous_run(current)
            runs.append(previous_run)
            # Start next search 1 minute before the found time
            current = previous_run - timedelta(minutes=1)

        return runs

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

    def _retreat_to_previous_possible(self, dt: datetime) -> datetime:
        """
        Retreat datetime to the previous possible matching time.

        Args:
            dt: The current datetime.

        Returns:
            The previous datetime that could potentially match.
        """
        # Try to retreat minute first
        prev_minute = self._get_previous_minute(dt)
        if prev_minute is not None:
            return prev_minute

        # If no valid minute in this hour, try previous hour
        prev_hour = self._get_previous_hour(dt)
        if prev_hour is not None:
            return prev_hour

        # If no valid hour today, try previous day
        prev_day = self._get_previous_day(dt)
        if prev_day is not None:
            return prev_day

        # If no valid day this month, try previous month
        return self._get_previous_month(dt)

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

    def _get_previous_minute(self, dt: datetime) -> Optional[datetime]:
        """
        Get the previous valid minute before the current time.

        Args:
            dt: The current datetime.

        Returns:
            Previous valid minute in the same hour, or None if no valid minute.
        """
        current_minute = dt.minute
        valid_minutes = sorted(self.cron_expr.minute.parsed_values, reverse=True)

        for minute in valid_minutes:
            if minute < current_minute:
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

    def _get_previous_hour(self, dt: datetime) -> Optional[datetime]:
        """
        Get the previous valid hour before the current time.

        Args:
            dt: The current datetime.

        Returns:
            Previous valid hour in the same day, or None if no valid hour.
        """
        current_hour = dt.hour
        valid_hours = sorted(self.cron_expr.hour.parsed_values, reverse=True)
        valid_minutes = sorted(self.cron_expr.minute.parsed_values, reverse=True)

        # Last minute of the previous valid hour
        last_minute = valid_minutes[0] if valid_minutes else 59

        for hour in valid_hours:
            if hour < current_hour:
                return dt.replace(hour=hour, minute=last_minute, second=0, microsecond=0)

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

    def _get_previous_day(self, dt: datetime) -> Optional[datetime]:
        """
        Get the previous valid day before the current time.

        Args:
            dt: The current datetime.

        Returns:
            Previous valid day in the same month, or None if no valid day.
        """
        current_day = dt.day
        valid_hours = sorted(self.cron_expr.hour.parsed_values, reverse=True)
        valid_minutes = sorted(self.cron_expr.minute.parsed_values, reverse=True)

        # Last time of the day
        last_hour = valid_hours[0] if valid_hours else 23
        last_minute = valid_minutes[0] if valid_minutes else 59

        # Check previous days in the month
        for day in range(current_day - 1, 0, -1):
            test_dt = dt.replace(day=day, hour=last_hour, minute=last_minute,
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

        # Start searching from current year
        current_year = dt.year
        current_month = dt.month

        # Search for up to 10 years to handle February 29th cases
        for year_offset in range(10):
            search_year = current_year + year_offset

            # Determine which months to check this year
            if year_offset == 0:
                # For current year, only check months after current month
                months_to_check = [m for m in valid_months if m > current_month]
            else:
                # For future years, check all valid months
                months_to_check = valid_months

            for month in months_to_check:
                # Find first valid day in this month
                for day in range(1, 32):
                    if not is_valid_day_in_month(search_year, month, day):
                        continue

                    test_dt = datetime(search_year, month, day, first_hour, first_minute, 0, 0)

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

    def _get_previous_month(self, dt: datetime) -> datetime:
        """
        Get the last valid time in the previous valid month.

        Args:
            dt: The current datetime.

        Returns:
            Last valid time in the previous valid month.
        """
        valid_months = sorted(self.cron_expr.month.parsed_values, reverse=True)
        valid_hours = sorted(self.cron_expr.hour.parsed_values, reverse=True)
        valid_minutes = sorted(self.cron_expr.minute.parsed_values, reverse=True)

        # Last time of any day
        last_hour = valid_hours[0] if valid_hours else 23
        last_minute = valid_minutes[0] if valid_minutes else 59

        # Start searching from current year
        current_year = dt.year
        current_month = dt.month

        # Search for up to 10 years back
        for year_offset in range(10):
            search_year = current_year - year_offset

            # Determine which months to check this year
            if year_offset == 0:
                # For current year, only check months before current month
                months_to_check = [m for m in valid_months if m < current_month]
            else:
                # For past years, check all valid months
                months_to_check = valid_months

            for month in months_to_check:
                # Find last valid day in this month
                for day in range(31, 0, -1):
                    if not is_valid_day_in_month(search_year, month, day):
                        continue

                    test_dt = datetime(search_year, month, day, last_hour, last_minute, 0, 0)

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
        raise CronPalError("Could not find valid previous month")