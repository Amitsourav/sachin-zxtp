#!/usr/bin/env python3
"""
Test fetching live price for option
"""

from kiteconnect import KiteConnect
import yaml
from pathlib import Path

# Load config
config_path = Path("config/config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

broker_config = config.get('broker', {})

# Initialize Zerodha
kite = KiteConnect(api_key=broker_config['api_key'])
kite.set_access_token(broker_config['access_token'])

print("""
╔══════════════════════════════════════════════════════════════╗
║           TESTING LIVE OPTION PRICE FETCH                     ║
╚══════════════════════════════════════════════════════════════╝
""")

# Test with HINDALCO option
option_symbol = "HINDALCO25OCT28800CE"
quote_key = f"NFO:{option_symbol}"

print(f"Testing: {option_symbol}")
print(f"Quote Key: {quote_key}")
print("-" * 60)

try:
    # Fetch quote
    print("Fetching quote from Zerodha...")
    quotes = kite.quote([quote_key])
    
    if quote_key in quotes:
        quote_data = quotes[quote_key]
        print(f"\n✅ SUCCESS! Got live data:")
        print(f"   Last Price: ₹{quote_data['last_price']:.2f}")
        print(f"   Open: ₹{quote_data['ohlc']['open']:.2f}")
        print(f"   High: ₹{quote_data['ohlc']['high']:.2f}")
        print(f"   Low: ₹{quote_data['ohlc']['low']:.2f}")
        print(f"   Close: ₹{quote_data['ohlc']['close']:.2f}")
        print(f"   Volume: {quote_data['volume']:,}")
        print(f"   Bid: ₹{quote_data['depth']['buy'][0]['price']:.2f}")
        print(f"   Ask: ₹{quote_data['depth']['sell'][0]['price']:.2f}")
        
        print(f"\n💰 CURRENT LIVE PRICE: ₹{quote_data['last_price']:.2f}")
    else:
        print(f"❌ Quote not found for {quote_key}")
        print(f"Available keys: {list(quotes.keys())}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    
# Try alternate format
print("\n" + "=" * 60)
print("Testing alternate formats...")

# Try without prefix
try:
    quotes2 = kite.quote(["NFO:HINDALCO25OCT28800CE", "NSE:HINDALCO"])
    print(f"Available quotes: {list(quotes2.keys())}")
    
    for key, data in quotes2.items():
        if 'HINDALCO' in key:
            print(f"\n{key}:")
            print(f"   Last Price: ₹{data['last_price']:.2f}")
            
except Exception as e:
    print(f"Error: {e}")