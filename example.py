"""
PayPay Mobile SDK - Example Usage

This example demonstrates all major features of the SDK.
"""
from paypay_mobile import PayPay

# Configuration
PHONE_NUMBER = "080-1234-5678"
PASSWORD = "your_password"


def example_login():
    """Example: Login and save credentials"""
    print("=== Login Example ===")
    paypay = PayPay(PHONE_NUMBER, PASSWORD)
    
    url = input("Enter OAuth URL: ")
    paypay.login(url)
    
    print(f"✅ Login successful!")
    print(f"Access Token: {paypay.access_token}")
    print(f"Device UUID: {paypay.device_uuid}")
    return paypay


def example_balance(paypay):
    """Example: Check balance and profile"""
    print("\n=== Balance & Profile ===")
    
    profile = paypay.get_profile()
    print(f"Name: {profile.name}")
    print(f"User ID: {profile.external_user_id}")
    
    balance = paypay.get_balance()
    print(f"Balance: ¥{balance.all_balance:,}")
    print(f"Money Light: ¥{balance.money_light:,}")
    print(f"Money: ¥{balance.money:,}")


def example_payment_link(paypay):
    """Example: Create and manage payment links"""
    print("\n=== Payment Link ===")
    
    # Create link
    link = paypay.create_link(amount=500, passcode="1234")
    print(f"Created link: {link.link}")
    
    # Check link
    info = paypay.link_check(link.link)
    print(f"Amount: ¥{info.amount}, Status: {info.status}")
    
    # Receive link (example)
    # paypay.link_receive(link.link, password="1234")


def example_send_money(paypay):
    """Example: Search user and send money"""
    print("\n=== Send Money ===")
    
    user_id = input("Enter user ID: ")
    user = paypay.search_p2puser(user_id)
    print(f"Found: {user.name}")
    
    amount = int(input("Amount (¥): "))
    result = paypay.send_money(amount=amount, receiver_id=user.external_user_id)
    print(f"✅ Sent ¥{amount:,}")
    
    # Send message
    paypay.send_message(result.chat_room_id, "Thank you!")


def main():
    """Main example"""
    print("PayPay Mobile SDK - Example\n")
    
    # Option 1: Login
    # paypay = example_login()
    
    # Option 2: Use saved token
    ACCESS_TOKEN = "your_saved_token"
    paypay = PayPay(access_token=ACCESS_TOKEN)
    
    # Run examples
    example_balance(paypay)
    # example_payment_link(paypay)
    # example_send_money(paypay)


if __name__ == "__main__":
    main()
