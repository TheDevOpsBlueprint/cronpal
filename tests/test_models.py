"""Tests for the cron expression models."""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.models import (
    CronExpression,
    CronField,
    FieldRange,
    FieldType,
    FIELD_RANGES,
)


def test_field_type_enum():
    """Test FieldType enum values."""
    assert FieldType.MINUTE.value == "minute"
    assert FieldType.HOUR.value == "hour"
    assert FieldType.DAY_OF_MONTH.value == "day_of_month"
    assert FieldType.MONTH.value == "month"
    assert FieldType.DAY_OF_WEEK.value == "day_of_week"


def test_field_range_creation():
    """Test FieldRange creation."""
    range_obj = FieldRange(0, 59, FieldType.MINUTE)
    assert range_obj.min_value == 0
    assert range_obj.max_value == 59
    assert range_obj.field_type == FieldType.MINUTE


def test_cron_field_creation():
    """Test CronField creation."""
    field_range = FieldRange(0, 59, FieldType.MINUTE)
    field = CronField("*/5", FieldType.MINUTE, field_range)

    assert field.raw_value == "*/5"
    assert field.field_type == FieldType.MINUTE
    assert field.field_range == field_range


def test_cron_field_str():
    """Test CronField string representation."""
    field_range = FieldRange(0, 59, FieldType.MINUTE)
    field = CronField("0", FieldType.MINUTE, field_range)
    assert str(field) == "0"


def test_cron_expression_creation():
    """Test CronExpression creation."""
    expr = CronExpression("0 0 * * *")
    assert expr.raw_expression == "0 0 * * *"
    assert expr.minute is None
    assert expr.hour is None
    assert expr.day_of_month is None
    assert expr.month is None
    assert expr.day_of_week is None


def test_cron_expression_with_fields():
    """Test CronExpression with fields set."""
    minute_field = CronField("0", FieldType.MINUTE, FIELD_RANGES[FieldType.MINUTE])
    hour_field = CronField("0", FieldType.HOUR, FIELD_RANGES[FieldType.HOUR])

    expr = CronExpression(
        raw_expression="0 0 * * *",
        minute=minute_field,
        hour=hour_field
    )

    assert expr.minute == minute_field
    assert expr.hour == hour_field
    assert expr.day_of_month is None


def test_cron_expression_is_valid_incomplete():
    """Test is_valid() with incomplete expression."""
    expr = CronExpression("0 0 * * *")
    assert expr.is_valid() is False


def test_cron_expression_is_valid_complete():
    """Test is_valid() with complete expression."""
    expr = CronExpression(
        raw_expression="0 0 * * *",
        minute=CronField("0", FieldType.MINUTE, FIELD_RANGES[FieldType.MINUTE]),
        hour=CronField("0", FieldType.HOUR, FIELD_RANGES[FieldType.HOUR]),
        day_of_month=CronField("*", FieldType.DAY_OF_MONTH, FIELD_RANGES[FieldType.DAY_OF_MONTH]),
        month=CronField("*", FieldType.MONTH, FIELD_RANGES[FieldType.MONTH]),
        day_of_week=CronField("*", FieldType.DAY_OF_WEEK, FIELD_RANGES[FieldType.DAY_OF_WEEK])
    )
    assert expr.is_valid() is True


def test_cron_expression_str():
    """Test CronExpression string representation."""
    expr = CronExpression("*/15 0 1,15 * *")
    assert str(expr) == "*/15 0 1,15 * *"


def test_field_ranges_constants():
    """Test FIELD_RANGES constant values."""
    assert FIELD_RANGES[FieldType.MINUTE].min_value == 0
    assert FIELD_RANGES[FieldType.MINUTE].max_value == 59

    assert FIELD_RANGES[FieldType.HOUR].min_value == 0
    assert FIELD_RANGES[FieldType.HOUR].max_value == 23

    assert FIELD_RANGES[FieldType.DAY_OF_MONTH].min_value == 1
    assert FIELD_RANGES[FieldType.DAY_OF_MONTH].max_value == 31

    assert FIELD_RANGES[FieldType.MONTH].min_value == 1
    assert FIELD_RANGES[FieldType.MONTH].max_value == 12

    assert FIELD_RANGES[FieldType.DAY_OF_WEEK].min_value == 0
    assert FIELD_RANGES[FieldType.DAY_OF_WEEK].max_value == 7