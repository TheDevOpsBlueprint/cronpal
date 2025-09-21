"""CronPal - A CLI tool for parsing and analyzing cron expressions."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

---

FILE: src/cronpal/cli.py
#!/usr/bin/env python3
"""Main CLI entry point for CronPal."""

import sys


def main():
    """Main entry point for the cronpal CLI."""
    print("CronPal v0.1.0")
    print("Cron expression parser and analyzer")
    return 0


if __name__ == "__main__":
    sys.exit(main())