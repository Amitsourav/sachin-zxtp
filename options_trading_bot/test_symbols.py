#!/usr/bin/env python3
"""
Test script to verify NIFTY50 symbols
"""

from kiteconnect import KiteConnect
import yaml

def test_symbols():
    # Load config
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
    kite = KiteConnect(api_key=config['broker']['api_key'])
    kite.set_access_token(config['broker']['access_token'])
    
    # Test different variations of SHRIRAMFINANCE
    test_symbols = [
        'NSE:SHRIRAMFIN',
        'NSE:SHRIRAMFINANCE', 
        'NSE:SRTRANSFIN',
        'NSE:SHRIRAM'
    ]
    
    print("Testing SHRIRAMFINANCE symbol variations...")
    
    for symbol in test_symbols:
        try:
            quote = kite.quote([symbol])
            if symbol in quote:
                data = quote[symbol]
                print(f"✅ {symbol}: ₹{data['last_price']} ({data['instrument_token']})")
            else:
                print(f"❌ {symbol}: Not found")
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
    
    # Also test current top gainers from sample list
    print("\nTesting other NIFTY50 symbols...")
    sample_symbols = ['NSE:VEDL', 'NSE:BPCL', 'NSE:RELIANCE']
    
    try:
        quotes = kite.quote(sample_symbols)
        for symbol in sample_symbols:
            if symbol in quotes:
                data = quotes[symbol]
                prev_close = data['ohlc']['close']
                ltp = data['last_price']
                change_pct = ((ltp - prev_close) / prev_close) * 100
                print(f"✅ {symbol}: ₹{ltp:.2f} ({change_pct:+.2f}%)")
    except Exception as e:
        print(f"Error getting quotes: {e}")

if __name__ == "__main__":
    test_symbols()