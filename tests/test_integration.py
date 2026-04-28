"""
Integration tests for Experian API client.
Note: These tests require valid API credentials.
"""

import pytest
from unittest.mock import Mock, patch

from integrations.experian_client import ExperianClient, ExperianAPIError
from src.models import Transaction


class TestExperianIntegration:
    """Test suite for Experian integration."""
    
    @patch('integrations.experian_client.requests.post')
    def test_authentication_success(self, mock_post):
        """Test successful authentication."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_token_123',
            'expires_in': 3600
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = ExperianClient(api_key='test_key', api_secret='test_secret')
        client.authenticate()
        
        assert client.token == 'test_token_123'
        assert client.token_expiry is not None
    
    @patch('integrations.experian_client.requests.post')
    def test_authentication_failure(self, mock_post):
        """Test authentication failure handling."""
        mock_post.side_effect = Exception("Connection error")
        
        client = ExperianClient(api_key='test_key', api_secret='test_secret')
        
        with pytest.raises(ExperianAPIError):
            client.authenticate()
    
    def test_transaction_transformation(self):
        """Test transformation of Experian data to Transaction objects."""
        experian_data = {
            'transactions': [
                {
                    'date': '2025-08-25T00:00:00',
                    'amount': 3500.0,
                    'category': 'SALARY',
                    'description': 'Company Payroll'
                },
                {
                    'date': '2025-09-25T00:00:00',
                    'amount': 3500.0,
                    'category': 'SALARY',
                    'description': 'Company Payroll'
                }
            ]
        }
        
        transactions = ExperianClient.transform_to_transactions(experian_data)
        
        assert len(transactions) == 2
        assert all(isinstance(t, Transaction) for t in transactions)
        assert transactions[0].category == 'salary'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])