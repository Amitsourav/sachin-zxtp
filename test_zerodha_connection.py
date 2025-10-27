#!/usr/bin/env python3
"""
Test Zerodha API Connection
Verify that your credentials and access token are working
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from kiteconnect import KiteConnect
except ImportError:
    print("Installing kiteconnect...")
    import os
    os.system("pip3 install kiteconnect")
    from kiteconnect import KiteConnect


def test_connection():
    """Test Zerodha API connection with credentials from config"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║              TESTING ZERODHA CONNECTION                      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Load config
    config_path = Path("config/config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    broker_config = config.get('broker', {})
    
    # Check configuration
    print("📋 Configuration Check:")
    print("-" * 50)
    print(f"Broker Name: {broker_config.get('name')}")
    print(f"API Key: {broker_config.get('api_key', 'NOT SET')[:10]}...")
    print(f"API Secret: {'***' if broker_config.get('api_secret') else 'NOT SET'}")
    print(f"Access Token: {broker_config.get('access_token', 'NOT SET')[:20]}..." if broker_config.get('access_token') else "Access Token: NOT SET")
    print(f"Trading Mode: {config['trading']['mode']}")
    print(f"Capital: ₹{config['trading']['capital']:,.2f}")
    
    if not all([broker_config.get('api_key'), broker_config.get('api_secret'), broker_config.get('access_token')]):
        print("\n❌ Missing credentials! Please check config.yaml")
        return False
    
    # Test connection
    print("\n🔌 Testing API Connection...")
    print("-" * 50)
    
    try:
        kite = KiteConnect(api_key=broker_config['api_key'])
        kite.set_access_token(broker_config['access_token'])
        
        # Get profile
        profile = kite.profile()
        print(f"✅ Connected Successfully!")
        print(f"   User: {profile['user_name']}")
        print(f"   Email: {profile['email']}")
        print(f"   Broker: {profile['broker']}")
        
        # Get account details
        print("\n💰 Account Details:")
        print("-" * 50)
        
        margins = kite.margins()
        if 'equity' in margins:
            equity = margins['equity']
            available_cash = equity.get('available', {}).get('cash', 0)
            used = equity.get('utilised', {}).get('debits', 0)
            total = equity.get('net', 0)
            
            print(f"Available Cash: ₹{available_cash:,.2f}")
            print(f"Used Margin: ₹{used:,.2f}")
            print(f"Total Equity: ₹{total:,.2f}")
        
        # Get positions
        print("\n📊 Current Positions:")
        print("-" * 50)
        positions = kite.positions()
        open_positions = [p for p in positions['day'] if p['quantity'] != 0]
        
        if open_positions:
            for pos in open_positions:
                print(f"Symbol: {pos['tradingsymbol']}")
                print(f"  Qty: {pos['quantity']}, Avg: ₹{pos['average_price']}")
                print(f"  P&L: ₹{pos['pnl']:,.2f}")
        else:
            print("No open positions")
        
        # Get today's orders
        print("\n📝 Today's Orders:")
        print("-" * 50)
        orders = kite.orders()
        today_orders = [o for o in orders if o['order_timestamp'].date() == datetime.now().date()] if orders else []
        
        if today_orders:
            for order in today_orders[:5]:  # Show last 5
                print(f"{order['tradingsymbol']} - {order['transaction_type']} {order['quantity']} @ ₹{order['price']}")
                print(f"  Status: {order['status']}")
        else:
            print("No orders today")
        
        # Test market data
        print("\n📈 Testing Market Data Access:")
        print("-" * 50)
        
        try:
            # Get quote for NIFTY
            quote = kite.quote(["NSE:NIFTY BANK"])
            if quote:
                nifty = list(quote.values())[0]
                print(f"NIFTY BANK: ₹{nifty['last_price']:,.2f}")
                print(f"  Change: {nifty['net_change']['points']:+.2f} ({nifty['net_change']['percentage']:+.2f}%)")
            
            # Get RELIANCE quote
            reliance = kite.quote(["NSE:RELIANCE"])
            if reliance:
                rel = list(reliance.values())[0]
                print(f"RELIANCE: ₹{rel['last_price']:,.2f}")
        except Exception as e:
            print(f"Market data error (may need subscription): {e}")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - READY FOR LIVE TRADING!")
        print("="*60)
        
        print("\n⚠️  Important Reminders:")
        print("1. Access token expires daily at 7:30 AM")
        print("2. Current mode: " + ("LIVE (Real Money!)" if config['trading']['mode'] == 'live' else "PAPER (Safe)"))
        print("3. Risk per trade: {}%".format(config['risk']['max_risk_per_trade']))
        print("4. Daily loss limit: ₹{:,.2f}".format(config['risk']['max_daily_loss']))
        
        print("\n🚀 To start trading:")
        print("   python3 main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection Failed: {e}")
        print("\nPossible issues:")
        print("1. Access token expired (regenerate with get_access_token.py)")
        print("2. Wrong API credentials")
        print("3. Network issues")
        print("4. API rate limit")
        
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)