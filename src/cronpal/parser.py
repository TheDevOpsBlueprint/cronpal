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

    return parser