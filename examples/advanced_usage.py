"""
Advanced usage examples including Experian integration.
"""

from unittest.mock import Mock, patch
from datetime import datetime

from src.income_estimator import IncomeEstimator
from integrations.experian_client import ExperianClient
from src.utils import setup_logging, format_currency


def example_experian_integration():
    """Example: Full Experian integration flow."""
    print("\n" + "="*70)
    print("ADVANCED EXAMPLE: Experian API Integration")
    print("="*70)
    
    # Mock Experian API response
    mock_experian_data = {
        'transactions': [
            {
                'date': '2025-08-25T00:00:00',
                'amount': 3500.0,
                'category': 'SALARY',
                'description': 'ACME CORP PAYROLL'
            },
            {
                'date': '2025-09-25T00:00:00',
                'amount': 3500.0,
                'category': 'SALARY',
                'description': 'ACME CORP PAYROLL'
            },
            {
                'date': '2025-10-25T00:00:00',
                'amount': 3500.0,
                'category': 'SALARY',
                'description': 'ACME CORP PAYROLL'
            },
            {
                'date': '2025-09-05T00:00:00',
                'amount': 500.0,
                'category': 'TRANSFER',
                'description': 'TRANSFER FROM SAVINGS'
            }
        ]
    }
    
    print("\nStep 1: Transform Experian data")
    transactions = ExperianClient.transform_to_transactions(mock_experian_data)
    print(f"  Transformed {len(transactions)} transactions")
    
    print("\nStep 2: Estimate income")
    estimator = IncomeEstimator()
    result = estimator.estimate(transactions)
    
    print(f"\nResults:")
    print(f"  Estimated Income: {format_currency(result.estimated_income)}")
    print(f"  Confidence: {result.confidence.upper()}")
    print(f"  Recommendation: {result.recommendation}")
    print(f"  Streams Detected: {len(result.streams)}")
    
    print("\nStep 3: Export results as JSON")
    result_dict = result.to_dict()
    print(f"  Exported: {result_dict}")


def example_error_handling():
    """Example: Proper error handling."""
    print("\n" + "="*70)
    print("ADVANCED EXAMPLE: Error Handling")
    print("="*70)
    
    from examples.sample_data import get_standard_salary_scenario
    
    try:
        transactions = get_standard_salary_scenario()
        estimator = IncomeEstimator()
        result = estimator.estimate(transactions)
        
        if result.recommendation == 'MANUAL_REVIEW':
            print("\n⚠️  Manual review required")
            print(f"  Reason: {result.confidence} confidence")
            print(f"  Income: {format_currency(result.estimated_income)}")
        else:
            print("\n✅ Assessment approved")
            print(f"  Income: {format_currency(result.estimated_income)}")
    
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("  Fallback: Route to manual review")


def example_batch_processing():
    """Example: Process multiple customers."""
    print("\n" + "="*70)
    print("ADVANCED EXAMPLE: Batch Processing")
    print("="*70)
    
    from examples.sample_data import (
        get_standard_salary_scenario,
        get_salary_plus_freelance_scenario,
        get_variable_income_scenario
    )
    
    # Simulate multiple customers
    customers = [
        {'id': 'CUST001', 'transactions': get_standard_salary_scenario()},
        {'id': 'CUST002', 'transactions': get_salary_plus_freelance_scenario()},
        {'id': 'CUST003', 'transactions': get_variable_income_scenario()},
    ]
    
    estimator = IncomeEstimator()
    results = []
    
    print(f"\nProcessing {len(customers)} customers...\n")
    
    for customer in customers:
        result = estimator.estimate(customer['transactions'])
        results.append({
            'customer_id': customer['id'],
            'income': result.estimated_income,
            'confidence': result.confidence,
            'recommendation': result.recommendation
        })
        
        print(f"  {customer['id']}: "
              f"Income={format_currency(result.estimated_income)}, "
              f"Confidence={result.confidence}, "
              f"Recommendation={result.recommendation}")
    
    print(f"\n✅ Processed {len(results)} customers")
    
    # Summary statistics
    total_approved = sum(1 for r in results if r['recommendation'] == 'APPROVE_ASSESSMENT')
    total_review = sum(1 for r in results if r['recommendation'] == 'MANUAL_REVIEW')
    
    print(f"\nSummary:")
    print(f"  Approved: {total_approved}")
    print(f"  Manual Review: {total_review}")


def main():
    """Run all advanced examples."""
    setup_logging('INFO')
    
    print("\nPaySplit Income Estimator - Advanced Usage Examples")
    print("="*70)
    
    example_experian_integration()
    example_error_handling()
    example_batch_processing()
    
    print("\n" + "="*70)
    print("Advanced Examples Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()