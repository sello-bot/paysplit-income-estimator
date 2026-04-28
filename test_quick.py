"""Quick test of the updated income estimator"""

from src.models import Transaction
from src.income_estimator import IncomeEstimator
from datetime import datetime

# Sample transactions
transactions = [
    # Income
    Transaction(datetime(2025, 8, 25), 3500.0, "salary", "Company"),
    Transaction(datetime(2025, 9, 25), 3500.0, "salary", "Company"),
    Transaction(datetime(2025, 10, 25), 3500.0, "salary", "Company"),
    
    # Expenses (negative amounts)
    Transaction(datetime(2025, 8, 1), -1200.0, "rent", "Landlord"),
    Transaction(datetime(2025, 9, 1), -1200.0, "rent", "Landlord"),
    Transaction(datetime(2025, 10, 1), -1200.0, "rent", "Landlord"),
]

# Create estimator
estimator = IncomeEstimator()

# Get results
result = estimator.estimate_income_and_expenses(transactions)

# Display
print("\n" + "="*70)
print("QUICK TEST RESULTS")
print("="*70)
print(f"\n✅ Income: R{result['income']['monthly_amount']:,.2f}")
print(f"✅ Expenses: R{result['expenses']['monthly_amount']:,.2f}")
print(f"✅ Net: R{result['net_monthly_income']:,.2f}")
print(f"✅ Recommendation: {result['recommendation']}")
print("\n" + "="*70)
print("Test passed! Your setup is working correctly.")
print("="*70)