#!/usr/bin/env python3
"""Demo script for testing pretty print functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.cli import main

# Test various expressions with pretty print
expressions = [
    "0 0 * * *",                    # Daily at midnight
    "*/15 * * * *",                  # Every 15 minutes
    "0 9-17 * * MON-FRI",           # Business hours on weekdays
    "0 0 1 * *",                    # First of every month
    "@weekly",                       # Weekly (special string)
    "30 2 15 JAN,JUL *",            # Specific dates with month names
    "0 */4 * * *",                  # Every 4 hours
]

print("CronPal Pretty Print Demo")
print("=" * 80)

for expr in expressions:
    print(f"\nExpression: {expr}")
    print("-" * 40)
    main([expr, "--pretty"])
    print("\n" + "=" * 80)