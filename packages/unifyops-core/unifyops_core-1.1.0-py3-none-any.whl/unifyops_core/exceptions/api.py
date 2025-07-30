"""
API Exceptions
=============

This module contains exceptions related to external API interactions.
These exceptions are used when making requests to external APIs and handling responses.

Examples:
---------

```python
from unifyops_core.exceptions import ApiClientError

# Raise an API client configuration error
raise ApiClientError(
    message="Invalid API client configuration",
    details=[{"loc": ["api_key"], "msg": "API key is missing"}]
)

# Raise an API response error
from unifyops_core.exceptions import ApiResponseError

raise ApiResponseError(
    message="Failed to parse API response",
    details=[{"loc": ["response", "data"], "msg": "Unexpected response format"}],
    status_code=502
)
"""

from fastapi import status
from typing import List, Dict, Any, Optional, Union
from unifyops_core.exceptions.base import AppException


class ApiError(AppException):
    """Base exception for all API-related errors."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_type = "api_error"


class ApiClientError(ApiError):
    """
    Exception raised when there's an error with the API client configuration
    or request preparation.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    error_type = "api_client_error"
    
    def __init__(
        self,
        message: str = "API client error",
        details: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        super().__init__(message=message, details=details, **kwargs)


class ApiResponseError(ApiError):
    status_code = status.HTTP_502_BAD_GATEWAY
    error_type  = "api_response_error"

    def __init__(
        self,
        message: str = "API response error",
        details: Optional[List[Dict[str, Any]]] = None,
        *,
        status_code: Optional[int] = None,
        service: Optional[str] = None,
        response_body: Optional[Union[str, Dict[str, Any]]] = None
    ):
        # 1) override the default status_code if provided
        if status_code is not None:
            self.status_code = status_code

        # 2) build a single metadata dict for all your extra fields
        meta: Dict[str, Any] = {}
        if service is not None:
            meta["service"] = service

        if response_body is not None:
            # if it’s JSON, keep it as-is; if string, wrap it
            meta["response_body"] = (
                response_body
                if isinstance(response_body, dict)
                else str(response_body)
            )

        # 3) merge into the existing details list (or start a new one)
        if meta:
            details = (details or []) + [meta]

        # 4) call the parent with only the args it expects
        super().__init__(message=message, details=details)


class ApiAuthenticationError(ApiError):
    """
    Exception raised when authentication with an external API fails.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    error_type = "api_authentication_error"
    
    def __init__(
        self,
        message: str = "API authentication failed",
        api_name: Optional[str] = None,
        details: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        self.api_name = api_name
        
        if api_name and not details:
            details = [{
                "loc": ["auth"],
                "msg": f"Authentication failed for API: {api_name}",
                "type": "api_authentication_error"
            }]
            
        super().__init__(message=message, details=details, **kwargs)


class ApiNotFoundError(ApiError):
    """
    Exception raised when a resource is not found in an external API.
    """
    status_code = status.HTTP_404_NOT_FOUND
    error_type = "api_not_found"
    
    def __init__(
        self,
        message: str = "API resource not found",
        api_name: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        self.api_name = api_name
        self.resource_type = resource_type
        self.resource_id = resource_id
        
        # Create more specific message based on available information
        if api_name and resource_type and resource_id:
            message = f"Resource {resource_type}/{resource_id} not found in {api_name} API"
        elif api_name and resource_type:
            message = f"Resource type {resource_type} not found in {api_name} API"
        elif api_name:
            message = f"Resource not found in {api_name} API"
        
        if not details and (api_name or resource_type or resource_id):
            details = [{
                "type": "api_not_found",
                "msg": message
            }]
            
            if api_name:
                details[0]["api_name"] = api_name
            if resource_type:
                details[0]["resource_type"] = resource_type
            if resource_id:
                details[0]["resource_id"] = resource_id
                
        super().__init__(message=message, details=details, **kwargs)


class ApiConflictError(ApiError):
    """
    Exception raised when an external API reports a conflict error.
    Typically occurs with duplicate resources or concurrent modifications.
    """
    status_code = status.HTTP_409_CONFLICT
    error_type = "api_conflict"
    
    def __init__(
        self,
        message: str = "API resource conflict",
        api_name: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        self.api_name = api_name
        self.resource_type = resource_type
        self.resource_id = resource_id
        
        # Create more specific message based on available information
        if api_name and resource_type and resource_id:
            message = f"Resource conflict for {resource_type}/{resource_id} in {api_name} API"
        elif api_name and resource_type:
            message = f"Resource conflict for {resource_type} in {api_name} API"
        elif api_name:
            message = f"Resource conflict in {api_name} API"
        
        if not details and (api_name or resource_type or resource_id):
            details = [{
                "type": "api_conflict",
                "msg": message
            }]
            
            if api_name:
                details[0]["api_name"] = api_name
            if resource_type:
                details[0]["resource_type"] = resource_type
            if resource_id:
                details[0]["resource_id"] = resource_id
                
        super().__init__(message=message, details=details, **kwargs)


class ApiRateLimitError(ApiError):
    """
    Exception raised when an external API rate limit is exceeded.
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_type = "api_rate_limit_error"
    
    def __init__(
        self,
        message: str = "API rate limit exceeded",
        api_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        self.api_name = api_name
        self.retry_after = retry_after
        
        if api_name and retry_after:
            message = f"Rate limit exceeded for {api_name} API. Retry after {retry_after} seconds"
        elif api_name:
            message = f"Rate limit exceeded for {api_name} API"
        
        if not details and (api_name or retry_after):
            details = [{
                "type": "api_rate_limit",
                "msg": message
            }]
            
            if api_name:
                details[0]["api_name"] = api_name
            if retry_after:
                details[0]["retry_after"] = retry_after
                
        super().__init__(message=message, details=details, **kwargs)


class ApiTimeoutError(ApiError):
    """
    Exception raised when an API request times out.
    """
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    error_type = "api_timeout_error"
    
    def __init__(
        self,
        message: str = "API request timeout",
        api_name: Optional[str] = None,
        timeout: Optional[int] = None,
        details: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        self.api_name = api_name
        self.timeout = timeout
        
        if api_name and timeout:
            message = f"Request to {api_name} API timed out after {timeout} seconds"
        elif api_name:
            message = f"Request to {api_name} API timed out"
        
        if not details and (api_name or timeout):
            details = [{
                "type": "api_timeout",
                "msg": message
            }]
            
            if api_name:
                details[0]["api_name"] = api_name
            if timeout:
                details[0]["timeout"] = timeout
                
        super().__init__(message=message, details=details, **kwargs)


class ApiServiceUnavailableError(ApiError):
    """
    Exception raised when an external API service is unavailable.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_type = "api_service_unavailable_error"
    
    def __init__(
        self,
        message: str = "API service unavailable",
        api_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        self.api_name = api_name
        self.retry_after = retry_after
        
        if api_name and retry_after:
            message = f"{api_name} API service is unavailable. Retry after {retry_after} seconds"
        elif api_name:
            message = f"{api_name} API service is unavailable"
        
        if not details and (api_name or retry_after):
            details = [{
                "type": "api_service_unavailable",
                "msg": message
            }]
            
            if api_name:
                details[0]["api_name"] = api_name
            if retry_after:
                details[0]["retry_after"] = retry_after
                
        super().__init__(message=message, details=details, **kwargs) 