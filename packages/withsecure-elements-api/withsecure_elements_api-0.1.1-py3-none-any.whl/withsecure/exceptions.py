"""
Custom exceptions for the WithSecure Elements API client.
"""

class WithSecureError(Exception):
    """Base exception for all WithSecure Elements API errors."""
    pass

class AuthenticationError(WithSecureError):
    """Raised when authentication fails."""
    pass

class APIError(WithSecureError):
    """Base exception for API-related errors."""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class ForbiddenError(APIError):
    """Raised when a forbidden error is returned."""
    pass

class InvalidParameters(WithSecureError):
    """Raised when invalid parameters are provided."""
    pass

class ResourceNotFound(APIError):
    """Raised when a requested resource is not found."""
    pass

class RateLimitExceeded(APIError):
    """Raised when API rate limits are exceeded."""
    pass

class ServerError(APIError):
    """Raised when the API server returns an error."""
    pass

class ClientError(APIError):
    """Raised when there's an error on the client side."""
    pass
