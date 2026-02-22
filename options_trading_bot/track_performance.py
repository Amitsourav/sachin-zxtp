#!/usr/bin/env python3
"""
Track trading performance in real-time
"""

from kiteconnect import KiteConnect
import yaml
import time
from datetime import datetime
import json
import os

def load_trade_data():
    """Load current trade data"""
    trade_file = 'current_trade.json'
    if os.path.exists(trade_file):
        with open(trade_file, 'r') as f:
            return json.load(f)
    return None

def track_performance():
    """Track current trade performance"""
    print("📊 TRADE PERFORMANCE TRACKER")
    print("=" * 50)
    
    # Load config
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    kite = KiteConnect(api_key=config['broker']['api_key'])
    kite.set_access_token(config['broker']['access_token'])
    
    # Load trade data
    trade_data = load_trade_data()
    if not trade_data:
        print("❌ No active trade found")
        print("Run CORRECT_915_NIFTY50.py first to create a trade")
        return
    
    symbol = trade_data['symbol']
    entry_price = trade_data['entry_price']
    quantity = trade_data['quantity']
    entry_time = trade_data['entry_time']
    
    print(f"Tracking: {symbol}")
    print(f"Entry: ₹{entry_price:.2f} at {entry_time}")
    print(f"Quantity: {quantity}")
    print("-" * 50)
    
    try:
        while True:
            try:
                # Get current price
                quote = kite.quote([f"NFO:{symbol}"])
                if f"NFO:{symbol}" in quote:
                    current_data = quote[f"NFO:{symbol}"]
                    current_price = current_data['last_price']
                    
                    # Calculate P&L
                    price_change = current_price - entry_price
                    pnl = price_change * quantity
                    pnl_pct = (price_change / entry_price) * 100
                    
                    # Show status
                    status = "🟢 PROFIT" if pnl > 0 else "🔴 LOSS" if pnl < 0 else "⚪ BREAK-EVEN"
                    
                    print(f"\r{datetime.now().strftime('%H:%M:%S')} | "
                          f"₹{current_price:.2f} | "
                          f"{price_change:+.2f} ({pnl_pct:+.1f}%) | "
                          f"P&L: ₹{pnl:+,.0f} | {status}", end="")
                    
                else:
                    print(f"\r{datetime.now().strftime('%H:%M:%S')} | Could not fetch price", end="")
                
            except Exception as e:
                print(f"\r{datetime.now().strftime('%H:%M:%S')} | Error: {str(e)[:30]}", end="")
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n📊 Final Performance Summary:")
        try:
            quote = kite.quote([f"NFO:{symbol}"])
            if f"NFO:{symbol}" in quote:
                current_data = quote[f"NFO:{symbol}"]
                current_price = current_data['last_price']
                
                price_change = current_price - entry_price
                pnl = price_change * quantity
                pnl_pct = (price_change / entry_price) * 100
                
                print(f"Final P&L: ₹{pnl:+,.2f} ({pnl_pct:+.2f}%)")
                print(f"Exit Price: ₹{current_price:.2f}")
                
        except:
            print("Could not get final price")
        
        print("👋 Tracking stopped")

if __name__ == "__main__":
    track_performance()