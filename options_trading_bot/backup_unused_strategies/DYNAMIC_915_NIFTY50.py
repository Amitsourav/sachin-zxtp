#!/usr/bin/env python3
"""
DYNAMIC 9:15 TRADING WITH LIVE NIFTY50 FETCHING
Fetches current NIFTY50 constituents from NSE API before trading
"""

import yaml
import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime
import requests
import time
import json

class DynamicNifty50Trader:
    def __init__(self):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize Kite
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        # Fetch LIVE NIFTY50 constituents
        self.nifty50_stocks = self.fetch_live_nifty50()
        
        print(f"✅ Initialized with {len(self.nifty50_stocks)} LIVE NIFTY50 stocks")
        
    def fetch_live_nifty50(self):
        """
        Fetch current NIFTY50 constituents from NSE
        Always gets the latest list - no more hardcoding!
        """
        print("\n🔄 Fetching LIVE NIFTY50 constituents from NSE...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Create session for NSE
            session = requests.Session()
            
            # Get main page first (for cookies)
            main_page = session.get('https://www.nseindia.com', headers=headers)
            
            # Get NIFTY50 constituents
            url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
            response = session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                stocks = []
                for item in data['data']:
                    symbol = item['symbol']
                    if symbol != 'NIFTY 50':  # Exclude index itself
                        # Handle special symbols
                        if symbol == 'M&M':
                            stocks.append('NSE:M&M')
                        elif symbol == 'L&T':
                            stocks.append('NSE:LT')
                        else:
                            stocks.append(f'NSE:{symbol}')
                
                print(f"✅ Successfully fetched {len(stocks)} stocks from NSE")
                
                # Save to cache
                self.save_to_cache(stocks)
                
                return stocks[:50]  # Ensure exactly 50
                
            else:
                print(f"❌ NSE API returned status: {response.status_code}")
                return self.load_from_cache()
                
        except Exception as e:
            print(f"❌ Error fetching from NSE: {e}")
            return self.load_from_cache()
    
    def save_to_cache(self, stocks):
        """Save fetched stocks to cache file"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'stocks': stocks
        }
        try:
            with open('config/nifty50_live_cache.json', 'w') as f:
                json.dump(cache_data, f, indent=2)
            print(f"💾 Cached {len(stocks)} stocks")
        except:
            pass
    
    def load_from_cache(self):
        """Load from cache if API fails"""
        try:
            with open('config/nifty50_live_cache.json', 'r') as f:
                cache = json.load(f)
                print(f"📂 Loaded {len(cache['stocks'])} stocks from cache")
                return cache['stocks']
        except:
            print("⚠️ No cache found, using fallback list")
            # Fallback to updated hardcoded list (Sept 2024)
            return [
                'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 'NSE:ICICIBANK',
                'NSE:KOTAKBANK', 'NSE:SBIN', 'NSE:BHARTIARTL', 'NSE:ITC', 'NSE:AXISBANK',
                'NSE:LT', 'NSE:BAJFINANCE', 'NSE:WIPRO', 'NSE:MARUTI', 'NSE:HCLTECH',
                'NSE:ASIANPAINT', 'NSE:ULTRACEMCO', 'NSE:TITAN', 'NSE:SUNPHARMA', 'NSE:TECHM',
                'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:M&M',
                'NSE:HINDUNILVR', 'NSE:ADANIPORTS', 'NSE:COALINDIA', 'NSE:DIVISLAB', 'NSE:DRREDDY',
                'NSE:UPL', 'NSE:ONGC', 'NSE:JSWSTEEL', 'NSE:GRASIM', 'NSE:BPCL',
                'NSE:CIPLA', 'NSE:EICHERMOT', 'NSE:MAXHEALTH', 'NSE:BAJAJFINSV', 'NSE:NESTLEIND',
                'NSE:BRITANNIA', 'NSE:TATACONSUM', 'NSE:HINDALCO', 'NSE:SBILIFE', 'NSE:APOLLOHOSP',
                'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT', 'NSE:INDIGO'
            ]
    
    def scan_for_top_gainers(self):
        """Scan LIVE NIFTY50 stocks for top gainers"""
        print(f"\n🔍 Scanning {len(self.nifty50_stocks)} LIVE NIFTY50 stocks...")
        
        quotes = self.kite.quote(self.nifty50_stocks)
        
        gainers = []
        for symbol in self.nifty50_stocks:
            if symbol in quotes:
                data = quotes[symbol]
                change = data.get('change_percent', data.get('net_change', 0))
                gainers.append({
                    'symbol': symbol,
                    'price': data['last_price'],
                    'change': change
                })
        
        # Sort by change percentage
        gainers.sort(key=lambda x: x['change'], reverse=True)
        
        print("\n📈 TOP 5 GAINERS (LIVE DATA):")
        print("-" * 40)
        for i, stock in enumerate(gainers[:5], 1):
            print(f"{i}. {stock['symbol']}: ₹{stock['price']:.2f} (+{stock['change']:.2f}%)")
        
        return gainers[0] if gainers else None
    
    def execute_trade(self):
        """Execute trade with LIVE NIFTY50 data"""
        print("\n" + "=" * 60)
        print(f"⚡ DYNAMIC 9:15 STRATEGY - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Get top gainer from LIVE NIFTY50
        top_gainer = self.scan_for_top_gainers()
        
        if top_gainer and top_gainer['change'] > 0.5:
            print(f"\n✅ TRADE SIGNAL: BUY {top_gainer['symbol']}")
            print(f"   Price: ₹{top_gainer['price']:.2f}")
            print(f"   Change: +{top_gainer['change']:.2f}%")
            
            # Place actual trade here
            # order = self.kite.place_order(...)
            
        else:
            print("\n❌ No strong gainers found in LIVE NIFTY50")


def main():
    print("=" * 60)
    print("DYNAMIC NIFTY50 TRADING SYSTEM")
    print("=" * 60)
    
    trader = DynamicNifty50Trader()
    
    # Show what stocks we're trading
    print("\n📋 LIVE NIFTY50 Stocks loaded:")
    print(f"Total: {len(trader.nifty50_stocks)}")
    print(f"Sample: {trader.nifty50_stocks[:5]}")
    
    # Execute trade
    trader.execute_trade()


if __name__ == "__main__":
    main()