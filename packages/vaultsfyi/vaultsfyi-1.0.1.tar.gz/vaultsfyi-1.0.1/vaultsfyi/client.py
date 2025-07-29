"""Main client for the Vaults.fyi SDK."""

import json
from typing import Dict, Any, Optional, Union, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import HttpResponseError, AuthenticationError, ForbiddenError, RateLimitError, NetworkError
from .utils import generate_query_params


class VaultsSdk:
    """Python SDK for interacting with the Vaults.fyi API."""
    
    def __init__(
        self, 
        api_key: str, 
        api_base_url: str = "https://api.vaults.fyi",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize the Vaults.fyi SDK client.
        
        Args:
            api_key: Your Vaults.fyi API key
            api_base_url: Base URL for the API (default: https://api.vaults.fyi)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip('/')
        self.timeout = timeout
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """Make HTTP request to the API.
        
        Args:
            endpoint: API endpoint path
            params: Request parameters (path and query params)
            method: HTTP method (GET or POST)
            
        Returns:
            JSON response data
            
        Raises:
            HttpResponseError: When API returns an error
            AuthenticationError: When API key is invalid
            RateLimitError: When rate limit is exceeded
            NetworkError: When network/connection issues occur
        """
        # Extract query parameters
        query_params = params.get('query', {}) if params else {}
        query_string = generate_query_params(query_params)
        
        # Build full URL
        url = f"{self.api_base_url}{endpoint}{query_string}"
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }
        
        # Prepare request body for POST requests
        body = None
        if method == "POST" and params and 'body' in params:
            body = json.dumps(params['body'])
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=self.timeout
            )
            
            # Handle different status codes
            if response.status_code == 401:
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'API key required')
                    error_id = error_data.get('errorId')
                    raise AuthenticationError(error_message, error_id)
                except (ValueError, KeyError):
                    raise AuthenticationError("Invalid API key")
            elif response.status_code == 403:
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Forbidden - insufficient permissions or credits exhausted')
                    error_id = error_data.get('errorId')
                    raise ForbiddenError(error_message, error_id)
                except (ValueError, KeyError):
                    raise ForbiddenError("Forbidden - insufficient permissions or credits exhausted")
            elif response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
            elif not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', f'HTTP {response.status_code}')
                except:
                    error_message = f'HTTP {response.status_code}: {response.text}'
                
                raise HttpResponseError(
                    error_message, 
                    status_code=response.status_code,
                    response_data=error_data if 'error_data' in locals() else None
                )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    # V1 API Methods
    
    def get_benchmarks(self) -> Dict[str, Any]:
        """Get benchmark data.
        
        Returns:
            Benchmark data
        """
        return self._make_request("/v1/benchmarks")
    
    # V2 API Methods
    
    def get_vault_historical_data(
        self,
        network: str,
        vault_address: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get historical data for a specific vault.
        
        Args:
            network: Network name (e.g., 'mainnet', 'base', 'arbitrum')
            vault_address: Vault contract address
            **kwargs: Additional query parameters
            
        Returns:
            Historical vault data
        """
        endpoint = f"/v2/historical/{network}/{vault_address}"
        params = {"query": kwargs} if kwargs else None
        return self._make_request(endpoint, params)
    
    def get_vault_total_returns(
        self,
        user_address: str,
        network: str,
        vault_address: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get total returns for a user in a specific vault.
        
        Args:
            user_address: User's wallet address
            network: Network name
            vault_address: Vault contract address
            **kwargs: Additional query parameters
            
        Returns:
            Total returns data
        """
        endpoint = f"/v2/portfolio/returns/{user_address}/{network}/{vault_address}"
        params = {"query": kwargs} if kwargs else None
        return self._make_request(endpoint, params)
    
    def get_positions(self, user_address: str, **kwargs) -> Dict[str, Any]:
        """Get all positions for a user.
        
        Args:
            user_address: User's wallet address
            **kwargs: Additional query parameters
            
        Returns:
            User positions data
        """
        endpoint = f"/v2/portfolio/positions/{user_address}"
        params = {"query": kwargs} if kwargs else None
        return self._make_request(endpoint, params)
    
    def get_deposit_options(
        self, 
        user_address: str, 
        allowed_assets: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get best deposit options for a user.
        
        Args:
            user_address: User's wallet address
            allowed_assets: List of allowed asset symbols (e.g., ['USDC', 'USDS'])
            **kwargs: Additional query parameters
            
        Returns:
            Best deposit options data
        """
        endpoint = f"/v2/portfolio/best-deposit-options/{user_address}"
        query_params = kwargs.copy()
        if allowed_assets:
            query_params['allowedAssets'] = allowed_assets
        
        params = {"query": query_params} if query_params else None
        return self._make_request(endpoint, params)
    
    def get_vault_holder_events(
        self,
        user_address: str,
        network: str,
        vault_address: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get events for a vault holder.
        
        Args:
            user_address: User's wallet address
            network: Network name
            vault_address: Vault contract address
            **kwargs: Additional query parameters
            
        Returns:
            Vault holder events data
        """
        endpoint = f"/v2/portfolio/events/{user_address}/{network}/{vault_address}"
        params = {"query": kwargs} if kwargs else None
        return self._make_request(endpoint, params)
    
    def get_all_vaults(self, **kwargs) -> Dict[str, Any]:
        """Get all available vaults.
        
        Args:
            **kwargs: Query parameters for filtering
            
        Returns:
            All vaults data
        """
        endpoint = "/v2/detailed-vaults"
        params = {"query": kwargs} if kwargs else None
        return self._make_request(endpoint, params)
    
    def get_vault(self, network: str, vault_address: str, **kwargs) -> Dict[str, Any]:
        """Get detailed information for a specific vault.
        
        Args:
            network: Network name
            vault_address: Vault contract address
            **kwargs: Additional query parameters
            
        Returns:
            Detailed vault data
        """
        endpoint = f"/v2/detailed-vaults/{network}/{vault_address}"
        params = {"query": kwargs} if kwargs else None
        return self._make_request(endpoint, params)
    
    def get_idle_assets(self, user_address: str, **kwargs) -> Dict[str, Any]:
        """Get idle assets for a user.
        
        Args:
            user_address: User's wallet address
            **kwargs: Additional query parameters
            
        Returns:
            Idle assets data
        """
        endpoint = f"/v2/portfolio/idle-assets/{user_address}"
        params = {"query": kwargs} if kwargs else None
        return self._make_request(endpoint, params)
    
    def get_transactions_context(
        self,
        user_address: str,
        network: str,
        vault_address: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get transaction context for a user and vault.
        
        Args:
            user_address: User's wallet address
            network: Network name
            vault_address: Vault contract address
            **kwargs: Additional query parameters
            
        Returns:
            Transaction context data
        """
        endpoint = f"/v2/transactions/context/{user_address}/{network}/{vault_address}"
        params = {"query": kwargs} if kwargs else None
        return self._make_request(endpoint, params)
    
    def get_actions(
        self,
        action: str,
        user_address: str,
        network: str,
        vault_address: str,
        amount: Optional[str] = None,
        asset_address: Optional[str] = None,
        simulate: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Get transaction actions for deposit/withdraw operations.
        
        Args:
            action: Action type ('deposit', 'redeem', etc.)
            user_address: User's wallet address
            network: Network name
            vault_address: Vault contract address
            amount: Amount for the transaction
            asset_address: Asset contract address
            simulate: Whether to simulate the transaction
            **kwargs: Additional query parameters
            
        Returns:
            Transaction action data
        """
        endpoint = f"/v2/transactions/{action}/{user_address}/{network}/{vault_address}"
        
        query_params = kwargs.copy()
        if amount is not None:
            query_params['amount'] = amount
        if asset_address is not None:
            query_params['assetAddress'] = asset_address
        query_params['simulate'] = simulate
        
        params = {"query": query_params} if query_params else None
        return self._make_request(endpoint, params)