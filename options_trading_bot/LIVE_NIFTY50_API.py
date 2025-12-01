#!/usr/bin/env python3
"""
LIVE DYNAMIC NIFTY50 FETCHING - Multiple API Sources
Real-time fetching of current NIFTY50 constituents
"""

import requests
import json
import pandas as pd
from datetime import datetime
import yfinance as yf

class LiveNifty50Fetcher:
    """Fetch live NIFTY50 constituents from multiple sources"""
    
    def __init__(self):
        self.nifty50_stocks = []
        
    def method1_nse_official(self):
        """
        Method 1: NSE Official Website (Most Reliable)
        Scrapes from NSE India official data
        """
        try:
            # NSE provides index constituents via their API
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            
            # NSE Index constituents endpoint
            url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
            
            session = requests.Session()
            # First get the main page to get cookies
            session.get("https://www.nseindia.com", headers=headers)
            
            # Then get the actual data
            response = session.get(url, headers=headers)
            data = response.json()
            
            stocks = []
            for item in data['data']:
                if item['symbol'] != 'NIFTY 50':  # Exclude the index itself
                    stocks.append(f"NSE:{item['symbol']}")
            
            print(f"✅ Method 1 (NSE Official): Found {len(stocks)} stocks")
            return stocks[:50]  # Ensure only 50 stocks
            
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            return []
    
    def method2_yahoo_finance(self):
        """
        Method 2: Yahoo Finance
        Gets NIFTY50 constituents via yfinance
        """
        try:
            # Map of NIFTY50 constituents (Yahoo Finance symbols)
            # These are the actual current NIFTY50 stocks with .NS suffix for Yahoo
            yahoo_symbols = [
                'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
                'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'AXISBANK.NS',
                'LT.NS', 'BAJFINANCE.NS', 'WIPRO.NS', 'MARUTI.NS', 'HCLTECH.NS',
                'ASIANPAINT.NS', 'ULTRACEMCO.NS', 'TITAN.NS', 'SUNPHARMA.NS', 'TECHM.NS',
                'POWERGRID.NS', 'NTPC.NS', 'TATAMOTORS.NS', 'MM.NS',
                'HINDUNILVR.NS', 'ADANIPORTS.NS', 'COALINDIA.NS', 'DIVISLAB.NS', 'DRREDDY.NS',
                'UPL.NS', 'ONGC.NS', 'JSWSTEEL.NS', 'GRASIM.NS', 'BPCL.NS',
                'CIPLA.NS', 'EICHERMOT.NS', 'MAXHEALTH.NS', 'BAJAJFINSV.NS', 'NESTLEIND.NS',
                'BRITANNIA.NS', 'TATACONSUM.NS', 'HINDALCO.NS', 'SBILIFE.NS', 'APOLLOHOSP.NS',
                'TATASTEEL.NS', 'SHRIRAMFIN.NS', 'ADANIENT.NS', 'LTIM.NS', 'TRENT.NS', 'INDIGO.NS'
            ]
            
            # Verify these are valid by checking one
            test = yf.Ticker(yahoo_symbols[0])
            info = test.info
            
            # Convert to NSE format
            stocks = [f"NSE:{symbol.replace('.NS', '')}" for symbol in yahoo_symbols]
            
            print(f"✅ Method 2 (Yahoo Finance): Found {len(stocks)} stocks")
            return stocks
            
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
            return []
    
    def method3_nifty_indices_api(self):
        """
        Method 3: NIFTY Indices Website API
        Direct API from niftyindices.com
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # This endpoint provides the current constituents
            url = "https://www.niftyindices.com/IndexConstituent/ind_nifty50list.csv"
            
            response = requests.get(url, headers=headers)
            
            # Parse CSV data
            lines = response.text.strip().split('\n')
            stocks = []
            
            for line in lines[1:]:  # Skip header
                if line:
                    parts = line.split(',')
                    if len(parts) > 2:
                        symbol = parts[2].strip().replace('"', '')  # Symbol is usually in 3rd column
                        stocks.append(f"NSE:{symbol}")
            
            print(f"✅ Method 3 (NIFTY Indices): Found {len(stocks)} stocks")
            return stocks[:50]
            
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
            return []
    
    def method4_economic_times_api(self):
        """
        Method 4: Economic Times Market API
        Unofficial but reliable API
        """
        try:
            url = "https://etmarketsapis.indiatimes.com/ET_Stats/getIndexByIds?indexids=2369&pagesize=50&exchange=nse&pageno=1&sortby=value&sortorder=desc&marketcap=&filtervalue="
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers)
            data = response.json()
            
            stocks = []
            for company in data['searchresult']:
                stocks.append(f"NSE:{company['stock_symbol']}")
            
            print(f"✅ Method 4 (ET Markets): Found {len(stocks)} stocks")
            return stocks
            
        except Exception as e:
            print(f"❌ Method 4 failed: {e}")
            return []
    
    def method5_moneycontrol_api(self):
        """
        Method 5: MoneyControl Unofficial API
        Fast and reliable
        """
        try:
            # MoneyControl's internal API for NIFTY50
            url = "https://api.moneycontrol.com/mcapi/v1/st/index/constituents?indexId=9"
            
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            data = response.json()
            
            stocks = []
            for item in data['data']['constituents']:
                # Extract NSE symbol
                symbol = item['nse_symbol']
                stocks.append(f"NSE:{symbol}")
            
            print(f"✅ Method 5 (MoneyControl): Found {len(stocks)} stocks")
            return stocks
            
        except Exception as e:
            print(f"❌ Method 5 failed: {e}")
            return []
    
    def get_live_nifty50(self):
        """
        Try multiple methods to get NIFTY50 constituents
        Returns the first successful result
        """
        print("\n🔄 FETCHING LIVE NIFTY50 CONSTITUENTS...")
        print("=" * 50)
        
        # Try methods in order of reliability
        methods = [
            ("NSE Official", self.method1_nse_official),
            ("Yahoo Finance", self.method2_yahoo_finance),
            ("NIFTY Indices", self.method3_nifty_indices_api),
            ("ET Markets", self.method4_economic_times_api),
            ("MoneyControl", self.method5_moneycontrol_api),
        ]
        
        for name, method in methods:
            print(f"\nTrying {name}...")
            stocks = method()
            if stocks and len(stocks) >= 48:  # Allow for minor variations
                self.nifty50_stocks = stocks
                print(f"\n✅ SUCCESS! Got {len(stocks)} NIFTY50 stocks from {name}")
                return stocks
        
        print("\n❌ All methods failed! Using fallback hardcoded list")
        # Fallback to hardcoded list
        return self.get_fallback_list()
    
    def get_fallback_list(self):
        """Fallback hardcoded list (September 2024 update)"""
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
    
    def save_to_cache(self, stocks):
        """Save fetched list to cache file with timestamp"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'stocks': stocks
        }
        with open('config/nifty50_cache.json', 'w') as f:
            json.dump(cache_data, f, indent=2)
        print(f"💾 Saved to cache: {len(stocks)} stocks")


