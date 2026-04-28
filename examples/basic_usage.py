"""
Basic usage examples for PaySplit Income Estimator.
"""

from src.income_estimator import IncomeEstimator
from src.utils import setup_logging, format_currency
from examples.sample_data import (
    get_standard_salary_scenario,
    get_salary_plus_freelance_scenario,
    get_variable_income_scenario
)


def example_1_simple_salary():
    """Example 1: Standard monthly salary."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Standard Monthly Salary")
    print("="*70)
    
    # Get sample data
    transactions = get_standard_salary_scenario()
    
    # Create estimator
    estimator = IncomeEstimator()
    
    # Estimate income
    result = estimator.estimate(transactions)
    
    # Display results
    print(f"\nEstimated Monthly Income: {format_currency(result.estimated_income)}")
    print(f"Confidence Level: {result.confidence.upper()}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Income Streams Detected: {len(result.streams)}")
    
    for i, stream in enumerate(result.streams, 1):
        print(f"\n  Stream {i}:")
        print(f"    Payment Day: ~{stream.center_day:.0f}th of month")
        print(f"    Median Amount: {format_currency(stream.median_amount)}")
        print(f"    Consistency: {stream.get_consistency_rating()}")


def example_2_multiple_streams():
    """Example 2: Multiple income streams."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Multiple Income Streams")
    print("="*70)
    
    transactions = get_salary_plus_freelance_scenario()
    
    estimator = IncomeEstimator()
    result = estimator.estimate(transactions)
    
    print(f"\nTotal Monthly Income: {format_currency(result.estimated_income)}")
    print(f"Confidence: {result.confidence.upper()}")
    print(f"\nIncome Breakdown ({len(result.streams)} streams):")
    
    for i, stream in enumerate(result.streams, 1):
        print(f"\n  Stream {i}:")
        print(f"    Day of Month: ~{stream.center_day:.0f}")
        print(f"    Amount: {format_currency(stream.median_amount)}")
        print(f"    Occurrences: {stream.transaction_count}")
        print(f"    Consistency: {stream.get_consistency_rating()}")


def example_3_variable_income():
    """Example 3: Variable income amounts."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Variable Income")
    print("="*70)
    
    transactions = get_variable_income_scenario()
    
    estimator = IncomeEstimator()
    result = estimator.estimate(transactions)
    
    print(f"\nEstimated Income: {format_currency(result.estimated_income)}")
    print(f"Confidence: {result.confidence.upper()}")
    
    if result.streams:
        stream = result.streams[0]
        print(f"\nIncome Details:")
        print(f"  Payment Day: ~{stream.center_day:.0f}th")
        print(f"  Median Amount: {format_currency(stream.median_amount)}")
        print(f"  Variance: {format_currency(stream.amount_variance)}")
        print(f"  Consistency: {stream.get_consistency_rating()}")


def example_4_custom_config():
    """Example 4: Custom configuration."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Configuration")
    print("="*70)
    
    transactions = get_standard_salary_scenario()
    
    # Custom estimator with relaxed parameters
    estimator = IncomeEstimator(
        window_tolerance=3,  # Allow ±3 days
        min_months_present=2,  # Only require 2 months
        high_variance_threshold=0.50  # More lenient
    )
    
    result = estimator.estimate(transactions)
    
    print(f"\nWith custom parameters:")
    print(f"  Window Tolerance: ±3 days")
    print(f"  Minimum Months: 2")
    print(f"  Variance Threshold: 50%")
    print(f"\nResult:")
    print(f"  Income: {format_currency(result.estimated_income)}")
    print(f"  Confidence: {result.confidence}")


def main():
    """Run all examples."""
    setup_logging('INFO')
    
    print("\nPaySplit Income Estimator - Basic Usage Examples")
    print("="*70)
    
    example_1_simple_salary()
    example_2_multiple_streams()
    example_3_variable_income()
    example_4_custom_config()
    
    print("\n" + "="*70)
    print("Examples Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()