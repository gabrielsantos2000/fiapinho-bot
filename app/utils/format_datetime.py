"""
Utility module for datetime operations and timestamp conversions.
"""

from datetime import datetime
from typing import Tuple


def datetime_to_timestamp(dt: datetime) -> int:
    """
    Convert datetime to Unix timestamp.

    Args:
        dt: datetime object

    Returns:
        int: Unix timestamp
    """
    return int(dt.timestamp())


def get_month_range_timestamps(year: int = None, month: int = None) -> Tuple[int, int]:
    """
    Get Unix timestamps for the start and end of a month.

    Args:
        year: Year (defaults to current year)
        month: Month (defaults to current month)

    Returns:
        Tuple[int, int]: (start_timestamp, end_timestamp)
    """
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    # First day of the month
    start_date = datetime(year, month, 1)

    # First day of next month
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    return datetime_to_timestamp(start_date), datetime_to_timestamp(end_date)


def get_date_timestamp(date: datetime = None) -> int:
    """
    Get Unix timestamp for a specific date (start of day).

    Args:
        date: Date to convert (defaults to today)

    Returns:
        int: Unix timestamp for start of day
    """
    if date is None:
        date = datetime.now()

    # Start of day
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    return datetime_to_timestamp(start_of_day)
