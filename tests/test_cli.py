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
    result = main([])
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
    assert "cronpal" in result.stdout.lower()


def test_version_flag():
    """Test the --version flag."""
    result = main(["--version"])
    assert result == 0


def test_version_flag_short():
    """Test the -v flag."""
    result = main(["-v"])
    assert result == 0


def test_help_output():
    """Test that help is shown when no arguments provided."""
    # Capture stdout to verify help is shown
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main([])

    output = f.getvalue()
    assert "usage:" in output.lower()
    assert "cronpal" in output.lower()


def test_expression_argument():
    """Test parsing a cron expression."""
    result = main(["0 0 * * *"])
    assert result == 0


def test_verbose_flag():
    """Test the --verbose flag."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Raw expression:" in output
    assert "Valid:" in output


def test_next_flag():
    """Test the --next flag."""
    result = main(["0 0 * * *", "--next", "10"])
    assert result == 0


def test_cron_expression_object_usage():
    """Test that CronExpression is used in the CLI."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["*/15 * * * *"])

    output = f.getvalue()
    assert "*/15 * * * *" in output
    assert result == 0