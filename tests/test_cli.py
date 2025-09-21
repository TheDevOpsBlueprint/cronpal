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
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main([])

    output = f.getvalue()
    assert "usage:" in output.lower()
    assert "cronpal" in output.lower()


def test_valid_expression():
    """Test parsing a valid cron expression."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 * * *"])

    output = f.getvalue()
    assert result == 0
    assert "✓ Valid" in output
    assert "0 0 * * *" in output


def test_invalid_expression_with_suggestion():
    """Test parsing an invalid expression with suggestion."""
    import io
    import contextlib

    f_out = io.StringIO()
    f_err = io.StringIO()

    with contextlib.redirect_stdout(f_out), contextlib.redirect_stderr(f_err):
        result = main(["0 0 *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "✗ Invalid" in error_output
    assert "💡 Suggestion:" in error_output
    assert "Add missing fields" in error_output


def test_invalid_character_with_suggestion():
    """Test invalid character with suggestion."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["0 0 * * $"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "✗ Validation failed" in error_output
    assert "💡 Suggestion:" in error_output


def test_verbose_flag_valid():
    """Test the --verbose flag with valid expression."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["0 0 * * *", "--verbose"])

    output = f.getvalue()
    assert result == 0
    assert "Raw expression:" in output
    assert "Validation: PASSED" in output


def test_verbose_flag_invalid():
    """Test the --verbose flag with invalid expression."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stderr(f):
        result = main(["invalid", "--verbose"])

    output = f.getvalue()
    assert result == 1
    assert "Expression: 'invalid'" in output
    assert "Expected format:" in output


def test_next_flag():
    """Test the --next flag."""
    result = main(["0 0 * * *", "--next", "10"])
    assert result == 0


def test_special_string():
    """Test parsing a special string."""
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        result = main(["@daily"])

    output = f.getvalue()
    assert result == 0
    assert "✓ Valid" in output
    assert "@daily" in output


def test_unknown_special_string():
    """Test unknown special string with suggestion."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["@invalid"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "✗ Invalid" in error_output
    assert "Unknown special string" in error_output
    assert "💡 Suggestion:" in error_output
    assert "@yearly" in error_output


def test_empty_expression():
    """Test empty expression with suggestion."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main([""])

    error_output = f_err.getvalue()
    assert result == 1
    assert "✗ Invalid" in error_output
    assert "Empty" in error_output
    assert "💡 Suggestion:" in error_output


def test_too_many_fields():
    """Test too many fields with suggestion."""
    import io
    import contextlib

    f_err = io.StringIO()

    with contextlib.redirect_stderr(f_err):
        result = main(["0 0 * * * *"])

    error_output = f_err.getvalue()
    assert result == 1
    assert "✗ Invalid" in error_output
    assert "Invalid number of fields" in error_output
    assert "💡 Suggestion:" in error_output
    assert "Remove extra fields" in error_output


def test_unexpected_error_handling():
    """Test that unexpected errors return exit code 2."""
    # This test is tricky to trigger naturally, but we ensure the path exists
    # The main function catches Exception and returns 2
    import io
    import contextlib
    from unittest.mock import patch

    f_err = io.StringIO()

    # Mock validate_expression to raise a non-CronPalError
    with patch('cronpal.cli.validate_expression', side_effect=RuntimeError("Unexpected")):
        with contextlib.redirect_stderr(f_err):
            result = main(["0 0 * * *"])

    error_output = f_err.getvalue()
    assert result == 2
    assert "✗ Unexpected error" in error_output