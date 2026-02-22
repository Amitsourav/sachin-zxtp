#!/usr/bin/env python3
"""
Zerodha API Setup and Configuration
This script helps you configure and test your Zerodha API connection
"""

import os
import sys
import json
import yaml
from pathlib import Path
from getpass import getpass
import webbrowser

try:
    from kiteconnect import KiteConnect
except ImportError:
    print("Installing kiteconnect package...")
    os.system("pip3 install kiteconnect")
    from kiteconnect import KiteConnect


def print_header():
    print("""
╔══════════════════════════════════════════════════════════════╗
║            ZERODHA KITE CONNECT API SETUP                    ║
║                                                              ║
║  This will configure your Zerodha API for live trading      ║
╚══════════════════════════════════════════════════════════════╝
    """)


def get_credentials():
    """Get API credentials from user"""
    print("\n📝 Enter your Zerodha Kite Connect API Details:")
    print("   (Get these from https://developers.kite.trade/apps)\n")
    
    api_key = input("1. API Key: ").strip()
    api_secret = getpass("2. API Secret: ").strip()
    
    return api_key, api_secret


def save_credentials(api_key, api_secret, access_token=None):
    """Save credentials to config file"""
    config_path = Path("config/config.yaml")
    
    # Read existing config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Update broker section
    config['broker'] = {
        'name': 'zerodha',
        'api_key': api_key,
        'api_secret': api_secret,
        'access_token': access_token or '',
    }
    
    # Switch to live trading mode
    config['trading']['mode'] = 'live'
    config['trading']['use_live_data'] = True
    
    # Save updated config
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("✅ Configuration saved to config/config.yaml")


def generate_access_token(api_key, api_secret):
    """Generate access token through login flow"""
    kite = KiteConnect(api_key=api_key)
    
    print("\n🔐 Authentication Process:")
    print("=" * 50)
    print("1. Opening Zerodha login page in your browser...")
    print("2. Login with your Zerodha credentials")
    print("3. After login, you'll be redirected to a URL")
    print("4. Copy the ENTIRE URL and paste it here")
    print("=" * 50)
    
    # Get login URL
    login_url = kite.login_url()
    print(f"\nLogin URL: {login_url}")
    
    # Open in browser
    webbrowser.open(login_url)
    
    print("\n⚠️  After login, the URL will look like:")
    print("   http://127.0.0.1/?request_token=XXXXXX&action=login&status=success")
    
    redirect_url = input("\n📋 Paste the complete redirect URL here: ").strip()
    
    try:
        # Extract request token
        request_token = redirect_url.split("request_token=")[1].split("&")[0]
        print(f"\n✅ Request token extracted: {request_token[:8]}...")
        
        # Generate session
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        
        print(f"✅ Access token generated successfully!")
        print(f"   User: {data.get('user_name', 'N/A')}")
        print(f"   Email: {data.get('email', 'N/A')}")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Failed to generate access token: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you copied the COMPLETE URL")
        print("2. Check if your API secret is correct")
        print("3. Try logging in again")
        return None


def test_connection(api_key, access_token):
    """Test the API connection"""
    print("\n🧪 Testing Zerodha Connection...")
    
    try:
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        
        # Get profile
        profile = kite.profile()
        print(f"✅ Connected successfully!")
        print(f"   Name: {profile['user_name']}")
        print(f"   User ID: {profile['user_id']}")
        print(f"   Email: {profile['email']}")
        print(f"   Broker: {profile['broker']}")
        
        # Get funds
        margins = kite.margins()
        if 'equity' in margins:
            available = margins['equity']['available']['cash']
            print(f"\n💰 Available Cash: ₹{available:,.2f}")
        
        # Get positions
        positions = kite.positions()
        open_positions = [p for p in positions['day'] if p['quantity'] != 0]
        print(f"📊 Open Positions: {len(open_positions)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


def create_live_trading_script():
    """Create a script to start live trading"""
    script_content = """#!/usr/bin/env python3
'''
Start LIVE Trading with Zerodha
WARNING: This will trade with REAL MONEY!
'''

import sys
import asyncio
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from main import run_bot


if __name__ == "__main__":
    print('''
    ⚠️  WARNING: LIVE TRADING MODE ⚠️
    ==================================
    This will trade with REAL MONEY!
    
    Settings:
    - Capital: ₹100,000
    - Risk per trade: 2%
    - Stop Loss: 30%
    - Target: 8%
    
    Press Ctrl+C to stop
    ''')
    
    response = input("\\nType 'YES' to start LIVE trading: ")
    
    if response == 'YES':
        print("\\n🚀 Starting LIVE trading...")
        asyncio.run(run_bot())
    else:
        print("❌ Live trading cancelled")
"""
    
    with open("start_live_trading.py", "w") as f:
        f.write(script_content)
    
    os.chmod("start_live_trading.py", 0o755)
    print("✅ Created start_live_trading.py")


def main():
    print_header()
    
    # Check if already configured
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        if config.get('broker', {}).get('name') == 'zerodha':
            print("⚠️  Zerodha is already configured!")
            response = input("\nReconfigure? (yes/no): ")
            if response.lower() != 'yes':
                print("Using existing configuration.")
                return
    
    # Get credentials
    api_key, api_secret = get_credentials()
    
    # Generate access token
    print("\n📱 Starting authentication...")
    access_token = generate_access_token(api_key, api_secret)
    
    if not access_token:
        print("\n❌ Setup failed. Please try again.")
        return
    
    # Test connection
    if test_connection(api_key, access_token):
        # Save configuration
        save_credentials(api_key, api_secret, access_token)
        
        # Create live trading script
        create_live_trading_script()
        
        print("\n" + "=" * 60)
        print("🎉 ZERODHA SETUP COMPLETE!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Review risk settings in config/config.yaml")
        print("2. Test with small capital first")
        print("3. Run: python3 start_live_trading.py")
        print("\n⚠️  IMPORTANT:")
        print("- Access token expires daily at 7:30 AM")
        print("- Run this setup again to refresh token")
        print("- Always monitor your first few trades closely")
    else:
        print("\n❌ Setup incomplete. Please check your credentials.")


if __name__ == "__main__":
    main()