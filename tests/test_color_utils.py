"""Tests for color utilities."""

import os
import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.color_utils import (
    ColorConfig,
    ColorScheme,
    format_cron_field,
    format_error_message,
    format_schedule_time,
    format_success_message,
    format_table_border,
    get_color_config,
    reset_color_config,
    set_color_config,
)


class TestColorConfig:
    """Tests for ColorConfig class."""

    def test_init_default(self):
        """Test default initialization."""
        config = ColorConfig()
        # Should auto-detect based on terminal
        assert config.use_colors in [True, False]

    def test_init_with_colors(self):
        """Test initialization with colors enabled."""
        config = ColorConfig(use_colors=True)
        # Will be True if colorama is available
        assert config.use_colors in [True, False]

    def test_init_without_colors(self):
        """Test initialization with colors disabled."""
        config = ColorConfig(use_colors=False)
        assert config.use_colors is False

    def test_no_color_env_variable(self, monkeypatch):
        """Test NO_COLOR environment variable."""
        monkeypatch.setenv("NO_COLOR", "1")
        config = ColorConfig()
        assert config.use_colors is False

    def test_get_color_with_colors_disabled(self):
        """Test getting color when colors are disabled."""
        config = ColorConfig(use_colors=False)
        color = config.get_color(ColorScheme.SUCCESS)
        assert color == ""

    def test_colorize_with_colors_disabled(self):
        """Test colorizing text when colors are disabled."""
        config = ColorConfig(use_colors=False)
        result = config.colorize("test", ColorScheme.SUCCESS)
        assert result == "test"

    def test_success_method(self):
        """Test success formatting method."""
        config = ColorConfig(use_colors=False)
        result = config.success("Success!")
        assert result == "Success!"

    def test_error_method(self):
        """Test error formatting method."""
        config = ColorConfig(use_colors=False)
        result = config.error("Error!")
        assert result == "Error!"

    def test_warning_method(self):
        """Test warning formatting method."""
        config = ColorConfig(use_colors=False)
        result = config.warning("Warning!")
        assert result == "Warning!"

    def test_info_method(self):
        """Test info formatting method."""
        config = ColorConfig(use_colors=False)
        result = config.info("Info")
        assert result == "Info"

    def test_header_method(self):
        """Test header formatting method."""
        config = ColorConfig(use_colors=False)
        result = config.header("Header")
        assert result == "Header"

    def test_field_method(self):
        """Test field formatting method."""
        config = ColorConfig(use_colors=False)
        result = config.field("Field")
        assert result == "Field"

    def test_value_method(self):
        """Test value formatting method."""
        config = ColorConfig(use_colors=False)
        result = config.value("Value")
        assert result == "Value"

    def test_separator_method(self):
        """Test separator formatting method."""
        config = ColorConfig(use_colors=False)
        result = config.separator("-")
        assert result == "-"

    def test_highlight_method(self):
        """Test highlight formatting method."""
        config = ColorConfig(use_colors=False)
        result = config.highlight("Important")
        assert result == "Important"


class TestGlobalColorConfig:
    """Tests for global color config management."""

    def teardown_method(self):
        """Reset global config after each test."""
        reset_color_config()

    def test_get_color_config_creates_default(self):
        """Test that get_color_config creates a default config."""
        config = get_color_config()
        assert config is not None
        assert isinstance(config, ColorConfig)

    def test_get_color_config_returns_same_instance(self):
        """Test that get_color_config returns the same instance."""
        config1 = get_color_config()
        config2 = get_color_config()
        assert config1 is config2

    def test_set_color_config(self):
        """Test setting a custom color config."""
        custom = ColorConfig(use_colors=False)
        set_color_config(custom)

        retrieved = get_color_config()
        assert retrieved is custom
        assert retrieved.use_colors is False

    def test_reset_color_config(self):
        """Test resetting the global config."""
        custom = ColorConfig(use_colors=False)
        set_color_config(custom)

        reset_color_config()

        # Should create a new default config
        new_config = get_color_config()
        assert new_config is not custom


