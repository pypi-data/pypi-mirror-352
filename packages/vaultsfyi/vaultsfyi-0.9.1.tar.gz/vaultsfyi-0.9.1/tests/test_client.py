"""Tests for the VaultsSdk client."""

import unittest
from unittest.mock import patch, Mock
import json

from vaultsfyi import VaultsSdk, HttpResponseError, AuthenticationError


class TestVaultsSdk(unittest.TestCase):
    """Test cases for VaultsSdk class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.client = VaultsSdk(api_key=self.api_key)
    
    def test_initialization(self):
        """Test SDK initialization."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.api_base_url, "https://api.vaults.fyi")
        self.assertEqual(self.client.timeout, 30)
    
    def test_initialization_with_custom_url(self):
        """Test SDK initialization with custom base URL."""
        custom_url = "https://custom-api.example.com"
        client = VaultsSdk(api_key=self.api_key, api_base_url=custom_url)
        self.assertEqual(client.api_base_url, custom_url)
    
    @patch('vaultsfyi.client.requests.Session.request')
    def test_successful_request(self, mock_request):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": []}
        mock_request.return_value = mock_response
        
        result = self.client.get_benchmarks()
        
        # Verify request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]['method'], 'GET')
        self.assertEqual(call_args[1]['url'], 'https://api.vaults.fyi/v1/benchmarks')
        self.assertIn('x-api-key', call_args[1]['headers'])
        self.assertEqual(call_args[1]['headers']['x-api-key'], self.api_key)
        
        # Verify response
        self.assertEqual(result, {"success": True, "data": []})
    
    @patch('vaultsfyi.client.requests.Session.request')
    def test_authentication_error(self, mock_request):
        """Test authentication error handling."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        with self.assertRaises(AuthenticationError):
            self.client.get_benchmarks()
    
    @patch('vaultsfyi.client.requests.Session.request')
    def test_http_error(self, mock_request):
        """Test HTTP error handling."""
        # Mock 500 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(HttpResponseError) as context:
            self.client.get_benchmarks()
        
        self.assertEqual(context.exception.status_code, 500)
    
    def test_get_deposit_options_with_allowed_assets(self):
        """Test get_deposit_options with allowed_assets parameter."""
        user_address = "0x123"
        allowed_assets = ["USDC", "USDS"]
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {"data": []}
            
            self.client.get_deposit_options(user_address, allowed_assets=allowed_assets)
            
            # Verify the correct endpoint and parameters
            expected_endpoint = f"/v2/portfolio/best-deposit-options/{user_address}"
            expected_params = {"query": {"allowedAssets": allowed_assets}}
            
            mock_request.assert_called_once_with(expected_endpoint, expected_params)
    
    def test_get_actions_parameters(self):
        """Test get_actions method with all parameters."""
        action = "deposit"
        user_address = "0x123"
        network = "mainnet"
        vault_address = "0x456"
        amount = "1000000"
        asset_address = "0x789"
        
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {"data": []}
            
            self.client.get_actions(
                action=action,
                user_address=user_address,
                network=network,
                vault_address=vault_address,
                amount=amount,
                asset_address=asset_address,
                simulate=True
            )
            
            # Verify the correct endpoint and parameters
            expected_endpoint = f"/v2/transactions/{action}/{user_address}/{network}/{vault_address}"
            expected_params = {
                "query": {
                    "amount": amount,
                    "assetAddress": asset_address,
                    "simulate": True
                }
            }
            
            mock_request.assert_called_once_with(expected_endpoint, expected_params)


if __name__ == '__main__':
    unittest.main()