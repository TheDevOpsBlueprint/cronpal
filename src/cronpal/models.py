"""Data models for cron expressions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Set


class FieldType(Enum):
    """Enum for different cron field types."""

    MINUTE = "minute"
    HOUR = "hour"
    DAY_OF_MONTH = "day_of_month"
    MONTH = "month"
    DAY_OF_WEEK = "day_of_week"


@dataclass
class FieldRange:
    """Represents the valid range for a cron field."""

    min_value: int
    max_value: int
    field_type: FieldType


@dataclass
class CronField:
    """Represents a single field in a cron expression."""

    raw_value: str
    field_type: FieldType
    field_range: FieldRange
    parsed_values: Optional[Set[int]] = field(default=None)

    def __str__(self) -> str:
        """String representation of the field."""
        return self.raw_value

    def is_wildcard(self) -> bool:
        """Check if this field is a wildcard."""
        return self.raw_value == "*"

    def matches(self, value: int) -> bool:
        """
        Check if a value matches this field.

        Args:
            value: The value to check.

        Returns:
            True if the value matches this field.
        """
        if self.parsed_values is None:
            return False
        return value in self.parsed_values


@dataclass
class CronExpression:
    """Represents a complete cron expression."""

    raw_expression: str
    minute: Optional[CronField] = None
    hour: Optional[CronField] = None
    day_of_month: Optional[CronField] = None
    month: Optional[CronField] = None
    day_of_week: Optional[CronField] = None

    def __str__(self) -> str:
        """String representation of the cron expression."""
        return self.raw_expression

    def is_valid(self) -> bool:
        """Check if all required fields are present."""
        return all([
            self.minute is not None,
            self.hour is not None,
            self.day_of_month is not None,
            self.month is not None,
            self.day_of_week is not None
        ])

    def matches_time(
        self,
        minute: int,
        hour: Optional[int] = None,
        day: Optional[int] = None
    ) -> bool:
        """
        Check if this expression matches a given time.

        Args:
            minute: The minute value to check (0-59).
            hour: The hour value to check (0-23).
            day: The day of month value to check (1-31).

        Returns:
            True if the time matches.
        """
        if self.minute is None:
            return False

        minute_match = self.minute.matches(minute)

        if hour is not None and self.hour is not None:
            hour_match = self.hour.matches(hour)
            minute_match = minute_match and hour_match

        if day is not None and self.day_of_month is not None:
            day_match = self.day_of_month.matches(day)
            minute_match = minute_match and day_match

        return minute_match


# Define valid ranges for each field type
FIELD_RANGES = {
    FieldType.MINUTE: FieldRange(0, 59, FieldType.MINUTE),
    FieldType.HOUR: FieldRange(0, 23, FieldType.HOUR),
    FieldType.DAY_OF_MONTH: FieldRange(1, 31, FieldType.DAY_OF_MONTH),
    FieldType.MONTH: FieldRange(1, 12, FieldType.MONTH),
    FieldType.DAY_OF_WEEK: FieldRange(0, 7, FieldType.DAY_OF_WEEK),
}