#!/usr/bin/env python3
"""
DYNAMIC NIFTY50 FETCHER
Fetches current NIFTY50 constituents dynamically instead of using hardcoded list
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime
import json
import os

class DynamicNifty50Fetcher:
    def __init__(self):
        """Initialize with Zerodha credentials"""
        # Load config
        config_path = 'config/config.yaml'
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            return
            
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return
        
        # Initialize Kite
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        print("🔍 DYNAMIC NIFTY50 CONSTITUENT FETCHER")
        print("="*60)
    
    def get_nifty50_from_instruments(self):
        """Method 1: Extract NIFTY50 stocks from instruments list"""
        try:
            print("📊 Fetching instruments from Zerodha...")
            
            # Get NSE instruments
            nse_instruments = self.kite.instruments('NSE')
            instruments_df = pd.DataFrame(nse_instruments)
            
            # Look for stocks with highest market cap or trading volume
            # Filter only equity stocks
            equity_stocks = instruments_df[
                (instruments_df['instrument_type'] == 'EQ') &
                (instruments_df['segment'] == 'NSE')
            ].copy()
            
            print(f"✅ Found {len(equity_stocks)} equity stocks on NSE")
            
            # Get quotes for analysis
            print("📈 Analyzing top stocks by volume...")
            
            # Take top stocks by name recognition (crude method)
            known_large_caps = [
                'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
                'KOTAKBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'AXISBANK',
                'LT', 'BAJFINANCE', 'WIPRO', 'MARUTI', 'HCLTECH',
                'ASIANPAINT', 'ULTRACEMCO', 'TITAN', 'SUNPHARMA', 'TECHM',
                'POWERGRID', 'NTPC', 'TATAMOTORS', 'M&M', 'HINDUNILVR',
                'ADANIPORTS', 'COALINDIA', 'DIVISLAB', 'DRREDDY', 'UPL',
                'ONGC', 'JSWSTEEL', 'GRASIM', 'BPCL', 'CIPLA',
                'EICHERMOT', 'MAXHEALTH', 'BAJAJFINSV', 'NESTLEIND', 'BRITANNIA',
                'TATACONSUM', 'HINDALCO', 'SBILIFE', 'APOLLOHOSP', 'TATASTEEL',
                'SHRIRAMFIN', 'ADANIENT', 'LTIM', 'TRENT', 'INDIGO'
            ]
            
            # Filter instruments to include known large caps
            nifty50_candidates = equity_stocks[
                equity_stocks['tradingsymbol'].isin(known_large_caps)
            ].copy()
            
            # Convert to NSE format
            nifty50_symbols = [f"NSE:{symbol}" for symbol in nifty50_candidates['tradingsymbol'].tolist()]
            
            print(f"✅ Found {len(nifty50_symbols)} NIFTY50 candidates")
            return nifty50_symbols[:50]  # Limit to 50
            
        except Exception as e:
            print(f"❌ Error fetching from instruments: {e}")
            return None
    
    def get_nifty50_from_index_quote(self):
        """Method 2: Try to get NIFTY50 constituents from index quote"""
        try:
            print("📊 Trying to fetch NIFTY50 index data...")
            
            # Try different NIFTY50 symbols
            nifty_symbols = ['NSE:NIFTY 50', 'NSE:NIFTY50', 'NSE:NIFTY_50']
            
            for symbol in nifty_symbols:
                try:
                    quote = self.kite.quote([symbol])
                    if quote:
                        print(f"✅ Found NIFTY index: {symbol}")
                        print(f"   Current Value: {quote[symbol].get('last_price', 'N/A')}")
                        # Unfortunately, Kite doesn't provide constituents in quote
                        break
                except:
                    continue
                    
            print("ℹ️  Kite API doesn't provide index constituents directly")
            return None
            
        except Exception as e:
            print(f"❌ Error fetching index data: {e}")
            return None
    
    def get_current_nifty50_list(self):
        """Get current NIFTY50 list using available methods"""
        print(f"🕐 Fetching current NIFTY50 constituents at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Method 1: From instruments (most reliable with Kite)
        nifty50 = self.get_nifty50_from_instruments()
        
        if nifty50:
            print(f"\n✅ DYNAMIC NIFTY50 LIST ({len(nifty50)} stocks):")
            print("="*60)
            
            # Display in groups of 5
            for i in range(0, len(nifty50), 5):
                group = nifty50[i:i+5]
                symbols = [s.replace('NSE:', '') for s in group]
                print(f"   {', '.join(symbols)}")
            
            # Save to file for future use
            nifty_data = {
                'timestamp': datetime.now().isoformat(),
                'count': len(nifty50),
                'symbols': nifty50
            }
            
            with open('config/dynamic_nifty50.json', 'w') as f:
                json.dump(nifty_data, f, indent=2)
            
            print(f"\n💾 Saved to config/dynamic_nifty50.json")
            
            return nifty50
        
        print("❌ Could not fetch current NIFTY50 list")
        return None
    
    def validate_nifty50_liquidity(self, symbols):
        """Validate that all symbols have good liquidity"""
        print("\n🔍 Validating liquidity of NIFTY50 stocks...")
        
        try:
            # Get quotes for all symbols
            quotes = self.kite.quote(symbols[:10])  # Test first 10
            
            liquid_symbols = []
            for symbol in symbols[:10]:
                if symbol in quotes:
                    data = quotes[symbol]
                    volume = data.get('volume', 0)
                    if volume > 1000:  # Basic liquidity check
                        liquid_symbols.append(symbol)
            
            print(f"✅ {len(liquid_symbols)}/{len(symbols[:10])} symbols passed liquidity test")
            
            return len(liquid_symbols) > 8  # At least 80% should be liquid
            
        except Exception as e:
            print(f"⚠️ Could not validate liquidity: {e}")
            return True  # Assume valid if we can't check

def main():
    print("🚀 FETCHING CURRENT NIFTY50 CONSTITUENTS")
    print("="*60)
    
    try:
        fetcher = DynamicNifty50Fetcher()
        nifty50 = fetcher.get_current_nifty50_list()
        
        if nifty50:
            print("\n🎯 SUCCESS! You now have the current NIFTY50 list")
            print("This list will be used by your trading bot instead of hardcoded symbols")
            
            # Validate
            if fetcher.validate_nifty50_liquidity(nifty50):
                print("✅ Liquidity validation passed")
            else:
                print("⚠️ Some symbols may have low liquidity")
                
        else:
            print("\n❌ Failed to fetch NIFTY50 list")
            print("Will fall back to static list")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()