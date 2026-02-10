"""
PayPay Mobile - Data Models
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class ProfileInfo:
    """User profile information"""
    name: str
    external_user_id: str
    icon: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfileInfo':
        return cls(
            name=data.get('name', ''),
            external_user_id=data.get('externalUserId', ''),
            icon=data.get('icon')
        )


@dataclass
class BalanceInfo:
    """PayPay balance information"""
    all_balance: int
    useable_balance: int
    money_light: int
    money: int
    points: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BalanceInfo':
        return cls(
            all_balance=data.get('allBalance', 0),
            useable_balance=data.get('useableBalance', 0),
            money_light=data.get('moneyLight', 0),
            money=data.get('money', 0),
            points=data.get('points', 0)
        )


@dataclass
class LinkInfo:
    """Payment link information"""
    amount: int
    money_light: int
    money: int
    has_password: bool
    chat_room_id: Optional[str]
    status: str
    order_id: str
    link_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkInfo':
        return cls(
            amount=data.get('amount', 0),
            money_light=data.get('moneyLight', 0),
            money=data.get('money', 0),
            has_password=data.get('hasPassword', False),
            chat_room_id=data.get('chatRoomId'),
            status=data.get('status', ''),
            order_id=data.get('orderId', ''),
            link_id=data.get('linkId')
        )


@dataclass
class CreateLinkResult:
    """Result of creating a payment link"""
    link: str
    chat_room_id: str
    order_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreateLinkResult':
        return cls(
            link=data.get('link', ''),
            chat_room_id=data.get('chatRoomId', ''),
            order_id=data.get('orderId')
        )


@dataclass
class P2PCodeResult:
    """Result of creating a P2P code"""
    p2pcode: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'P2PCodeResult':
        return cls(
            p2pcode=data.get('p2pcode', '')
        )


@dataclass
class SendMoneyResult:
    """Result of sending money"""
    chat_room_id: str
    order_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SendMoneyResult':
        return cls(
            chat_room_id=data.get('chatRoomId', ''),
            order_id=data.get('orderId')
        )


@dataclass
class UserSearchResult:
    """Result of user search"""
    name: str
    icon: Optional[str]
    external_user_id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSearchResult':
        return cls(
            name=data.get('name', ''),
            icon=data.get('icon'),
            external_user_id=data.get('externalUserId', '')
        )


@dataclass
class ChatRoomResult:
    """Result of initializing chat room"""
    chatroom_id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatRoomResult':
        return cls(
            chatroom_id=data.get('chatroomId', '')
        )


@dataclass
class BarcodeInfo:
    """Barcode/QR code information"""
    amount: Optional[int]
    external_user_id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BarcodeInfo':
        return cls(
            amount=data.get('amount'),
            external_user_id=data.get('externalUserId', '')
        )


@dataclass
class HistoryItem:
    """Payment history item"""
    order_id: str
    amount: int
    transaction_type: str
    datetime: str
    description: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryItem':
        return cls(
            order_id=data.get('orderId', ''),
            amount=data.get('amount', 0),
            transaction_type=data.get('transactionType', ''),
            datetime=data.get('datetime', ''),
            description=data.get('description')
        )
