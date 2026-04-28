"""
Test Experian JSON Processing
==============================
Tests the processor with sample Experian FinSnap JSON data.

Run: python examples/test_experian_json.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from experian_processor import ExperianProcessor
import json


def test_with_sample_data():
    """Test with sample Experian JSON data (from your screenshots)."""
    
    print("="*70)
    print("TESTING EXPERIAN JSON PROCESSOR")
    print("="*70)
    
    # Sample data matching your Experian screenshot structure
    sample_experian_json = {
        "response_status": "Success",
        "transaction_stats": {
            "received_time": "2023-09-21T12:07:57",
            "response_time": "2023-09-21T12:07:57",
            "system_uuid": "6890287f-0e50-49e0-b11e-696f4cdbed73"
        },
        "return_data": {
            "fetched_data": {
                "fetch_accounts": [
                    {
                        "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                        "title": "John's Savings Account",
                        "credit_line": "0",
                        "available_balance": "0",
                        "current_balance": "0",
                        "currency": "ZAR",
                        "transactions": [
                            # INCOME TRANSACTIONS (positive amounts)
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "John Salary",
                                "title": "John Salary",
                                "transaction_date": "2023-08-25",
                                "amount": 10000,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 29,
                                    "title": "Salary/Regular Income"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "John Salary",
                                "title": "John Salary",
                                "transaction_date": "2023-09-25",
                                "amount": 10000,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 29,
                                    "title": "Salary/Regular Income"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "John Salary",
                                "title": "John Salary",
                                "transaction_date": "2023-10-25",
                                "amount": 10000,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 29,
                                    "title": "Salary/Regular Income"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Freelance Work",
                                "title": "Freelance",
                                "transaction_date": "2023-08-10",
                                "amount": 1500,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 30,
                                    "title": "Other Income"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Freelance Work",
                                "title": "Freelance",
                                "transaction_date": "2023-09-10",
                                "amount": 1600,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 30,
                                    "title": "Other Income"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Freelance Work",
                                "title": "Freelance",
                                "transaction_date": "2023-10-10",
                                "amount": 1550,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 30,
                                    "title": "Other Income"
                                }
                            },
                            
                            # EXPENSE TRANSACTIONS (negative amounts)
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Rent Payment",
                                "title": "Rent",
                                "transaction_date": "2023-08-01",
                                "amount": -5000,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 15,
                                    "title": "Rent"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Rent Payment",
                                "title": "Rent",
                                "transaction_date": "2023-09-01",
                                "amount": -5000,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 15,
                                    "title": "Rent"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Rent Payment",
                                "title": "Rent",
                                "transaction_date": "2023-10-01",
                                "amount": -5000,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 15,
                                    "title": "Rent"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Woolworths",
                                "title": "Groceries",
                                "transaction_date": "2023-08-05",
                                "amount": -1200,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 10,
                                    "title": "Groceries"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Woolworths",
                                "title": "Groceries",
                                "transaction_date": "2023-09-05",
                                "amount": -1150,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 10,
                                    "title": "Groceries"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Woolworths",
                                "title": "Groceries",
                                "transaction_date": "2023-10-05",
                                "amount": -1180,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 10,
                                    "title": "Groceries"
                                }
                            },
                            
                            # EXCLUDED CATEGORY (restaurants - category 22)
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Restaurant Meal",
                                "title": "Restaurant",
                                "transaction_date": "2023-08-15",
                                "amount": -800,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 22,
                                    "title": "Restaurants"
                                }
                            },
                            {
                                "account_id": "6ebe76c9fb411be97b3b0d48b791a7c9",
                                "full_title": "Restaurant Meal",
                                "title": "Restaurant",
                                "transaction_date": "2023-09-15",
                                "amount": -750,
                                "service_fee": 0,
                                "currency": "ZAR",
                                "category": {
                                    "id": 22,
                                    "title": "Restaurants"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    # Process the data
    processor = ExperianProcessor()
    result = processor.process_customer(sample_experian_json)
    
    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print("\n📊 INCOME:")
    print(f"  Monthly Amount: R{result['income']['monthly_amount']:,.2f}")
    print(f"  Clusters: {result['income']['clusters']}")
    print(f"  Confidence: {result['income']['confidence']}")
    
    if result['income']['details']:
        print("\n  Income Streams:")
        for i, stream in enumerate(result['income']['details'], 1):
            print(f"    {i}. Day {stream['day_of_month']}: R{stream['median_amount']:,.2f} "
                  f"({stream['occurrences']}x, {stream['consistency']})")
    
    print("\n📊 EXPENSES:")
    print(f"  Monthly Amount: R{result['expenses']['monthly_amount']:,.2f}")
    print(f"  Clusters: {result['expenses']['clusters']}")
    print(f"  Confidence: {result['expenses']['confidence']}")
    
    if result['expenses']['details']:
        print("\n  Expense Patterns:")
        for i, stream in enumerate(result['expenses']['details'], 1):
            print(f"    {i}. Day {stream['day_of_month']}: R{stream['median_amount']:,.2f} "
                  f"({stream['occurrences']}x, {stream['consistency']})")
    
    print("\n📊 SUMMARY:")
    print(f"  Net Monthly Income: R{result['net_monthly_income']:,.2f}")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Transactions Analyzed: {result['total_transactions_analyzed']}")
    
    # Verify expected results
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    
    # Expected: 2 income streams (salary R10,000 + freelance ~R1,550)
    expected_income = 10000 + 1550  # Approximately
    income_ok = abs(result['income']['monthly_amount'] - expected_income) < 100
    
    # Expected: 2 expense streams (rent R5,000 + groceries ~R1,180)
    # Restaurants should be EXCLUDED
    expected_expenses = 5000 + 1180  # Approximately
    expenses_ok = abs(result['expenses']['monthly_amount'] - expected_expenses) < 100
    
    # Check restaurants were excluded
    restaurants_excluded = result['expenses']['monthly_amount'] < 7000  # Should not include R800 restaurants
    
    print(f"✓ Income correct: {income_ok} (Expected ~R{expected_income:,.2f}, Got R{result['income']['monthly_amount']:,.2f})")
    print(f"✓ Expenses correct: {expenses_ok} (Expected ~R{expected_expenses:,.2f}, Got R{result['expenses']['monthly_amount']:,.2f})")
    print(f"✓ Restaurants excluded: {restaurants_excluded}")
    
    if income_ok and expenses_ok and restaurants_excluded:
        print("\n✅ All tests PASSED!")
    else:
        print("\n❌ Some tests FAILED - check the logic")
    
    # Save result
    print("\n" + "="*70)
    print("Saving results...")
    with open('output/test_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("✓ Saved to: output/test_result.json")


if __name__ == "__main__":
    test_with_sample_data()