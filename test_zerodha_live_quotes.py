#!/usr/bin/env python3
"""
Test Zerodha live quotes to debug the issue
"""

from kiteconnect import KiteConnect
import yaml

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

api_key = config['broker']['api_key']
access_token = config['broker']['access_token']

# Initialize Kite
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

print("Testing Zerodha Live Quotes...")
print("=" * 60)

try:
    # Test with proper instrument tokens
    # NIFTY 50 stocks with their NSE exchange tokens
    test_symbols = {
        'NSE:RELIANCE': 738561,
        'NSE:TCS': 2953217,
        'NSE:INFY': 408065,
        'NSE:HDFCBANK': 341249,
        'NSE:ICICIBANK': 1270529,
        'NSE:ITC': 424961,
        'NSE:SBIN': 779521,
        'NSE:BHARTIARTL': 2714625,
        'NSE:KOTAKBANK': 492033,
        'NSE:LT': 2939649
    }
    
    # Method 1: Using exchange:symbol format
    print("\nMethod 1: Fetching with exchange:symbol format")
    print("-" * 40)
    symbols_list = list(test_symbols.keys())[:5]
    quotes = kite.quote(symbols_list)
    
    for symbol in symbols_list:
        if symbol in quotes:
            data = quotes[symbol]
            change_pct = ((data['last_price'] - data['ohlc']['close']) / data['ohlc']['close'] * 100) if data['ohlc']['close'] else 0
            print(f"{symbol:20} | LTP: ₹{data['last_price']:8.2f} | Change: {change_pct:+.2f}%")
    
    # Method 2: Using instrument tokens
    print("\nMethod 2: Fetching with instrument tokens")
    print("-" * 40)
    token_list = list(test_symbols.values())[:5]
    quotes2 = kite.quote(token_list)
    
    for symbol, token in list(test_symbols.items())[:5]:
        if token in quotes2:
            data = quotes2[token]
            change_pct = ((data['last_price'] - data['ohlc']['close']) / data['ohlc']['close'] * 100) if data['ohlc']['close'] else 0
            print(f"{symbol:20} | LTP: ₹{data['last_price']:8.2f} | Change: {change_pct:+.2f}%")
    
    # Find top gainers
    print("\nTop Gainers:")
    print("-" * 40)
    gainers = []
    for symbol in symbols_list:
        if symbol in quotes:
            data = quotes[symbol]
            change_pct = ((data['last_price'] - data['ohlc']['close']) / data['ohlc']['close'] * 100) if data['ohlc']['close'] else 0
            if change_pct > 0:
                gainers.append({
                    'symbol': symbol.split(':')[1],
                    'ltp': data['last_price'],
                    'change': change_pct
                })
    
    gainers.sort(key=lambda x: x['change'], reverse=True)
    
    if gainers:
        for i, stock in enumerate(gainers[:3], 1):
            print(f"{i}. {stock['symbol']:12} | ₹{stock['ltp']:8.2f} | +{stock['change']:.2f}%")
    else:
        print("No gainers found - all stocks are flat or down")
        print("\nShowing all stocks with their changes:")
        for symbol in symbols_list:
            if symbol in quotes:
                data = quotes[symbol]
                change_pct = ((data['last_price'] - data['ohlc']['close']) / data['ohlc']['close'] * 100) if data['ohlc']['close'] else 0
                print(f"  {symbol:20} | Change: {change_pct:+.2f}%")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("1. Access token expired - regenerate it")
    print("2. Market data subscription not active")
    print("3. API rate limit reached")