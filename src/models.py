"""
Data models for PaySplit Income Estimator.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Transaction:
    """Represents a single bank transaction."""
    date: datetime
    amount: float
    category: str
    description: str
    
    def __post_init__(self):
        """Validate transaction data."""
        # Allow both positive (income) and negative (expense) amounts
        if self.amount == 0:
            raise ValueError("Transaction amount cannot be zero")
        if not isinstance(self.date, datetime):
            raise TypeError("Date must be a datetime object")


@dataclass
class IncomeStream:
    """Represents a detected income stream."""
    center_day: float
    median_amount: float
    transaction_count: int
    amount_variance: float
    transactions: List[Transaction]
    
    def get_consistency_rating(self) -> str:
        """Rate the consistency of this income stream."""
        if self.median_amount == 0:
            return "N/A"
        
        cv = self.amount_variance / self.median_amount
        
        if cv < 0.10:
            return "Very Stable"
        elif cv < 0.25:
            return "Stable"
        elif cv < 0.40:
            return "Moderate"
        else:
            return "Variable"


@dataclass
class IncomeEstimate:
    """Result of income estimation analysis."""
    estimated_income: float
    confidence: str
    streams: List[IncomeStream]
    recommendation: str
    method_used: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'estimated_income': self.estimated_income,
            'confidence': self.confidence,
            'streams': [
                {
                    'center_day': s.center_day,
                    'median_amount': s.median_amount,
                    'transaction_count': s.transaction_count,
                    'amount_variance': s.amount_variance,
                    'consistency': s.get_consistency_rating()
                }
                for s in self.streams
            ],
            'recommendation': self.recommendation,
            'method_used': self.method_used
        }