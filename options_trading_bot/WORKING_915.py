#!/usr/bin/env python3
"""
WORKING 9:15 STRATEGY - Fixed version that won't hang
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime
import time

class Working915Strategy:
    def __init__(self):
        print("Initializing...")
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        print("✅ Connected successfully")
        
    def find_top_gainer(self):
        """Simple top gainer finder"""
        stocks = [
            'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 'NSE:ICICIBANK',
            'NSE:KOTAKBANK', 'NSE:SBIN', 'NSE:BHARTIARTL', 'NSE:ITC', 'NSE:AXISBANK'
        ]
        
        print(f"Scanning {len(stocks)} stocks...")
        
        try:
            quotes = self.kite.quote(stocks)
            
            gainers = []
            for symbol in stocks:
                if symbol in quotes:
                    data = quotes[symbol]
                    change = ((data['last_price'] - data['ohlc']['close']) / data['ohlc']['close']) * 100
                    if change > 0:
                        gainers.append({
                            'symbol': symbol.split(':')[1],
                            'ltp': data['last_price'],
                            'change': change
                        })
            
            if gainers:
                gainers.sort(key=lambda x: x['change'], reverse=True)
                top = gainers[0]
                print(f"✅ Top Gainer: {top['symbol']} (+{top['change']:.2f}%)")
                return top
                
        except Exception as e:
            print(f"Error scanning: {e}")
        
        return None
    
    def execute(self):
        """Simple execution"""
        print(f"\n⚡ EXECUTING at {datetime.now().strftime('%H:%M:%S')}")
        
        top_gainer = self.find_top_gainer()
        
        if top_gainer:
            print(f"\n" + "="*50)
            print(f"TRADE SIGNAL")
            print(f"="*50)
            print(f"Stock: {top_gainer['symbol']}")
            print(f"Price: ₹{top_gainer['ltp']:.2f}")
            print(f"Change: +{top_gainer['change']:.2f}%")
            print(f"Action: BUY CALL OPTION")
            print(f"="*50)
            return True
        else:
            print("No gainers found")
            return False

def main():
    print("🚀 WORKING 9:15 STRATEGY")
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Initialize
    strategy = Working915Strategy()
    
    # Check time and wait
    now = datetime.now()
    if now.time() < datetime.strptime("09:15", "%H:%M").time():
        target = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
        wait = (target - now).total_seconds()
        
        if wait > 0:
            print(f"⏰ Waiting {wait:.0f} seconds for 9:15...")
            
            # Simple wait - no complex logic
            time.sleep(wait)
            
            print(f"🔔 9:15 REACHED!")
    
    # Execute immediately
    strategy.execute()
    print("\n✅ Complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user")
    except Exception as e:
        print(f"Error: {e}")