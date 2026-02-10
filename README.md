# PayPay Mobile SDK

Python SDK for PayPay Mobile API with AWS CAPTCHA solver.

Based on [PayPaython-mobile](https://github.com/taka-4602/PayPaython-mobile) + [paypaypy](https://github.com/suimin-1729/paypaypy) AWS Solver.

## Installation

```bash
pip install paypay-mobile
```

## Quick Start

```python
from paypay_mobile import PayPay

# Login
paypay = PayPay("080-1234-5678", "password")
url = input("OAuth URL: ")
paypay.login(url)

# Check balance
balance = paypay.get_balance()
print(f"Balance: ¥{balance.all_balance:,}")

# Send money
user = paypay.search_p2puser("user_id")
result = paypay.send_money(amount=100, receiver_id=user.external_user_id)

# Create payment link
link = paypay.create_link(amount=500, passcode="1234")
print(f"Link: {link.link}")
```

## Features

- 🔐 Login with phone/password or access token
- 🤖 AWS CAPTCHA auto-solver
- 💸 Payment links (create/receive/reject/cancel)
- 💰 P2P transfers
- 📊 Balance & history
- 💬 Chat & messaging
- 🔍 User search

## API Methods

### Authentication
- `login(url_or_id)` - Login with OAuth URL
- `token_refresh()` - Refresh access token

### Account
- `get_profile()` - Get user profile
- `get_balance()` - Get balance
- `get_history(size=20)` - Get payment history

### Payments
- `send_money(amount, receiver_id)` - Send money
- `create_link(amount, passcode=None)` - Create payment link
- `link_check(url_or_id)` - Check link info
- `link_receive(url_or_id, password=None)` - Receive payment
- `link_reject(url_or_id)` - Reject link
- `link_cancel(url_or_id)` - Cancel link

### Users & Chat
- `search_p2puser(user_id)` - Search user
- `send_message(chat_room_id, message)` - Send message
- `get_chat_rooms(size=20)` - Get chat rooms

### QR Codes
- `create_p2pcode(amount=None)` - Create P2P QR code
- `get_barcode_info(url)` - Read QR code

## Advanced Usage

### Use saved token
```python
paypay = PayPay(access_token="your_token")
```

### Use proxy
```python
paypay = PayPay("phone", "password", proxy="http://proxy:8080")
```

### Error handling
```python
from paypay_mobile import TokenExpiredException

try:
    balance = paypay.get_balance()
except TokenExpiredException:
    paypay.token_refresh()
    balance = paypay.get_balance()
```

## Publishing to PyPI

```bash
# Build
python -m pip install build twine
python -m build

# Upload to TestPyPI (optional)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

## License

MIT License - See LICENSE file

## Disclaimer

Unofficial SDK. Not affiliated with PayPay Corporation. Use at your own risk.
