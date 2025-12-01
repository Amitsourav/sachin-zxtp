#!/usr/bin/env python3
"""
Zerodha Access Token Generator
Run this script to get your access token for trading
"""

from kiteconnect import KiteConnect
import webbrowser

# Your API credentials from .env file
API_KEY = "ke8cqy1r7kub89v8"
API_SECRET = "pq3jxj11d7nf2q3xytttarbc0qz4z7on"

# Initialize KiteConnect
kite = KiteConnect(api_key=API_KEY)

# Get login URL
login_url = kite.login_url()
print("="*80)
print("ZERODHA ACCESS TOKEN GENERATOR")
print("="*80)
print("\nStep 1: Opening browser for login...")
print(f"Login URL: {login_url}")

# Open browser
webbrowser.open(login_url)

print("\nStep 2: After logging in, you'll be redirected to a URL like:")
print("http://127.0.0.1/?request_token=xxxxx&action=login&status=success")
print("\nCopy the request_token value and paste below:")

# Get request token from user
request_token = input("\nEnter request_token: ").strip()

try:
    # Generate access token
    data = kite.generate_session(request_token, api_secret=API_SECRET)
    access_token = data["access_token"]
    
    print("\n" + "="*80)
    print("SUCCESS! Your access token is:")
    print("="*80)
    print(f"\nACCESS_TOKEN: {access_token}")
    print("\n" + "="*80)
    print("\nIMPORTANT: Add this to your .env file:")
    print(f"ZERODHA_ACCESS_TOKEN={access_token}")
    print("\nThis token is valid for the entire trading day.")
    print("You'll need to regenerate it tomorrow.")
    print("="*80)
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nMake sure you:")
    print("1. Logged in successfully")
    print("2. Copied the correct request_token")
    print("3. Have the correct API credentials")