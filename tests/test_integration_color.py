"""Integration tests for colored output."""

import subprocess
import sys
from pathlib import Path

import pytest

# Get the project root
PROJECT_ROOT = Path(__file__).parent.parent


def test_color_output_disabled_with_flag():
    """Test that --no-color flag disables color output."""
    result = subprocess.run(
        [sys.executable, "-m", "cronpal.cli", "0 0 * * *", "--no-color"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT / "src"
    )

    assert result.returncode == 0
    # Check that ANSI codes are not present
    assert "\033[" not in result.stdout
    assert "Valid cron expression" in result.stdout


def test_color_output_in_pretty_mode():
    """Test colored output in pretty mode."""
    result = subprocess.run(
        [sys.executable, "-m", "cronpal.cli", "*/15 * * * *", "--pretty", "--no-color"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT / "src"
    )

    assert result.returncode == 0
    # Check table elements
    assert "┌" in result.stdout
    assert "│" in result.stdout
    assert "Cron Expression Analysis" in result.stdout
    assert "Every 15 minutes" in result.stdout
    # No ANSI codes
    assert "\033[" not in result.stdout


def test_color_output_error_messages():
    """Test colored output for error messages."""
    result = subprocess.run(
        [sys.executable, "-m", "cronpal.cli", "invalid", "--no-color"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT / "src"
    )

    assert result.returncode == 1
    # Error should be in stderr
    assert "✗" in result.stderr
    assert "Invalid" in result.stderr
    # No ANSI codes
    assert "\033[" not in result.stderr


def test_color_output_verbose_mode():
    """Test colored output in verbose mode."""
    result = subprocess.run(
        [sys.executable, "-m", "cronpal.cli", "@daily", "--verbose", "--no-color"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT / "src"
    )

    assert result.returncode == 0
    assert "Valid cron expression" in result.stdout
    assert "Special string:" in result.stdout
    assert "Description:" in result.stdout
    # No ANSI codes
    assert "\033[" not in result.stdout


def test_color_output_next_runs():
    """Test colored output for next runs."""
    result = subprocess.run(
        [sys.executable, "-m", "cronpal.cli", "0 12 * * *", "--next", "2", "--no-color"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT / "src"
    )

    assert result.returncode == 0
    assert "Next 2 runs:" in result.stdout
    assert "1." in result.stdout
    assert "2." in result.stdout
    # No ANSI codes
    assert "\033[" not in result.stdout


def test_no_color_environment_variable():
    """Test that NO_COLOR environment variable disables colors."""
    import os
    env = os.environ.copy()
    env["NO_COLOR"] = "1"

    result = subprocess.run(
        [sys.executable, "-m", "cronpal.cli", "0 0 * * *"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT / "src",
        env=env
    )

    assert result.returncode == 0
    # Should not have ANSI codes when NO_COLOR is set
    assert "\033[" not in result.stdout
    assert "Valid cron expression" in result.stdout