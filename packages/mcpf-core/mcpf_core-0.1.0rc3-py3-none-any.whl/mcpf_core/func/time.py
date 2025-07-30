"""
time.py

This module provides utility functions for working with timestamps.

Functions:
    - convert_second_to_ms(timestamp_in_seconds: int) -> int:
        Converts a timestamp from seconds to milliseconds.
    - convert_second_to_us(timestamp_in_seconds: int) -> int:
        Converts a timestamp from seconds to microseconds.
"""


def convert_second_to_ms(timestamp_in_seconds: int):
    """
    Converts a timestamp from seconds to milliseconds.

    Args:
        timestamp_in_seconds (int): The timestamp in seconds.

    Returns:
        int: The timestamp converted to milliseconds.
    """
    return timestamp_in_seconds * 1000


def convert_second_to_us(timestamp_in_seconds: int):
    """
    Converts a timestamp from seconds to microseconds.

    Args:
        timestamp_in_seconds (int): The timestamp in seconds.

    Returns:
        int: The timestamp converted to microseconds.
    """
    return timestamp_in_seconds * 1000 * 1000
