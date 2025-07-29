"""Custom exceptions for WFRMLS API wrapper."""

from typing import Any, Dict, Optional


class WFRMLSError(Exception):
    """Base exception for all WFRMLS API errors.
    
    This is the base class for all exceptions raised by the WFRMLS API wrapper.
    All other custom exceptions inherit from this class.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message describing what went wrong
            status_code: HTTP status code from the API response
            response_data: Raw response data from the API for debugging
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(WFRMLSError):
    """Raised when authentication fails.
    
    This exception is raised when the bearer token is invalid, missing,
    or expired, resulting in a 401 Unauthorized response.
    """


class ValidationError(WFRMLSError):
    """Raised when request validation fails.
    
    This exception is raised when the API returns a 400 Bad Request,
    indicating that the request parameters or format are invalid.
    """


class NotFoundError(WFRMLSError):
    """Raised when a resource is not found.
    
    This exception is raised when the API returns a 404 Not Found,
    indicating that the requested resource (property, member, etc.) does not exist.
    """


class RateLimitError(WFRMLSError):
    """Raised when rate limit is exceeded.
    
    This exception is raised when the API returns a 429 Too Many Requests,
    indicating that the client has exceeded the rate limit.
    """


class ServerError(WFRMLSError):
    """Raised when server returns 5xx error.
    
    This exception is raised when the API returns a 500+ status code,
    indicating a server-side error that is not caused by the client request.
    """


class NetworkError(WFRMLSError):
    """Raised when network connection fails.
    
    This exception is raised when there are network connectivity issues
    preventing the request from reaching the API server.
    """ 