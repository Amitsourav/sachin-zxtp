#!/usr/bin/env python3
"""
Check SHRIRAMFIN specifically
"""

from kiteconnect import KiteConnect
import yaml
from datetime import datetime

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    
kite = KiteConnect(api_key=config['broker']['api_key'])
kite.set_access_token(config['broker']['access_token'])

print(f"Checking at {datetime.now().strftime('%H:%M:%S')}")
print("=" * 50)

# Check specific stocks
test_stocks = [
    'NSE:SHRIRAMFIN',
    'NSE:VEDL', 
    'NSE:BPCL',
    'NSE:M&M',
    'NSE:TATASTEEL',
    'NSE:HINDALCO'
]

try:
    quotes = kite.quote(test_stocks)
    
    gainers = []
    for symbol in test_stocks:
        if symbol in quotes:
            data = quotes[symbol]
            prev_close = data['ohlc']['close']
            ltp = data['last_price']
            
            if prev_close > 0:
                change_pct = ((ltp - prev_close) / prev_close) * 100
                gainers.append({
                    'symbol': symbol.split(':')[1],
                    'ltp': ltp,
                    'change': change_pct
                })
    
    # Sort by gain
    gainers.sort(key=lambda x: x['change'], reverse=True)
    
    print("Current Performance:")
    for stock in gainers:
        marker = "🔴" if stock['change'] < 0 else "🟢"
        print(f"{marker} {stock['symbol']:<12} ₹{stock['ltp']:>8.2f}  {stock['change']:+6.2f}%")
    
    print(f"\nTop Gainer: {gainers[0]['symbol']} (+{gainers[0]['change']:.2f}%)")
    
except Exception as e:
    print(f"Error: {e}")