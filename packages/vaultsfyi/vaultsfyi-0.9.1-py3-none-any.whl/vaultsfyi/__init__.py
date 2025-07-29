"""Vaults.fyi Python SDK

A Python SDK for interacting with the Vaults.fyi API.
"""

from .client import VaultsSdk
from .exceptions import (
    VaultsFyiError,
    HttpResponseError,
    AuthenticationError,
    ForbiddenError,
    ValidationError,
    RateLimitError,
    NetworkError,
)

__version__ = "1.0.1"
__author__ = "Kaimi Seeker"
__email__ = "kaimi@wallfacer.io"

__all__ = [
    "VaultsSdk",
    "VaultsFyiError",
    "HttpResponseError", 
    "AuthenticationError",
    "ForbiddenError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
]