"""
Sample transaction data for testing and examples.
"""

from datetime import datetime
from src.models import Transaction


def get_standard_salary_scenario():
    """Regular monthly salary."""
    return [
        Transaction(datetime(2025, 8, 25), 3500.0, "salary", "ACME Corp"),
        Transaction(datetime(2025, 9, 25), 3500.0, "salary", "ACME Corp"),
        Transaction(datetime(2025, 10, 25), 3500.0, "salary", "ACME Corp"),
    ]


def get_salary_plus_freelance_scenario():
    """Full-time job plus freelance income."""
    return [
        # Primary salary
        Transaction(datetime(2025, 8, 25), 3500.0, "salary", "Main Employer"),
        Transaction(datetime(2025, 9, 25), 3500.0, "salary", "Main Employer"),
        Transaction(datetime(2025, 10, 25), 3500.0, "salary", "Main Employer"),
        # Freelance work
        Transaction(datetime(2025, 8, 10), 800.0, "income", "Client A"),
        Transaction(datetime(2025, 9, 10), 950.0, "income", "Client A"),
        Transaction(datetime(2025, 10, 10), 875.0, "income", "Client A"),
    ]


def get_variable_income_scenario():
    """Variable freelance income."""
    return [
        Transaction(datetime(2025, 8, 15), 2500.0, "income", "Various Clients"),
        Transaction(datetime(2025, 9, 15), 3200.0, "income", "Various Clients"),
        Transaction(datetime(2025, 10, 15), 2800.0, "income", "Various Clients"),
    ]


def get_complex_scenario():
    """Multiple income streams with noise."""
    return [
        # Salary
        Transaction(datetime(2025, 8, 25), 3500.0, "salary", "Employer"),
        Transaction(datetime(2025, 9, 26), 3500.0, "salary", "Employer"),
        Transaction(datetime(2025, 10, 24), 3500.0, "salary", "Employer"),
        # Side income
        Transaction(datetime(2025, 8, 10), 600.0, "income", "Client 1"),
        Transaction(datetime(2025, 9, 10), 650.0, "income", "Client 1"),
        Transaction(datetime(2025, 10, 10), 700.0, "income", "Client 1"),
        # One-time payment (should be filtered)
        Transaction(datetime(2025, 9, 15), 5000.0, "income", "Bonus"),
        # Transfers (should be excluded)
        Transaction(datetime(2025, 8, 5), 1000.0, "transfer", "From Savings"),
        Transaction(datetime(2025, 9, 12), 800.0, "transfer", "From Checking"),
    ]