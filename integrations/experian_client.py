"""
Experian API integration client.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from src.models import Transaction
from src.config import ExperianConfig

logger = logging.getLogger(__name__)


class ExperianAPIError(Exception):
    """Exception for Experian API errors."""
    pass


class ExperianClient:
    """Client for interacting with Experian API."""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """
        Initialize Experian client.
        
        Args:
            api_key: Experian API key (default from config)
            api_secret: Experian API secret (default from config)
        """
        self.api_key = api_key or ExperianConfig.API_KEY
        self.api_secret = api_secret or ExperianConfig.API_SECRET
        self.base_url = ExperianConfig.BASE_URL
        self.timeout = ExperianConfig.TIMEOUT_SECONDS
        
        self.token = None
        self.token_expiry = None
        
        logger.info("Initialized Experian client")
    
    def authenticate(self):
        """Authenticate with Experian API and get OAuth token."""
        try:
            logger.info("Authenticating with Experian API")
            
            response = requests.post(
                f"{self.base_url}/oauth/token",
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.api_key,
                    'client_secret': self.api_secret
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            self.token = data['access_token']
            self.token_expiry = datetime.now() + timedelta(seconds=data['expires_in'])
            
            logger.info("Successfully authenticated with Experian")
            
        except requests.RequestException as e:
            logger.error(f"Experian authentication failed: {e}")
            raise ExperianAPIError(f"Authentication failed: {e}")
    
    def _ensure_authenticated(self):
        """Ensure we have a valid authentication token."""
        if not self.token or datetime.now() >= self.token_expiry:
            self.authenticate()
    
    def get_transactions(self,
                        customer_id: str,
                        months: int = 3) -> Dict:
        """
        Retrieve bank statement transactions for a customer.
        
        Args:
            customer_id: Customer identifier
            months: Number of months to retrieve (default: 3)
        
        Returns:
            Dictionary with transaction data
        """
        self._ensure_authenticated()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        try:
            logger.info(f"Fetching transactions for customer {customer_id}")
            
            response = requests.get(
                f"{self.base_url}/bank-statements/transactions",
                headers={'Authorization': f'Bearer {self.token}'},
                params={
                    'customer_id': customer_id,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data.get('transactions', []))} transactions")
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch transactions: {e}")
            raise ExperianAPIError(f"Failed to fetch transactions: {e}")
    
    @staticmethod
    def transform_to_transactions(experian_data: Dict) -> List[Transaction]:
        """
        Transform Experian API response to Transaction objects.
        
        Args:
            experian_data: Raw Experian API response
        
        Returns:
            List of Transaction objects
        """
        transactions = []
        
        for txn_data in experian_data.get('transactions', []):
            try:
                # Parse date
                date = datetime.fromisoformat(txn_data['date'])
                
                # Get amount
                amount = float(txn_data['amount'])
                
                # Map category
                category = ExperianConfig.CATEGORY_MAPPING.get(
                    txn_data['category'],
                    'income'
                ).lower()
                
                # Get description
                description = txn_data.get('description', '')
                
                transactions.append(
                    Transaction(
                        date=date,
                        amount=amount,
                        category=category,
                        description=description
                    )
                )
                
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid transaction: {e}")
                continue
        
        logger.info(f"Transformed {len(transactions)} valid transactions")
        return transactions