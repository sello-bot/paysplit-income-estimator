"""
Experian FinSnap Data Processor
================================
Processes Experian FinSnap JSON data for PaySplit income estimation.
"""

from datetime import datetime
from typing import List, Dict
import logging

from .models import Transaction
from .income_estimator import IncomeEstimator

logger = logging.getLogger(__name__)


# Categories to EXCLUDE (from your requirements)
EXCLUDED_CATEGORY_IDS = {
    3,    # charitable giving
    43,   # electronics/general merchandise
    7,    # entertainment/recreation
    114,  # expense reimbursement
    9,    # gifts
    13,   # home improvement
    104,  # postage/shipping
    227,  # refunds/adjustments
    22,   # restaurants
    40,   # savings
    36,   # securities trades
    23    # travel
}


class ExperianProcessor:
    """
    Process Experian FinSnap JSON data.
    
    Handles the exact JSON structure from Experian FinSnap API.
    """
    
    def __init__(self):
        """Initialize the processor."""
        self.estimator = IncomeEstimator()
        logger.info("Initialized ExperianProcessor")
    
    def parse_experian_json(self, json_data: Dict) -> List[Transaction]:
        """
        Parse Experian FinSnap JSON into Transaction objects.
        
        Args:
            json_data: Complete Experian FinSnap JSON response
        
        Returns:
            List of Transaction objects
        """
        transactions = []
        
        try:
            # Navigate to accounts
            return_data = json_data.get('return_data', {})
            fetched_data = return_data.get('fetched_data', {})
            fetch_accounts = fetched_data.get('fetch_accounts', [])
            
            logger.info(f"Found {len(fetch_accounts)} accounts in Experian data")
            
            for account in fetch_accounts:
                account_id = account.get('account_id', '')
                account_txns = account.get('transactions', [])
                
                logger.info(f"Processing account {account_id}: {len(account_txns)} transactions")
                
                for txn_data in account_txns:
                    try:
                        # Extract transaction data
                        date_str = txn_data.get('transaction_date', '')
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        
                        amount = float(txn_data.get('amount', 0))
                        
                        # Get category
                        category = txn_data.get('category', {})
                        category_id = category.get('id', 0)
                        category_title = category.get('title', 'Unknown')
                        
                        # Check if category should be excluded
                        if category_id in EXCLUDED_CATEGORY_IDS:
                            logger.debug(f"Excluding transaction: category {category_id} - {category_title}")
                            continue
                        
                        # Get description
                        full_title = txn_data.get('full_title', '')
                        title = txn_data.get('title', '')
                        
                        transaction = Transaction(
                            date=date,
                            amount=amount,
                            category=category_title,
                            description=full_title or title
                        )
                        
                        transactions.append(transaction)
                        
                    except (ValueError, KeyError, TypeError) as e:
                        logger.warning(f"Skipping invalid transaction: {e}")
                        continue
            
            logger.info(f"Parsed {len(transactions)} valid transactions from Experian data")
            
        except Exception as e:
            logger.error(f"Error parsing Experian JSON: {e}")
            raise
        
        return transactions
    
    def process_customer(self, experian_json: Dict) -> Dict:
        """
        Complete processing for a customer's Experian data.
        
        Args:
            experian_json: Complete Experian FinSnap JSON response
        
        Returns:
            Dictionary with income, expenses, net income, and recommendation
        """
        logger.info("="*70)
        logger.info("Processing customer Experian data")
        logger.info("="*70)
        
        # Parse JSON to transactions
        transactions = self.parse_experian_json(experian_json)
        
        if not transactions:
            logger.warning("No valid transactions found")
            return {
                'income': {
                    'monthly_amount': 0.0,
                    'clusters': 0,
                    'confidence': 'none',
                    'details': []
                },
                'expenses': {
                    'monthly_amount': 0.0,
                    'clusters': 0,
                    'confidence': 'none',
                    'details': []
                },
                'net_monthly_income': 0.0,
                'recommendation': 'MANUAL_REVIEW',
                'error': 'No valid transactions found'
            }
        
        # Estimate income and expenses
        result = self.estimator.estimate_income_and_expenses(transactions)
        
        # Format for output
        formatted_result = {
            'income': {
                'monthly_amount': result['income']['monthly_amount'],
                'clusters': result['income']['clusters'],
                'confidence': result['income']['confidence'],
                'details': [
                    {
                        'day_of_month': int(stream.center_day),
                        'median_amount': stream.median_amount,
                        'occurrences': stream.transaction_count,
                        'variance': stream.amount_variance,
                        'consistency': self._get_consistency_rating(stream)
                    }
                    for stream in result['income']['streams']
                ]
            },
            'expenses': {
                'monthly_amount': result['expenses']['monthly_amount'],
                'clusters': result['expenses']['clusters'],
                'confidence': result['expenses']['confidence'],
                'details': [
                    {
                        'day_of_month': int(stream.center_day),
                        'median_amount': stream.median_amount,
                        'occurrences': stream.transaction_count,
                        'variance': stream.amount_variance,
                        'consistency': self._get_consistency_rating(stream)
                    }
                    for stream in result['expenses']['streams']
                ]
            },
            'net_monthly_income': result['net_monthly_income'],
            'recommendation': result['recommendation'],
            'total_transactions_analyzed': len(transactions)
        }
        
        return formatted_result
    
    def _get_consistency_rating(self, stream) -> str:
        """Get consistency rating for a stream."""
        if stream.median_amount == 0:
            return "N/A"
        
        cv = stream.amount_variance / stream.median_amount
        
        if cv < 0.10:
            return "Very Stable"
        elif cv < 0.25:
            return "Stable"
        elif cv < 0.40:
            return "Moderate"
        else:
            return "Variable"