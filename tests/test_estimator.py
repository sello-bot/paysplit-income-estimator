"""
Unit tests for IncomeEstimator.
"""

import pytest
from datetime import datetime

from src.models import Transaction
from src.income_estimator import IncomeEstimator


class TestIncomeEstimator:
    """Test suite for IncomeEstimator."""
    
    def test_standard_salary(self):
        """Test detection of regular monthly salary."""
        transactions = [
            Transaction(datetime(2025, 8, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 9, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 10, 25), 3500.0, "salary", "Company"),
        ]
        
        estimator = IncomeEstimator()
        result = estimator.estimate(transactions)
        
        assert result.estimated_income == 3500.0
        assert len(result.streams) == 1
        assert result.confidence in ['high', 'medium']
        assert result.recommendation == 'APPROVE_ASSESSMENT'
    
    def test_weekend_variation(self):
        """Test salary with weekend payment shifts."""
        transactions = [
            Transaction(datetime(2025, 8, 30), 3000.0, "salary", "Company"),
            Transaction(datetime(2025, 9, 28), 3000.0, "salary", "Company"),
            Transaction(datetime(2025, 10, 29), 3000.0, "salary", "Company"),
        ]
        
        estimator = IncomeEstimator(window_tolerance=2)
        result = estimator.estimate(transactions)
        
        assert len(result.streams) == 1
        assert result.estimated_income == 3000.0
    
    def test_multiple_streams(self):
        """Test detection of multiple income sources."""
        transactions = [
            # Salary
            Transaction(datetime(2025, 8, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 9, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 10, 25), 3500.0, "salary", "Company"),
            # Freelance
            Transaction(datetime(2025, 8, 10), 800.0, "income", "Client"),
            Transaction(datetime(2025, 9, 10), 850.0, "income", "Client"),
            Transaction(datetime(2025, 10, 10), 900.0, "income", "Client"),
        ]
        
        estimator = IncomeEstimator()
        result = estimator.estimate(transactions)
        
        assert len(result.streams) == 2
        assert result.estimated_income > 4000.0
    
    def test_one_time_payment_filtered(self):
        """Test that one-time payments are excluded."""
        transactions = [
            Transaction(datetime(2025, 8, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 9, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 10, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 9, 15), 5000.0, "income", "Bonus"),
        ]
        
        estimator = IncomeEstimator()
        result = estimator.estimate(transactions)
        
        assert len(result.streams) == 1
        assert result.estimated_income == 3500.0
    
    def test_transfers_excluded(self):
        """Test that transfers are excluded."""
        transactions = [
            Transaction(datetime(2025, 8, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 9, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 10, 25), 3500.0, "salary", "Company"),
            Transaction(datetime(2025, 8, 5), 1000.0, "transfer", "Savings"),
            Transaction(datetime(2025, 9, 3), 200.0, "refund", "Store"),
        ]
        
        estimator = IncomeEstimator()
        result = estimator.estimate(transactions)
        
        assert result.estimated_income == 3500.0
    
    def test_no_persistent_pattern(self):
        """Test handling of irregular transactions."""
        transactions = [
            Transaction(datetime(2025, 8, 5), 1000.0, "income", "Random"),
            Transaction(datetime(2025, 9, 15), 1500.0, "income", "Random"),
            Transaction(datetime(2025, 10, 22), 800.0, "income", "Random"),
        ]
        
        estimator = IncomeEstimator()
        result = estimator.estimate(transactions)
        
        assert result.confidence == 'none'
        assert result.recommendation == 'MANUAL_REVIEW'
    
    def test_empty_transactions(self):
        """Test handling of empty transaction list."""
        estimator = IncomeEstimator()
        result = estimator.estimate([])
        
        assert result.estimated_income == 0.0
        assert result.confidence == 'none'
        assert result.recommendation == 'MANUAL_REVIEW'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])