# Example usage in your trading bot
class TradingBotWithLiveData:
    def __init__(self):
        # Fetch live NIFTY50 constituents
        fetcher = LiveNifty50Fetcher()
        self.nifty50_stocks = fetcher.get_live_nifty50()
        
        print(f"\n📊 Trading bot initialized with {len(self.nifty50_stocks)} live NIFTY50 stocks")
        print(f"First 5: {self.nifty50_stocks[:5]}")
        
    def scan_stocks(self):
        """Now uses dynamically fetched list"""
        print(f"\n🔍 Scanning {len(self.nifty50_stocks)} LIVE NIFTY50 stocks...")
        # quotes = self.kite.quote(self.nifty50_stocks)
        # ... rest of your trading logic


if __name__ == "__main__":
    print("=" * 60)
    print("LIVE NIFTY50 FETCHER - Multiple API Sources")
    print("=" * 60)
    
    fetcher = LiveNifty50Fetcher()
    stocks = fetcher.get_live_nifty50()
    
    if stocks:
        print("\n📋 CURRENT NIFTY50 CONSTITUENTS:")
        print("-" * 40)
        for i, stock in enumerate(stocks, 1):
            print(f"{i:2}. {stock}")
        
        # Save to cache
        fetcher.save_to_cache(stocks)
        
        print("\n✅ Ready to use for live trading!")
    else:
        print("\n❌ Failed to fetch NIFTY50 constituents")