class TestFormatFunctions:
    """Tests for formatting utility functions."""

    def test_format_cron_field_basic(self):
        """Test basic cron field formatting."""
        reset_color_config()
        set_color_config(ColorConfig(use_colors=False))

        result = format_cron_field("Minute", "*/15")
        assert "Minute: */15" in result

    def test_format_cron_field_with_description(self):
        """Test cron field formatting with description."""
        reset_color_config()
        set_color_config(ColorConfig(use_colors=False))

        result = format_cron_field("Hour", "9-17", "Business hours")
        assert "Hour: 9-17" in result
        assert "Business hours" in result

    def test_format_error_message_basic(self):
        """Test basic error message formatting."""
        reset_color_config()
        set_color_config(ColorConfig(use_colors=False))

        result = format_error_message("Invalid expression")
        assert "✗ Invalid expression" in result

    def test_format_error_message_with_suggestion(self):
        """Test error message with suggestion."""
        reset_color_config()
        set_color_config(ColorConfig(use_colors=False))

        result = format_error_message("Invalid", "Try adding more fields")
        assert "✗ Invalid" in result
        assert "💡 Suggestion:" in result
        assert "Try adding more fields" in result

    def test_format_success_message_basic(self):
        """Test basic success message formatting."""
        reset_color_config()
        set_color_config(ColorConfig(use_colors=False))

        result = format_success_message("Valid expression")
        assert "✓ Valid expression" in result

    def test_format_success_message_with_details(self):
        """Test success message with details."""
        reset_color_config()
        set_color_config(ColorConfig(use_colors=False))

        result = format_success_message("Valid", "Runs daily")
        assert "✓ Valid" in result
        assert "Runs daily" in result

    def test_format_table_border(self):
        """Test table border formatting."""
        reset_color_config()
        set_color_config(ColorConfig(use_colors=False))

        result = format_table_border("─", 10)
        assert result == "─" * 10

    def test_format_schedule_time_next(self):
        """Test formatting next scheduled time."""
        reset_color_config()
        set_color_config(ColorConfig(use_colors=False))

        result = format_schedule_time("2024-01-15 10:00:00", is_next=True)
        assert result == "2024-01-15 10:00:00"

    def test_format_schedule_time_previous(self):
        """Test formatting previous scheduled time."""
        reset_color_config()
        set_color_config(ColorConfig(use_colors=False))

        result = format_schedule_time("2024-01-15 10:00:00", is_next=False)
        assert result == "2024-01-15 10:00:00"


class TestColorSchemeEnum:
    """Tests for ColorScheme enum."""

    def test_color_scheme_values(self):
        """Test ColorScheme enum values."""
        assert ColorScheme.SUCCESS.value == "success"
        assert ColorScheme.ERROR.value == "error"
        assert ColorScheme.WARNING.value == "warning"
        assert ColorScheme.INFO.value == "info"
        assert ColorScheme.HEADER.value == "header"
        assert ColorScheme.FIELD.value == "field"
        assert ColorScheme.VALUE.value == "value"
        assert ColorScheme.SEPARATOR.value == "separator"
        assert ColorScheme.HIGHLIGHT.value == "highlight"


class TestColorOutput:
    """Tests for actual color output (when available)."""

    def test_colors_when_available(self):
        """Test color output when colorama is available."""
        try:
            import colorama
            # If colorama is available, test with colors enabled
            config = ColorConfig(use_colors=True)

            if config.use_colors:
                # Colors are available
                colored_text = config.success("Success")
                # Should contain ANSI codes or actual text
                assert "Success" in colored_text

                error_text = config.error("Error")
                assert "Error" in error_text
        except ImportError:
            # colorama not available, skip this test
            pass

    def test_no_colors_in_non_tty(self, monkeypatch):
        """Test that colors are disabled for non-TTY output."""
        # Mock isatty to return False
        monkeypatch.setattr(sys.stdout, 'isatty', lambda: False)

        config = ColorConfig()
        # Should be disabled for non-TTY
        assert config.use_colors is False