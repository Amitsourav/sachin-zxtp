#!/usr/bin/env python3
"""
Quick test to show monitoring with updates every 3-4 seconds
"""

from kiteconnect import KiteConnect
import yaml
import time
from datetime import datetime

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

kite = KiteConnect(api_key=config['broker']['api_key'])
kite.set_access_token(config['broker']['access_token'])

print("="*70)
print("LIVE OPTION PRICE MONITORING - Updates every 3 seconds")
print("="*70)

# Test with SBILIFE option expiring tomorrow
option_symbol = "NFO:SBILIFE25OCT1900CE"
entry_price = 14.20  # Assuming entry at this price
quantity = 375
target = entry_price * 1.08
stop_loss = entry_price * 0.70

print(f"\nMonitoring: SBILIFE25OCT1900CE")
print(f"Entry Price: ₹{entry_price:.2f}")
print(f"Quantity: {quantity}")
print(f"Target: ₹{target:.2f} | Stop Loss: ₹{stop_loss:.2f}")
print("-"*70)
print("Time     | LTP    | Change | P&L        | Status")
print("-"*70)

try:
    for i in range(20):  # Monitor for ~1 minute
        quote = kite.quote([option_symbol])
        
        if option_symbol in quote:
            data = quote[option_symbol]
            ltp = data['last_price']
            
            # Calculate changes
            change = ltp - entry_price
            change_pct = (change / entry_price) * 100
            pnl = change * quantity
            
            # Status indicator
            if pnl > 0:
                status = "✅ Profit"
            elif pnl < 0:
                status = "❌ Loss"
            else:
                status = "⚪ Flat"
            
            # Check target/SL
            if ltp >= target:
                status = "🎯 TARGET HIT!"
            elif ltp <= stop_loss:
                status = "🛑 STOP LOSS!"
            
            # Print update
            print(f"{datetime.now().strftime('%H:%M:%S')} | "
                  f"₹{ltp:5.2f} | "
                  f"{change:+5.2f} | "
                  f"₹{pnl:+8.2f} | "
                  f"{status}")
            
            # Exit if target or SL hit
            if ltp >= target or ltp <= stop_loss:
                break
        
        time.sleep(3)  # Wait 3 seconds
        
except KeyboardInterrupt:
    print("\n\nMonitoring stopped by user")
    
print("-"*70)
print("Monitoring complete")