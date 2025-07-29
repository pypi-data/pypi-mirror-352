"""Exception classes for the Vaults.fyi SDK."""


class VaultsFyiError(Exception):
    """Base exception class for Vaults.fyi SDK errors."""
    pass


class HttpResponseError(VaultsFyiError):
    """Exception raised when HTTP request fails."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(VaultsFyiError):
    """Exception raised when API key authentication fails."""
    
    def __init__(self, message: str, error_id: str = None):
        super().__init__(message)
        self.error_id = error_id


class ForbiddenError(VaultsFyiError):
    """Exception raised when API key has exhausted credits or lacks permissions."""
    
    def __init__(self, message: str, error_id: str = None):
        super().__init__(message)
        self.error_id = error_id


class ValidationError(VaultsFyiError):
    """Exception raised when request validation fails."""
    pass


class RateLimitError(VaultsFyiError):
    """Exception raised when API rate limit is exceeded."""
    pass


class NetworkError(VaultsFyiError):
    """Exception raised when network/connection issues occur."""
    pass