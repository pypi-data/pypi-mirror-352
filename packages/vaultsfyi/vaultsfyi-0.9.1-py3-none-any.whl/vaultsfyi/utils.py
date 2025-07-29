"""Utility functions for the Vaults.fyi SDK."""

from typing import Dict, Any, Optional
from urllib.parse import urlencode


def generate_query_params(params: Optional[Dict[str, Any]]) -> str:
    """Generate query string from parameters dictionary.
    
    Args:
        params: Dictionary of query parameters
        
    Returns:
        Query string with leading '?' if params exist, empty string otherwise
    """
    if not params:
        return ""
    
    # Handle list parameters by creating multiple key=value pairs
    query_pairs = []
    for key, value in params.items():
        if value is not None:
            if isinstance(value, list):
                # Create multiple parameters for list values
                for item in value:
                    query_pairs.append((key, str(item)))
            elif isinstance(value, bool):
                # Convert boolean to lowercase string
                query_pairs.append((key, str(value).lower()))
            else:
                query_pairs.append((key, str(value)))
    
    if not query_pairs:
        return ""
    
    return "?" + urlencode(query_pairs)


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase.
    
    Args:
        snake_str: String in snake_case format
        
    Returns:
        String in camelCase format
    """
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase to snake_case.
    
    Args:
        camel_str: String in camelCase format
        
    Returns:
        String in snake_case format
    """
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()