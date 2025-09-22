"""Color utilities for terminal output."""

import os
import sys
from enum import Enum
from typing import Optional

try:
    import colorama
    from colorama import Fore, Back, Style

    colorama.init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False


    # Create dummy classes if colorama is not available
    class Fore:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        RESET = ""
        LIGHTBLACK_EX = LIGHTRED_EX = LIGHTGREEN_EX = LIGHTYELLOW_EX = ""
        LIGHTBLUE_EX = LIGHTMAGENTA_EX = LIGHTCYAN_EX = LIGHTWHITE_EX = ""


    class Back:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        RESET = ""


    class Style:
        DIM = NORMAL = BRIGHT = RESET_ALL = ""


class ColorScheme(Enum):
    """Color schemes for different output types."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HEADER = "header"
    FIELD = "field"
    VALUE = "value"
    SEPARATOR = "separator"
    HIGHLIGHT = "highlight"


class ColorConfig:
    """Configuration for colors used in output."""

    def __init__(self, use_colors: Optional[bool] = None):
        """
        Initialize color configuration.

        Args:
            use_colors: Whether to use colors. If None, auto-detect.
        """
        if use_colors is None:
            # Check NO_COLOR environment variable
            if os.environ.get("NO_COLOR"):
                self.use_colors = False
            # Check if output is to a terminal
            elif not sys.stdout.isatty():
                self.use_colors = False
            else:
                self.use_colors = COLORS_AVAILABLE
        else:
            self.use_colors = use_colors and COLORS_AVAILABLE

        # Define color mappings
        self.colors = {
            ColorScheme.SUCCESS: Fore.GREEN,
            ColorScheme.ERROR: Fore.RED,
            ColorScheme.WARNING: Fore.YELLOW,
            ColorScheme.INFO: Fore.CYAN,
            ColorScheme.HEADER: Fore.BLUE + Style.BRIGHT,
            ColorScheme.FIELD: Fore.MAGENTA,
            ColorScheme.VALUE: Fore.GREEN,
            ColorScheme.SEPARATOR: Fore.LIGHTBLACK_EX,
            ColorScheme.HIGHLIGHT: Fore.YELLOW + Style.BRIGHT,
        }

    def get_color(self, scheme: ColorScheme) -> str:
        """
        Get color code for a scheme.

        Args:
            scheme: The color scheme to get.

        Returns:
            Color code string or empty string if colors disabled.
        """
        if not self.use_colors:
            return ""
        return self.colors.get(scheme, "")

    def colorize(self, text: str, scheme: ColorScheme) -> str:
        """
        Colorize text with the specified scheme.

        Args:
            text: Text to colorize.
            scheme: Color scheme to apply.

        Returns:
            Colored text or original text if colors disabled.
        """
        if not self.use_colors:
            return text
        color = self.get_color(scheme)
        if color:
            return f"{color}{text}{Style.RESET_ALL}"
        return text

    def success(self, text: str) -> str:
        """Format success message."""
        return self.colorize(text, ColorScheme.SUCCESS)

    def error(self, text: str) -> str:
        """Format error message."""
        return self.colorize(text, ColorScheme.ERROR)

    def warning(self, text: str) -> str:
        """Format warning message."""
        return self.colorize(text, ColorScheme.WARNING)

    def info(self, text: str) -> str:
        """Format info message."""
        return self.colorize(text, ColorScheme.INFO)

    def header(self, text: str) -> str:
        """Format header text."""
        return self.colorize(text, ColorScheme.HEADER)

    def field(self, text: str) -> str:
        """Format field name."""
        return self.colorize(text, ColorScheme.FIELD)

    def value(self, text: str) -> str:
        """Format field value."""
        return self.colorize(text, ColorScheme.VALUE)

    def separator(self, text: str) -> str:
        """Format separator."""
        return self.colorize(text, ColorScheme.SEPARATOR)

    def highlight(self, text: str) -> str:
        """Format highlighted text."""
        return self.colorize(text, ColorScheme.HIGHLIGHT)


# Global color config instance
_color_config: Optional[ColorConfig] = None


def get_color_config() -> ColorConfig:
    """
    Get the global color configuration.

    Returns:
        The global ColorConfig instance.
    """
    global _color_config
    if _color_config is None:
        _color_config = ColorConfig()
    return _color_config


def set_color_config(config: ColorConfig) -> None:
    """
    Set the global color configuration.

    Args:
        config: The ColorConfig to use globally.
    """
    global _color_config
    _color_config = config


def reset_color_config() -> None:
    """Reset the global color configuration."""
    global _color_config
    _color_config = None


def format_cron_field(field_name: str, field_value: str,
                      description: Optional[str] = None) -> str:
    """
    Format a cron field with colors.

    Args:
        field_name: Name of the field.
        field_value: Value of the field.
        description: Optional description.

    Returns:
        Formatted string with colors.
    """
    config = get_color_config()

    result = f"{config.field(field_name)}: {config.value(field_value)}"
    if description:
        result += f" {config.separator('-')} {config.info(description)}"

    return result


def format_error_message(message: str, suggestion: Optional[str] = None) -> str:
    """
    Format an error message with colors.

    Args:
        message: Error message.
        suggestion: Optional suggestion for fixing.

    Returns:
        Formatted error message.
    """
    config = get_color_config()

    result = config.error(f"✗ {message}")
    if suggestion:
        result += f"\n  {config.warning('💡 Suggestion:')} {suggestion}"

    return result


def format_success_message(message: str, details: Optional[str] = None) -> str:
    """
    Format a success message with colors.

    Args:
        message: Success message.
        details: Optional additional details.

    Returns:
        Formatted success message.
    """
    config = get_color_config()

    result = config.success(f"✓ {message}")
    if details:
        result += f"\n  {config.info(details)}"

    return result


def format_table_border(char: str, width: int = 1) -> str:
    """
    Format table border characters.

    Args:
        char: Border character.
        width: Number of times to repeat.

    Returns:
        Formatted border string.
    """
    config = get_color_config()
    return config.separator(char * width)


def format_schedule_time(time_str: str, is_next: bool = True) -> str:
    """
    Format a scheduled run time.

    Args:
        time_str: Time string to format.
        is_next: Whether this is a future time.

    Returns:
        Formatted time string.
    """
    config = get_color_config()

    if is_next:
        return config.highlight(time_str)
    else:
        return config.info(time_str)