"""
PaySplit Income & Expense Estimator
====================================
Updated to handle BOTH income (inflows) and expenses (outflows).

Uses rule-based temporal clustering to identify recurring patterns.
"""

from typing import List, Dict
from statistics import median, stdev
import logging

from .models import Transaction, IncomeStream, IncomeEstimate
from .config import EstimatorConfig
from .utils import calculate_day_difference, get_month_key

logger = logging.getLogger(__name__)


class IncomeEstimator:
    """
    Estimates monthly income and expenses using temporal pattern detection.
    
    UPDATED: Now processes both inflows (income) and outflows (expenses).
    """
    
    def __init__(self,
                 window_tolerance: int = None,
                 min_months_present: int = None,
                 high_variance_threshold: float = None,
                 min_income_threshold: float = None):
        """
        Initialize the estimator.
        
        Args:
            window_tolerance: Days tolerance for grouping (default from config)
            min_months_present: Minimum months pattern must appear (default from config)
            high_variance_threshold: Threshold for high variance flag (default from config)
            min_income_threshold: Minimum total income (default from config)
        """
        self.window_tolerance = window_tolerance or EstimatorConfig.WINDOW_TOLERANCE_DAYS
        self.min_months_present = min_months_present or EstimatorConfig.MIN_MONTHS_PRESENT
        self.high_variance_threshold = (
            high_variance_threshold or EstimatorConfig.HIGH_VARIANCE_THRESHOLD
        )
        self.min_income_threshold = (
            min_income_threshold or EstimatorConfig.MIN_INCOME_THRESHOLD
        )
        
        logger.info(f"Initialized IncomeEstimator with tolerance={self.window_tolerance}")
    
    def preprocess_transactions(self,
                               transactions: List[Transaction],
                               flow_type: str = 'inflow',
                               excluded_categories: List[str] = None) -> List[Transaction]:
        """
        Filter transactions by flow type and excluded categories.
        
        Args:
            transactions: Raw transaction list
            flow_type: 'inflow' for income, 'outflow' for expenses
            excluded_categories: Categories to exclude
        
        Returns:
            Filtered list of transactions
        """
        if excluded_categories is None:
            excluded_categories = EstimatorConfig.EXCLUDED_CATEGORIES
        
        filtered = []
        
        for txn in transactions:
            # Skip excluded categories
            if txn.category.lower() in excluded_categories:
                continue
            
            # Filter by flow type
            if flow_type == 'inflow' and txn.amount > 0:
                filtered.append(txn)
            elif flow_type == 'outflow' and txn.amount < 0:
                filtered.append(txn)
        
        # Sort by date
        filtered.sort(key=lambda x: x.date)
        
        logger.info(
            f"Preprocessed {len(transactions)} -> {len(filtered)} {flow_type} transactions"
        )
        
        return filtered
    
    def _group_by_temporal_proximity(self,
                                     transactions: List[Transaction]) -> List[Dict]:
        """
        Group transactions by temporal proximity (day of month).
        
        Args:
            transactions: List of filtered transactions
        
        Returns:
            List of temporal groups
        """
        temporal_groups = []
        
        for txn in transactions:
            day_of_month = txn.date.day
            
            # Try to place in existing group
            placed = False
            for group in temporal_groups:
                day_diff = calculate_day_difference(day_of_month, group['center_day'])
                
                if day_diff <= self.window_tolerance:
                    group['transactions'].append(txn)
                    # Update center day (rolling average)
                    days = [t.date.day for t in group['transactions']]
                    group['center_day'] = sum(days) / len(days)
                    placed = True
                    break
            
            # Create new group if not placed
            if not placed:
                temporal_groups.append({
                    'center_day': day_of_month,
                    'transactions': [txn]
                })
        
        logger.debug(f"Created {len(temporal_groups)} temporal groups")
        return temporal_groups
    
    def _validate_persistence(self,
                             temporal_groups: List[Dict]) -> List[IncomeStream]:
        """
        Validate that patterns persist across required months.
        
        Args:
            temporal_groups: Groups of temporally-close transactions
        
        Returns:
            List of valid income streams
        """
        valid_streams = []
        
        for group in temporal_groups:
            # Get unique year-month combinations
            months_present = set(
                get_month_key(t.date) for t in group['transactions']
            )
            
            # Check if present in required number of months
            if len(months_present) >= self.min_months_present:
                # Use absolute values for amounts
                amounts = [abs(t.amount) for t in group['transactions']]
                median_amount = median(amounts)
                
                # Calculate variance
                amount_variance = stdev(amounts) if len(amounts) > 1 else 0.0
                
                stream = IncomeStream(
                    center_day=group['center_day'],
                    median_amount=median_amount,
                    transaction_count=len(amounts),
                    amount_variance=amount_variance,
                    transactions=group['transactions']
                )
                valid_streams.append(stream)
                
                logger.debug(
                    f"Valid stream: day={stream.center_day:.0f}, "
                    f"amount=${stream.median_amount:.2f}, "
                    f"count={stream.transaction_count}"
                )
        
        logger.info(f"Validated {len(valid_streams)} persistent streams")
        return valid_streams
    
    def _calculate_confidence(self, streams: List[IncomeStream]) -> str:
        """
        Determine confidence level based on stream characteristics.
        
        Args:
            streams: List of detected streams
        
        Returns:
            Confidence level: 'high', 'medium', 'low', or 'none'
        """
        if not streams:
            return 'none'
        
        # Check for high variance in any stream
        high_variance = any(
            (stream.amount_variance / stream.median_amount > self.high_variance_threshold)
            if stream.median_amount > 0 else False
            for stream in streams
        )
        
        # Check transaction count
        total_transactions = sum(s.transaction_count for s in streams)
        
        if high_variance or total_transactions < 4:
            confidence = 'medium'
        elif total_transactions >= 6:
            confidence = 'high'
        else:
            confidence = 'medium'
        
        logger.info(f"Calculated confidence: {confidence}")
        return confidence
    
    def _determine_recommendation(self,
                                  total_income: float,
                                  confidence: str) -> str:
        """
        Determine recommendation based on income and confidence.
        
        Args:
            total_income: Estimated total monthly income
            confidence: Confidence level
        
        Returns:
            Recommendation: 'APPROVE_ASSESSMENT', 'MANUAL_REVIEW', or 'DECLINE'
        """
        if confidence == 'none' or total_income < self.min_income_threshold:
            return 'MANUAL_REVIEW'
        elif confidence == 'low':
            return 'MANUAL_REVIEW'
        else:
            return 'APPROVE_ASSESSMENT'
    
    def estimate(self, 
                transactions: List[Transaction],
                flow_type: str = 'inflow') -> IncomeEstimate:
        """
        Estimate monthly amount for income or expenses.
        
        Process:
        1. Filter transactions by flow type
        2. Cluster by temporal proximity
        3. Filter clusters not present in all 3 months
        4. Calculate median for each persistent cluster
        5. Sum medians for total estimate
        
        Args:
            transactions: List of all transactions
            flow_type: 'inflow' for income, 'outflow' for expenses
        
        Returns:
            IncomeEstimate object with results
        """
        logger.info(f"Starting estimation for {flow_type} with {len(transactions)} transactions")
        
        # Step 1: Preprocess
        filtered_txns = self.preprocess_transactions(transactions, flow_type)
        
        if not filtered_txns:
            logger.warning(f"No valid {flow_type} transactions found")
            return IncomeEstimate(
                estimated_income=0.0,
                confidence='none',
                streams=[],
                recommendation='MANUAL_REVIEW',
                method_used='temporal_pattern_detection'
            )
        
        # Step 2: Group by temporal proximity
        temporal_groups = self._group_by_temporal_proximity(filtered_txns)
        
        # Step 3: Validate persistence
        valid_streams = self._validate_persistence(temporal_groups)
        
        # Step 4: Calculate total (sum of medians)
        total_amount = sum(stream.median_amount for stream in valid_streams)
        
        # Step 5: Determine confidence and recommendation
        confidence = self._calculate_confidence(valid_streams)
        recommendation = self._determine_recommendation(total_amount, confidence)
        
        logger.info(
            f"Estimation complete: {flow_type}=${total_amount:.2f}, "
            f"confidence={confidence}, recommendation={recommendation}"
        )
        
        return IncomeEstimate(
            estimated_income=total_amount,
            confidence=confidence,
            streams=valid_streams,
            recommendation=recommendation,
            method_used='temporal_pattern_detection'
        )
    
    def estimate_income_and_expenses(self, 
                                    transactions: List[Transaction]) -> Dict:
        """
        Estimate BOTH income and expenses from transactions.
        
        This is the main method to use for complete analysis.
        
        Args:
            transactions: List of all transactions
        
        Returns:
            Dictionary with income, expenses, and net income
        """
        logger.info("="*70)
        logger.info("Starting complete income & expense estimation")
        logger.info("="*70)
        
        # Estimate income (inflows)
        income_result = self.estimate(transactions, 'inflow')
        
        # Estimate expenses (outflows)
        expense_result = self.estimate(transactions, 'outflow')
        
        # Calculate net income
        net_income = income_result.estimated_income - expense_result.estimated_income
        
        # Overall recommendation
        if income_result.confidence == 'none':
            overall_recommendation = 'MANUAL_REVIEW'
        elif income_result.estimated_income < self.min_income_threshold:
            overall_recommendation = 'MANUAL_REVIEW'
        else:
            overall_recommendation = income_result.recommendation
        
        result = {
            'income': {
                'monthly_amount': income_result.estimated_income,
                'clusters': len(income_result.streams),
                'confidence': income_result.confidence,
                'streams': income_result.streams
            },
            'expenses': {
                'monthly_amount': expense_result.estimated_income,
                'clusters': len(expense_result.streams),
                'confidence': expense_result.confidence,
                'streams': expense_result.streams
            },
            'net_monthly_income': net_income,
            'recommendation': overall_recommendation
        }
        
        logger.info("="*70)
        logger.info(f"Income: ${income_result.estimated_income:,.2f}")
        logger.info(f"Expenses: ${expense_result.estimated_income:,.2f}")
        logger.info(f"Net Income: ${net_income:,.2f}")
        logger.info(f"Recommendation: {overall_recommendation}")
        logger.info("="*70)
        
        return result