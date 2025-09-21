"""Tests for the argument parser module."""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.parser import create_parser


def test_create_parser():
    """Test that parser is created successfully."""
    parser = create_parser()
    assert parser is not None
    assert parser.prog == "cronpal"


def test_parse_expression():
    """Test parsing a cron expression argument."""
    parser = create_parser()
    args = parser.parse_args(["0 0 * * *"])
    assert args.expression == "0 0 * * *"


def test_parse_version_flag():
    """Test parsing version flag."""
    parser = create_parser()
    args = parser.parse_args(["--version"])
    assert args.version is True


def test_parse_version_flag_short():
    """Test parsing short version flag."""
    parser = create_parser()
    args = parser.parse_args(["-v"])
    assert args.version is True


def test_parse_verbose_flag():
    """Test parsing verbose flag."""
    parser = create_parser()
    args = parser.parse_args(["0 0 * * *", "--verbose"])
    assert args.verbose is True
    assert args.expression == "0 0 * * *"


def test_parse_next_flag():
    """Test parsing next flag with value."""
    parser = create_parser()
    args = parser.parse_args(["0 0 * * *", "--next", "10"])
    assert args.next == 10
    assert args.expression == "0 0 * * *"


def test_parse_next_flag_short():
    """Test parsing short next flag."""
    parser = create_parser()
    args = parser.parse_args(["0 0 * * *", "-n", "5"])
    assert args.next == 5


def test_parse_no_arguments():
    """Test parsing with no arguments."""
    parser = create_parser()
    args = parser.parse_args([])
    assert args.expression is None
    assert args.version is False
    assert args.verbose is False


def test_parse_multiple_flags():
    """Test parsing multiple flags together."""
    parser = create_parser()
    args = parser.parse_args(["0 0 * * *", "--verbose", "--next", "3"])
    assert args.expression == "0 0 * * *"
    assert args.verbose is True
    assert args.next == 3


def test_help_text():
    """Test that help text contains expected information."""
    parser = create_parser()
    help_text = parser.format_help()
    assert "cronpal" in help_text
    assert "Parse and analyze cron expressions" in help_text
    assert "Examples:" in help_text
    assert "Cron Expression Format:" in help_text