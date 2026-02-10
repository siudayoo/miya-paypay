"""
PayPay Mobile - Custom Exceptions
"""


class PayPayException(Exception):
    """Base exception for PayPay Mobile"""
    pass


class LoginException(PayPayException):
    """Raised when login fails"""
    pass


class AuthenticationException(PayPayException):
    """Raised when authentication fails"""
    pass


class TokenExpiredException(PayPayException):
    """Raised when access token has expired"""
    pass


class LinkException(PayPayException):
    """Raised when link operation fails"""
    pass


class PaymentException(PayPayException):
    """Raised when payment operation fails"""
    pass


class NetworkException(PayPayException):
    """Raised when network request fails"""
    pass


class RateLimitException(PayPayException):
    """Raised when rate limit is exceeded"""
    pass


class ValidationException(PayPayException):
    """Raised when input validation fails"""
    pass
