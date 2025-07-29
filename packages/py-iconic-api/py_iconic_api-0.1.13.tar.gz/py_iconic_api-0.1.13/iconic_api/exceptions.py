# -*- coding: utf-8 -*-
import httpx
from typing import Optional, Any, Dict, Type

class IconicAPIError(Exception):
    """Base exception for Iconic API client errors."""
    def __init__(self, message: str, response: httpx.Response):
        super().__init__(message)
        self.status_code = response.status_code
        self.response_content = response.content
        self.request_url = response.request.url
        self.request_method = response.request.method
        self.request_url = response.request.url
        self.request_params = response.request.url.params
        self.request_data = response.request.content
        self.response_headers = response.headers
        
        try:
            self.response_json = response.json()
        except Exception:
            self.response_json = None
        
        self.retry_after = None
        if self.response_headers.get('Retry-After'):
            self.retry_after = int(self.response_headers['Retry-After'])

    def __str__(self):
        parts = [super().__str__()]
        if self.status_code:
            parts.append(f"Status Code: {self.status_code}")
        if self.request_method and self.request_url:
            parts.append(f"Request: {self.request_method} {self.request_url}")
        if self.response_json:
            parts.append(f"Response JSON: {self.response_json}")
        elif self.response_content:
            parts.append(f"Response Content: {self.response_content[:500]}") # Truncate for readability
        if hasattr(self, 'retry_after'):
            parts.append(f"Retry After: {self.retry_after}")
        return "\n".join(parts)

class AuthenticationError(IconicAPIError):
    """Raised for authentication failures (401)."""
    pass

class AccessDeniedError(IconicAPIError):
    """Raised when access to a resource is forbidden (403)."""
    pass

class ResourceNotFoundError(IconicAPIError):
    """Raised when a requested resource is not found (404)."""
    pass

class ValidationError(IconicAPIError):
    """Raised when request data is invalid (400)."""
    pass

class ServerError(IconicAPIError):
    """Raised when the server returns a 500 error."""
    pass

class RateLimitError(IconicAPIError):
    """Raised when API rate limits are exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

class MaintenanceModeError(IconicAPIError):
    """Raised when the API is in maintenance mode (503)."""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

# Mapping status codes to exception classes for use in helper functions
STATUS_CODE_EXCEPTION_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    403: AccessDeniedError,
    404: ResourceNotFoundError,
    429: RateLimitError,
    500: ServerError,
    503: MaintenanceModeError,
}

def exception_for_status(status_code: int) -> Type[IconicAPIError]:
    """
    Return the appropriate exception class for a given HTTP status code.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        The corresponding exception class
    """
    return STATUS_CODE_EXCEPTION_MAP.get(status_code, IconicAPIError)

def create_exception_from_response(
    response: httpx.Response, 
    method: str, 
    url: str, 
    **kwargs
) -> IconicAPIError:
    """
    Create the appropriate exception based on the API response.
    
    This function determines the appropriate exception type based on the
    response status code and content, then constructs and returns it.
    
    Args:
        response: The HTTP response
        method: HTTP method used for the request
        url: URL of the request
        **kwargs: Additional parameters from the original request
        
    Returns:
        An instance of the appropriate IconicAPIError subclass
    """
    status_code = response.status_code
    
    # Extract retry-after header if present
    retry_after_header = response.headers.get("Retry-After")
    retry_after = int(retry_after_header) if retry_after_header and retry_after_header.isdigit() else None
    
    # Default error message
    message = f"API request failed for {method} {url}"
    
    # Determine exception class based on status code
    exception_class = exception_for_status(status_code)
    
    # Special handling for specific error types
    if status_code == 401:
        message = "Authentication failed. Token might be invalid or expired."
    elif status_code == 403:
        message = "Access denied. You don't have permission to access this resource."
    elif status_code == 404:
        message = "Resource not found."
    elif status_code == 429:
        message = "API rate limit exceeded."
    elif status_code == 500:
        message = "Server error. The request failed due to an internal server error."
    elif status_code == 503:
        message = "Service unavailable."
        # Check if it's maintenance mode
        try:
            content = response.json()
            if content.get("caused_by") == "maintenance_mode":
                exception_class = MaintenanceModeError
                message = "Service unavailable due to maintenance mode."
        except Exception:
            pass  # Fall through to generic handling
    
    return exception_class(message=message, response=response)