#!/usr/bin/env python3
"""
Get Zerodha Access Token
Run this script to get a fresh access token for your Zerodha account
"""

from kiteconnect import KiteConnect
import yaml
from pathlib import Path
import webbrowser

print("""
╔══════════════════════════════════════════════════════════════╗
║           ZERODHA ACCESS TOKEN GENERATOR                      ║
╚══════════════════════════════════════════════════════════════╝
""")

# Load config
config_path = Path("config/config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

api_key = config['broker']['api_key']
api_secret = config['broker']['api_secret']

print(f"API Key: {api_key}")
print(f"API Secret: {api_secret[:10]}...")

# Initialize Kite
kite = KiteConnect(api_key=api_key)

# Get login URL
login_url = kite.login_url()
print(f"\n📌 Step 1: Open this URL in your browser:")
print(f"   {login_url}")

# Try to open browser automatically
try:
    webbrowser.open(login_url)
    print("\n✅ Browser opened automatically!")
except:
    print("\n⚠️  Please open the URL manually in your browser")

print("""
📌 Step 2: Login with your Zerodha credentials

📌 Step 3: After successful login, you'll be redirected to:
   127.0.0.1:5000/?request_token=XXXX&action=login&status=success
   
   Copy the request_token value from the URL
""")

# Get request token from user
request_token = input("\n📝 Enter the request_token from URL: ").strip()

if not request_token:
    print("❌ No request token provided!")
    exit(1)

try:
    # Generate access token
    print("\n🔐 Generating access token...")
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    
    print(f"\n✅ SUCCESS! Your new access token:")
    print("=" * 60)
    print(f"{access_token}")
    print("=" * 60)
    
    # Update config file
    update = input("\n💾 Update config.yaml with new token? (yes/no): ").lower()
    
    if update == 'yes':
        config['broker']['access_token'] = access_token
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("✅ Config file updated successfully!")
        print("\n🚀 You can now run: python3 paper_trade_zerodha.py")
    else:
        print("\n📋 Please update config/config.yaml manually:")
        print(f"   access_token: {access_token}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure:")
    print("1. Request token is correct")
    print("2. API credentials are valid")
    print("3. You logged in successfully")