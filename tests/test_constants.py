"""Tests for cron constants."""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.constants import (
    DAY_NAMES,
    LIST_SEPARATOR,
    MONTH_NAMES,
    RANGE_SEPARATOR,
    SPECIAL_STRINGS,
    STEP_SEPARATOR,
    WILDCARD,
)


def test_special_strings():
    """Test special cron strings."""
    assert SPECIAL_STRINGS["@yearly"] == "0 0 1 1 *"
    assert SPECIAL_STRINGS["@annually"] == "0 0 1 1 *"
    assert SPECIAL_STRINGS["@monthly"] == "0 0 1 * *"
    assert SPECIAL_STRINGS["@weekly"] == "0 0 * * 0"
    assert SPECIAL_STRINGS["@daily"] == "0 0 * * *"
    assert SPECIAL_STRINGS["@midnight"] == "0 0 * * *"
    assert SPECIAL_STRINGS["@hourly"] == "0 * * * *"
    assert SPECIAL_STRINGS["@reboot"] == "@reboot"


def test_month_names():
    """Test month name mappings."""
    assert MONTH_NAMES["JAN"] == 1
    assert MONTH_NAMES["FEB"] == 2
    assert MONTH_NAMES["MAR"] == 3
    assert MONTH_NAMES["APR"] == 4
    assert MONTH_NAMES["MAY"] == 5
    assert MONTH_NAMES["JUN"] == 6
    assert MONTH_NAMES["JUL"] == 7
    assert MONTH_NAMES["AUG"] == 8
    assert MONTH_NAMES["SEP"] == 9
    assert MONTH_NAMES["OCT"] == 10
    assert MONTH_NAMES["NOV"] == 11
    assert MONTH_NAMES["DEC"] == 12
    assert len(MONTH_NAMES) == 12


def test_day_names():
    """Test day name mappings."""
    assert DAY_NAMES["SUN"] == 0
    assert DAY_NAMES["MON"] == 1
    assert DAY_NAMES["TUE"] == 2
    assert DAY_NAMES["WED"] == 3
    assert DAY_NAMES["THU"] == 4
    assert DAY_NAMES["FRI"] == 5
    assert DAY_NAMES["SAT"] == 6
    assert len(DAY_NAMES) == 7


def test_special_characters():
    """Test special character constants."""
    assert WILDCARD == "*"
    assert RANGE_SEPARATOR == "-"
    assert LIST_SEPARATOR == ","
    assert STEP_SEPARATOR == "/"


def test_yearly_and_annually_are_same():
    """Test that @yearly and @annually have the same value."""
    assert SPECIAL_STRINGS["@yearly"] == SPECIAL_STRINGS["@annually"]


def test_daily_and_midnight_are_same():
    """Test that @daily and @midnight have the same value."""
    assert SPECIAL_STRINGS["@daily"] == SPECIAL_STRINGS["@midnight"]