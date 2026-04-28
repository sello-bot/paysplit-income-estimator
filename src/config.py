"""
Configuration management for PaySplit Income Estimator.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EstimatorConfig:
    """Configuration for income estimation."""
    
    # Temporal grouping parameters
    WINDOW_TOLERANCE_DAYS: int = int(os.getenv('WINDOW_TOLERANCE_DAYS', 2))
    
    # Validation parameters
    MIN_MONTHS_PRESENT: int = int(os.getenv('MIN_MONTHS_PRESENT', 3))
    
    # Risk thresholds
    HIGH_VARIANCE_THRESHOLD: float = float(os.getenv('HIGH_VARIANCE_THRESHOLD', 0.40))
    MIN_INCOME_THRESHOLD: float = float(os.getenv('MIN_INCOME_THRESHOLD', 500.0))
    
    # Transaction filtering
    EXCLUDED_CATEGORIES: List[str] = [
        'transfer',
        'internal_transfer',
        'refund',
        'reversal',
        'atm_withdrawal'
    ]
    
    @classmethod
    def validate(cls):
        """Validate configuration values."""
        assert cls.WINDOW_TOLERANCE_DAYS > 0, "Window tolerance must be positive"
        assert cls.MIN_MONTHS_PRESENT > 0, "Min months must be positive"
        assert 0 < cls.HIGH_VARIANCE_THRESHOLD < 1, "Variance threshold must be between 0 and 1"
        assert cls.MIN_INCOME_THRESHOLD >= 0, "Min income threshold must be non-negative"


class ExperianConfig:
    """Configuration for Experian API integration."""
    
    API_KEY: str = os.getenv('EXPERIAN_API_KEY', '')
    API_SECRET: str = os.getenv('EXPERIAN_API_SECRET', '')
    BASE_URL: str = os.getenv('EXPERIAN_BASE_URL', 'https://api.experian.com/v1')
    TIMEOUT_SECONDS: int = 30
    
    # Category mapping
    CATEGORY_MAPPING = {
        'SALARY': 'salary',
        'WAGE': 'salary',
        'INCOME': 'income',
        'PAYMENT': 'income',
        'TRANSFER': 'transfer',
        'INTERNAL_TRANSFER': 'internal_transfer',
        'REFUND': 'refund',
        'REVERSAL': 'reversal',
    }
    
    @classmethod
    def validate(cls):
        """Validate Experian configuration."""
        if not cls.API_KEY:
            raise ValueError("EXPERIAN_API_KEY not set")
        if not cls.API_SECRET:
            raise ValueError("EXPERIAN_API_SECRET not set")


class AppConfig:
    """General application configuration."""
    
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'