"""
PayPay Mobile - Main PayPay Class

This module provides the main PayPay class for interacting with PayPay's mobile API.
Based on PayPaython-mobile with AWS Solver integration from paypaypy.
"""
import re
import uuid
import json
from typing import Optional, List, Dict, Any, Union
import requests

from .models import (
    ProfileInfo, BalanceInfo, LinkInfo, CreateLinkResult,
    P2PCodeResult, SendMoneyResult, UserSearchResult,
    ChatRoomResult, BarcodeInfo, HistoryItem
)
from .exceptions import (
    LoginException, AuthenticationException, TokenExpiredException,
    LinkException, PaymentException, NetworkException, RateLimitException,
    ValidationException
)
from .aws_solver import handle_aws_captcha


class PayPay:
    """
    Main PayPay class for mobile API interactions
    
    Example:
        >>> paypay = PayPay("080-1234-5678", "password")
        >>> url = input("URL?: ")
        >>> paypay.login(url)
        >>> print(paypay.access_token)
        
    Or with access token:
        >>> paypay = PayPay(access_token="your_access_token")
        >>> balance = paypay.get_balance()
        >>> print(balance.all_balance)
    """
    
    BASE_URL = "https://app4.paypay.ne.jp"
    WEB_BASE_URL = "https://www.paypay.ne.jp"
    
    def __init__(
        self,
        phone_number: Optional[str] = None,
        password: Optional[str] = None,
        device_uuid: Optional[str] = None,
        access_token: Optional[str] = None,
        proxy: Optional[Union[str, Dict[str, str]]] = None,
        use_aws_solver: bool = True
    ):
        """
        Initialize PayPay client
        
        Args:
            phone_number: Phone number for login (with or without hyphens)
            password: Password for login
            device_uuid: Registered device UUID (optional)
            access_token: Existing access token (skips login)
            proxy: Proxy configuration (str or dict)
            use_aws_solver: Enable AWS CAPTCHA solver (default: True)
        """
        self.phone_number = self._normalize_phone(phone_number) if phone_number else None
        self.password = password
        self.device_uuid = device_uuid or str(uuid.uuid4())
        self.client_uuid = str(uuid.uuid4())
        self.access_token = access_token
        self.refresh_token: Optional[str] = None
        self.use_aws_solver = use_aws_solver
        
        # Setup session
        self.session = requests.Session()
        self._setup_proxy(proxy)
        self._setup_headers()
        
        # If we have phone/password but no access token, prepare for login
        if phone_number and password and not access_token:
            self._login_prepared = True
        else:
            self._login_prepared = False
    
    def _normalize_phone(self, phone: str) -> str:
        """Remove hyphens from phone number"""
        return phone.replace("-", "")
    
    def _setup_proxy(self, proxy: Optional[Union[str, Dict[str, str]]]):
        """Setup proxy configuration"""
        if proxy:
            if isinstance(proxy, str):
                # Handle string proxy
                if not proxy.startswith("http://") and not proxy.startswith("https://"):
                    proxy = f"http://{proxy}"
                self.session.proxies = {
                    "http": proxy,
                    "https": proxy
                }
            elif isinstance(proxy, dict):
                self.session.proxies = proxy
    
    def _setup_headers(self):
        """Setup default headers"""
        self.session.headers.update({
            "User-Agent": "PayPay/3.80.0 (iPhone; iOS 16.0; Scale/3.00)",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Client-OS-Version": "16.0",
            "Client-OS-Type": "IOS",
            "Client-App-Version": "3.80.0",
            "Client-Mode": "NORMAL"
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        use_base_url: bool = True,
        retry_on_captcha: bool = True
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and AWS CAPTCHA support
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            use_base_url: Use BASE_URL (True) or full URL (False)
            retry_on_captcha: Retry request after solving CAPTCHA
            
        Returns:
            Response JSON data
            
        Raises:
            NetworkException: On network errors
            AuthenticationException: On auth errors
            RateLimitException: On rate limiting
        """
        url = f"{self.BASE_URL}{endpoint}" if use_base_url else endpoint
        
        # Add auth header if we have access token
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            )
            
            # Handle AWS CAPTCHA if enabled
            if self.use_aws_solver and retry_on_captcha:
                if handle_aws_captcha(self.session, response):
                    # Retry request after solving CAPTCHA
                    response = self.session.request(
                        method=method,
                        url=url,
                        json=data,
                        params=params,
                        headers=headers
                    )
            
            # Handle rate limiting
            if response.status_code == 429:
                raise RateLimitException("Rate limit exceeded")
            
            # Handle token expiration
            if response.status_code == 401:
                raise TokenExpiredException("Access token expired")
            
            # Raise for other errors
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            raise NetworkException(f"Network request failed: {str(e)}")
    
    def login(self, url_or_id: str) -> bool:
        """
        Complete login process
        
        Args:
            url_or_id: Full OAuth URL or just the ID parameter
                      e.g., "https://www.paypay.ne.jp/portal/oauth2/l?id=TK4602"
                      or just "TK4602"
        
        Returns:
            True if login successful
            
        Raises:
            LoginException: If login fails
        """
        if not self.phone_number or not self.password:
            raise LoginException("Phone number and password required for login")
        
        # Extract ID from URL if full URL provided
        link_id = self._extract_link_id(url_or_id)
        
        try:
            # Step 1: Start login
            self._login_start()
            
            # Step 2: Confirm login with link
            self._login_confirm(link_id)
            
            return True
            
        except Exception as e:
            raise LoginException(f"Login failed: {str(e)}")
    
    def _extract_link_id(self, url_or_id: str) -> str:
        """Extract link ID from URL or return ID directly"""
        if "id=" in url_or_id:
            match = re.search(r'id=([A-Za-z0-9]+)', url_or_id)
            if match:
                return match.group(1)
        return url_or_id
    
    def _login_start(self):
        """Start login process"""
        endpoint = "/bff/v2/oauth2/par"
        data = {
            "phoneNumber": self.phone_number,
            "password": self.password,
            "deviceUuid": self.device_uuid,
            "clientUuid": self.client_uuid
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        if response.get("header", {}).get("resultCode") != "S0000":
            raise LoginException("Login start failed")
    
    def _login_confirm(self, link_id: str):
        """Confirm login with OAuth link"""
        endpoint = f"/bff/v2/oauth2/token?id={link_id}"
        data = {
            "deviceUuid": self.device_uuid,
            "clientUuid": self.client_uuid
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        payload = response.get("payload", {})
        self.access_token = payload.get("accessToken")
        self.refresh_token = payload.get("refreshToken")
        
        if not self.access_token:
            raise LoginException("Failed to obtain access token")
    
    def token_refresh(self, refresh_token: Optional[str] = None) -> bool:
        """
        Refresh access token
        
        Args:
            refresh_token: Refresh token (uses instance token if not provided)
            
        Returns:
            True if refresh successful
        """
        token = refresh_token or self.refresh_token
        
        if not token:
            raise AuthenticationException("No refresh token available")
        
        endpoint = "/bff/v2/oauth2/refresh"
        data = {
            "refreshToken": token
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        payload = response.get("payload", {})
        self.access_token = payload.get("accessToken")
        self.refresh_token = payload.get("refreshToken")
        
        return bool(self.access_token)
    
    def get_profile(self) -> ProfileInfo:
        """
        Get user profile information
        
        Returns:
            ProfileInfo object with user data
        """
        endpoint = "/bff/v2/getProfile"
        response = self._make_request("GET", endpoint)
        
        payload = response.get("payload", {})
        return ProfileInfo.from_dict(payload)
    
    def get_balance(self) -> BalanceInfo:
        """
        Get PayPay balance
        
        Returns:
            BalanceInfo object with balance data
        """
        endpoint = "/bff/v2/getBalance"
        response = self._make_request("GET", endpoint)
        
        payload = response.get("payload", {})
        return BalanceInfo.from_dict(payload)
    
    def get_history(self, size: int = 20) -> List[Dict[str, Any]]:
        """
        Get payment history
        
        Args:
            size: Number of history items to retrieve (default: 20)
            
        Returns:
            List of history items
        """
        endpoint = "/bff/v2/getHistory"
        params = {"size": size}
        response = self._make_request("GET", endpoint, params=params)
        
        return response.get("payload", {}).get("history", [])
    
    def get_chat_rooms(self, size: int = 20) -> List[Dict[str, Any]]:
        """
        Get PayPay DM chat rooms
        
        Args:
            size: Number of chat rooms to retrieve
            
        Returns:
            List of chat rooms
        """
        endpoint = "/bff/v2/getChatRooms"
        params = {"size": size}
        response = self._make_request("GET", endpoint, params=params)
        
        return response.get("payload", {}).get("chatRooms", [])
    
    def get_chat_room_messages(self, chat_room_id: str) -> List[Dict[str, Any]]:
        """
        Get messages from a chat room
        
        Args:
            chat_room_id: Chat room ID (with or without "sendbird_group_channel_" prefix)
            
        Returns:
            List of messages
        """
        # Remove prefix if present
        if chat_room_id.startswith("sendbird_group_channel_"):
            chat_room_id = chat_room_id[23:]
        
        endpoint = f"/bff/v2/getChatRoomMessages/{chat_room_id}"
        response = self._make_request("GET", endpoint)
        
        return response.get("payload", {}).get("messages", [])
    
    def get_point_history(self) -> List[Dict[str, Any]]:
        """
        Get PayPay point history
        
        Returns:
            List of point history items
        """
        endpoint = "/bff/v2/getPointHistory"
        response = self._make_request("GET", endpoint)
        
        return response.get("payload", {}).get("history", [])
    
    def link_check(self, url_or_id: str, web: bool = False) -> LinkInfo:
        """
        Check payment link information
        
        Args:
            url_or_id: Payment link URL or ID
            web: Use Web API instead of mobile API
            
        Returns:
            LinkInfo object with link data
        """
        link_id = self._extract_link_id(url_or_id)
        
        if web:
            endpoint = f"{self.WEB_BASE_URL}/portal/api/v2/link/check/{link_id}"
            response = self._make_request("GET", endpoint, use_base_url=False)
        else:
            endpoint = f"/bff/v2/executeLink/check/{link_id}"
            response = self._make_request("GET", endpoint)
        
        payload = response.get("payload", {})
        return LinkInfo.from_dict(payload)
    
    def link_receive(
        self,
        url_or_id: str,
        password: Optional[str] = None,
        link_info: Optional[Union[LinkInfo, Dict]] = None
    ) -> bool:
        """
        Receive payment from link
        
        Args:
            url_or_id: Payment link URL or ID
            password: Password if link is protected
            link_info: Pre-fetched link info to skip check
            
        Returns:
            True if successful
        """
        link_id = self._extract_link_id(url_or_id)
        
        # Get link info if not provided
        if link_info is None:
            link_info = self.link_check(link_id)
        
        if isinstance(link_info, dict):
            link_info = LinkInfo.from_dict(link_info)
        
        endpoint = "/bff/v2/executeLink/receive"
        data = {
            "linkId": link_id,
            "orderId": link_info.order_id
        }
        
        if password:
            data["password"] = password
        
        response = self._make_request("POST", endpoint, data=data)
        
        return response.get("header", {}).get("resultCode") == "S0000"
    
    def link_reject(
        self,
        url_or_id: str,
        link_info: Optional[Union[LinkInfo, Dict]] = None
    ) -> bool:
        """
        Reject payment link
        
        Args:
            url_or_id: Payment link URL or ID
            link_info: Pre-fetched link info to skip check
            
        Returns:
            True if successful
        """
        link_id = self._extract_link_id(url_or_id)
        
        # Get link info if not provided
        if link_info is None:
            link_info = self.link_check(link_id)
        
        if isinstance(link_info, dict):
            link_info = LinkInfo.from_dict(link_info)
        
        endpoint = "/bff/v2/executeLink/reject"
        data = {
            "linkId": link_id,
            "orderId": link_info.order_id
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        return response.get("header", {}).get("resultCode") == "S0000"
    
    def link_cancel(
        self,
        url_or_id: str,
        link_info: Optional[Union[LinkInfo, Dict]] = None
    ) -> bool:
        """
        Cancel payment link
        
        Args:
            url_or_id: Payment link URL or ID
            link_info: Pre-fetched link info to skip check
            
        Returns:
            True if successful
        """
        link_id = self._extract_link_id(url_or_id)
        
        # Get link info if not provided
        if link_info is None:
            link_info = self.link_check(link_id)
        
        if isinstance(link_info, dict):
            link_info = LinkInfo.from_dict(link_info)
        
        endpoint = "/bff/v2/executeLink/cancel"
        data = {
            "linkId": link_id,
            "orderId": link_info.order_id
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        return response.get("header", {}).get("resultCode") == "S0000"
    
    def create_link(self, amount: int, passcode: Optional[str] = None) -> CreateLinkResult:
        """
        Create payment link
        
        Args:
            amount: Amount in yen
            passcode: Optional password for link
            
        Returns:
            CreateLinkResult object with link URL and chat room ID
        """
        endpoint = "/bff/v2/createLink"
        data = {
            "amount": amount
        }
        
        if passcode:
            data["passcode"] = passcode
        
        response = self._make_request("POST", endpoint, data=data)
        
        payload = response.get("payload", {})
        return CreateLinkResult.from_dict(payload)
    
    def create_p2pcode(self, amount: Optional[int] = None) -> P2PCodeResult:
        """
        Create P2P QR code for receiving money
        
        Args:
            amount: Optional amount in yen
            
        Returns:
            P2PCodeResult object with QR code URL
        """
        endpoint = "/bff/v2/createP2PCode"
        data = {}
        
        if amount is not None:
            data["amount"] = amount
        
        response = self._make_request("POST", endpoint, data=data)
        
        payload = response.get("payload", {})
        return P2PCodeResult.from_dict(payload)
    
    def send_money(self, amount: int, receiver_id: str) -> SendMoneyResult:
        """
        Send money to user
        
        Args:
            amount: Amount in yen
            receiver_id: Receiver's external user ID
            
        Returns:
            SendMoneyResult object with chat room ID
        """
        endpoint = "/bff/v2/sendMoney"
        data = {
            "amount": amount,
            "receiverId": receiver_id
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        payload = response.get("payload", {})
        return SendMoneyResult.from_dict(payload)
    
    def send_message(self, chat_room_id: str, message: str) -> bool:
        """
        Send message in chat room
        
        Args:
            chat_room_id: Chat room ID
            message: Message text
            
        Returns:
            True if successful
        """
        endpoint = "/bff/v2/sendMessage"
        data = {
            "chatRoomId": chat_room_id,
            "message": message
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        return response.get("header", {}).get("resultCode") == "S0000"
    
    def set_money_priority(self, paypay_money: bool = False) -> bool:
        """
        Set payment priority (Money Light vs Money)
        
        Args:
            paypay_money: True for Money priority, False for Money Light priority
            
        Returns:
            True if successful
        """
        endpoint = "/bff/v2/setMoneyPriority"
        data = {
            "priority": "MONEY" if paypay_money else "MONEY_LIGHT"
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        return response.get("header", {}).get("resultCode") == "S0000"
    
    def search_p2puser(
        self,
        user_id: str,
        is_global: bool = True,
        order: int = 0
    ) -> UserSearchResult:
        """
        Search for PayPay user
        
        Args:
            user_id: User ID or display name
            is_global: Search globally (True) or in friends (False)
            order: Index if multiple users match (for friend search)
            
        Returns:
            UserSearchResult object
        """
        endpoint = "/bff/v2/searchP2PUser"
        params = {
            "userId": user_id,
            "isGlobal": str(is_global).lower()
        }
        
        response = self._make_request("GET", endpoint, params=params)
        
        payload = response.get("payload", {})
        users = payload.get("users", [])
        
        if not users:
            raise ValidationException("User not found")
        
        if order >= len(users):
            raise ValidationException(f"User index {order} out of range")
        
        return UserSearchResult.from_dict(users[order])
    
    def initialize_chatroom(self, external_user_id: str) -> ChatRoomResult:
        """
        Initialize chat room with user
        
        Args:
            external_user_id: External user ID
            
        Returns:
            ChatRoomResult object with chat room ID
        """
        endpoint = "/bff/v2/initializeChatroom"
        data = {
            "externalUserId": external_user_id
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        payload = response.get("payload", {})
        return ChatRoomResult.from_dict(payload)
    
    def get_barcode_info(self, url: str) -> BarcodeInfo:
        """
        Get information from PayPay QR code/barcode
        
        Args:
            url: Full QR code URL
            
        Returns:
            BarcodeInfo object
        """
        endpoint = "/bff/v2/getBarcodeInfo"
        data = {
            "url": url
        }
        
        response = self._make_request("POST", endpoint, data=data)
        
        payload = response.get("payload", {})
        return BarcodeInfo.from_dict(payload)
