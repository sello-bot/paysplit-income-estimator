"""
Utility functions for PaySplit Income Estimator.
"""

from datetime import datetime
from typing import List
import logging


def setup_logging(log_level: str = 'INFO'):
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def calculate_day_difference(day1: int, day2: int) -> int:
    """
    Calculate minimum difference between two days of month.
    Handles wrap-around (e.g., day 30 and day 2).
    
    Args:
        day1: First day (1-31)
        day2: Second day (1-31)
    
    Returns:
        Minimum difference in days
    """
    direct_diff = abs(day1 - day2)
    wrap_around_forward = abs(day1 - day2 + 31)
    wrap_around_backward = abs(day1 - day2 - 31)
    
    return min(direct_diff, wrap_around_forward, wrap_around_backward)


def format_currency(amount: float) -> str:
    """Format amount as currency string."""
    return f"${amount:,.2f}"


def get_month_key(date: datetime) -> str:
    """Get year-month key for grouping."""
    return f"{date.year}-{date.month:02d}"


def validate_date_range(transactions: List, expected_months: int = 3) -> bool:
    """
    Validate that transactions span the expected number of months.
    
    Args:
        transactions: List of Transaction objects
        expected_months: Expected number of months (default: 3)
    
    Returns:
        True if date range is valid
    """
    if not transactions:
        return False
    
    unique_months = set(get_month_key(t.date) for t in transactions)
    return len(unique_months) >= expected_months