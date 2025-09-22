"""Argument parser for CronPal CLI."""

import argparse
from textwrap import dedent

from cronpal import __version__


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="cronpal",
        description="Parse and analyze cron expressions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
            Examples:
              cronpal "0 0 * * *"              # Parse a cron expression
              cronpal --version                 # Show version
              cronpal --help                    # Show this help message
              cronpal "0 0 * * *" --timezone "US/Eastern"  # Use specific timezone
              cronpal "0 0 * * *" --pretty     # Pretty print the expression

            Cron Expression Format:
              ┌───────────── minute (0-59)
              │ ┌───────────── hour (0-23)
              │ │ ┌───────────── day of month (1-31)
              │ │ │ ┌───────────── month (1-12)
              │ │ │ │ ┌───────────── day of week (0-7)
              │ │ │ │ │
              * * * * *
        """)
    )

    # Positional argument for cron expression
    parser.add_argument(
        "expression",
        nargs="?",
        help="Cron expression to parse (e.g., '0 0 * * *')"
    )

    # Optional arguments
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version information"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "-n", "--next",
        type=int,
        metavar="N",
        help="Show next N execution times (default: 5)"
    )

    parser.add_argument(
        "-p", "--previous",
        type=int,
        metavar="N",
        help="Show previous N execution times"
    )

    parser.add_argument(
        "-t", "--timezone",
        type=str,
        metavar="TZ",
        help="Timezone for cron execution (e.g., 'US/Eastern', 'Europe/London')"
    )

    parser.add_argument(
        "--list-timezones",
        action="store_true",
        help="List all available timezone names"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print the cron expression with formatted output"
    )

    return parser