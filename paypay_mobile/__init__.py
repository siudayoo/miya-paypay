"""
PayPay Mobile - Python SDK for PayPay Mobile API

A Python library for interacting with PayPay's mobile API, featuring:
- Login with phone number and password
- AWS WAF CAPTCHA solver integration
- Payment links (create, receive, reject, cancel)
- P2P transfers
- Balance and history management
- Chat/messaging functionality
- User search

Based on PayPaython-mobile with AWS Solver from paypaypy.
"""

__version__ = "1.0.0"
__author__ = "PayPay Mobile Contributors"
__license__ = "MIT"

from .paypay import PayPay
from .models import (
    ProfileInfo,
    BalanceInfo,
    LinkInfo,
    CreateLinkResult,
    P2PCodeResult,
    SendMoneyResult,
    UserSearchResult,
    ChatRoomResult,
    BarcodeInfo,
    HistoryItem
)
from .exceptions import (
    PayPayException,
    LoginException,
    AuthenticationException,
    TokenExpiredException,
    LinkException,
    PaymentException,
    NetworkException,
    RateLimitException,
    ValidationException
)

__all__ = [
    # Main class
    "PayPay",
    
    # Models
    "ProfileInfo",
    "BalanceInfo",
    "LinkInfo",
    "CreateLinkResult",
    "P2PCodeResult",
    "SendMoneyResult",
    "UserSearchResult",
    "ChatRoomResult",
    "BarcodeInfo",
    "HistoryItem",
    
    # Exceptions
    "PayPayException",
    "LoginException",
    "AuthenticationException",
    "TokenExpiredException",
    "LinkException",
    "PaymentException",
    "NetworkException",
    "RateLimitException",
    "ValidationException",
]
