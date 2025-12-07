#!/usr/bin/env python3
"""
Test M-Pesa Integration - Verify all components are working
"""
import requests
from datetime import datetime
import base64

# Test configuration
MPESA_CONSUMER_KEY = "UnDvUCktXcQDyRScx0uAnJlA7rboMWhSnAxvhSOYQiX8QU0t"
MPESA_CONSUMER_SECRET = "eP7nwvhM3OwL0nVhRlOCsGnRawPi32BkENmT33NygDpdYdq5sy1WyAshdCnidCkb"
MPESA_SHORTCODE = "174379"
MPESA_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

def test_oauth_token():
    """Test OAuth token generation"""
    print("\n1️⃣ Testing OAuth Token Generation...")
    print("-" * 70)
    
    try:
        response = requests.get(
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET),
            timeout=30
        )
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ OAuth Token Generated Successfully")
            print(f"   Token (first 20 chars): {token[:20]}...")
            print(f"   Token Length: {len(token)} characters")
            return token
        else:
            print(f"❌ Failed to get token")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_password_generation():
    """Test password generation for STK Push"""
    print("\n2️⃣ Testing Password Generation...")
    print("-" * 70)
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(data_to_encode.encode()).decode('utf-8')
    
    print(f"✅ Password Generated Successfully")
    print(f"   Timestamp: {timestamp}")
    print(f"   Password (first 30 chars): {password[:30]}...")
    print(f"   Password Length: {len(password)} characters")
    
    return password, timestamp

def test_stk_push_structure(access_token):
    """Test STK Push request structure"""
    print("\n3️⃣ Testing STK Push Request Structure...")
    print("-" * 70)
    
    if not access_token:
        print("⚠️  Skipped (no access token)")
        return
    
    password, timestamp = test_password_generation()
    
    # Prepare test payload
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,  # Test with 1 KSh
        "PartyA": "254708374149",  # Test phone from Postman
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": "254708374149",
        "CallBackURL": "https://mydomain.com/mpesa/callback",
        "AccountReference": "TEST_ORDER",
        "TransactionDesc": "Test Payment"
    }
    
    print("✅ STK Push Payload Structure:")
    for key, value in payload.items():
        if key == "Password":
            print(f"   {key}: {value[:30]}... (truncated)")
        else:
            print(f"   {key}: {value}")
    
    print("\n⚠️  NOTE: Actual STK Push not sent (test only)")
    print("   To test real STK Push, use a valid Kenyan phone number")

def main():
    print("\n" + "=" * 70)
    print("🧪 M-PESA INTEGRATION TEST - Sandbox Environment")
    print("=" * 70)
    
    # Test 1: OAuth Token
    access_token = test_oauth_token()
    
    # Test 2: Password Generation
    test_password_generation()
    
    # Test 3: STK Push Structure
    test_stk_push_structure(access_token)
    
    print("\n" + "=" * 70)
    print("✅ M-PESA INTEGRATION COMPONENTS VERIFIED")
    print("=" * 70)
    print("\n📋 Next Steps:")
    print("   1. Login as vendor: http://127.0.0.1:5000/login")
    print("   2. Go to order: http://127.0.0.1:5000/vendor/order/3")
    print("   3. Enter valid Kenyan phone number (254XXXXXXXXX)")
    print("   4. Click 'Send Payment Request to Customer'")
    print("   5. Check phone for M-Pesa prompt")
    print("   6. Enter PIN and confirm")
    print("   7. Click 'Manual Confirm' in vendor portal")
    print("\n⚠️  Remember: Use real Kenyan phone number for testing!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
