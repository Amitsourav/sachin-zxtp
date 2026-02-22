#!/usr/bin/env python3
"""
Example: Loading NIFTY50 from config file instead of hardcoding
This is faster than API but still maintainable
"""

import json
import os

class TradingBot:
    def __init__(self):
        # Load NIFTY50 from config file (still fast, but maintainable)
        self.nifty50_stocks = self.load_nifty50_stocks()
        
    def load_nifty50_stocks(self):
        """Load NIFTY50 list from config file"""
        config_path = 'config/nifty50_stocks.json'
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                print(f"✅ Loaded NIFTY50 list (Updated: {data['last_updated']})")
                return data['stocks']
        except FileNotFoundError:
            print("⚠️ Config file not found, using hardcoded list")
            # Fallback to hardcoded list
            return [
                'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', # ... etc
            ]
    
    def scan_stocks(self):
        """Now uses dynamic list from config"""
        print(f"Scanning {len(self.nifty50_stocks)} stocks...")
        # quotes = self.kite.quote(self.nifty50_stocks)
        
# Alternative: Fetch from web (slower but always current)
def fetch_nifty50_from_web():
    """
    Could scrape from:
    - moneycontrol.com/stocks/marketinfo/nifty50
    - nseindia.com
    - Or use unofficial APIs
    
    BUT this adds 500ms-2s delay at market open!
    """
    pass

if __name__ == "__main__":
    bot = TradingBot()
    print(f"Loaded {len(bot.nifty50_stocks)} NIFTY50 stocks")
    print("First 5:", bot.nifty50_stocks[:5])