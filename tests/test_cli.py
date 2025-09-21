"""Tests for the CLI module."""

import subprocess
import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.cli import main


def test_main_function():
    """Test that the main function runs without error."""
    result = main()
    assert result == 0


def test_cli_execution():
    """Test that the CLI can be executed as a module."""
    result = subprocess.run(
        [sys.executable, "-m", "cronpal.cli"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent / "src"
    )
    assert result.returncode == 0
    assert "CronPal" in result.stdout


def test_version_output():
    """Test that version information is displayed."""
    # This will be expanded in future PRs
    from cronpal import __version__
    assert __version__ == "0.1.0"