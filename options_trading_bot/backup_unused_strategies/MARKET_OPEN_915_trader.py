#!/usr/bin/env python3
"""
MARKET OPEN 9:15 STRATEGY - FIXED TIMING ISSUE
This version ensures scanning happens AFTER market opens at 9:15 AM
Uses real-time prices, not pre-market or yesterday's closing prices
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta, time
import time as time_module
import os
import sys

class MarketOpen915Trader:
    def __init__(self):
        """Initialize trader but DON'T scan yet"""
        # Load config
        config_path = 'config/config.yaml'
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            sys.exit(1)
            
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
            
        # Initialize Kite Connect
        try:
            self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
            self.kite.set_access_token(self.config['broker']['access_token'])
        except Exception as e:
            print(f"❌ Failed to initialize KiteConnect: {e}")
            sys.exit(1)
        
        self.capital = self.config['trading'].get('capital', 100000)
        
        print("="*80)
        print("📈 MARKET OPEN 9:15 TRADING STRATEGY")
        print("="*80)
        print(f"Capital: ₹{self.capital:,.2f}")
        
        # Verify account access
        try:
            profile = self.kite.profile()
            print(f"✅ Connected to: {profile['user_name']} ({profile['user_id']})")
            
            margins = self.kite.margins()
            if 'equity' in margins and 'available' in margins['equity']:
                available_cash = margins['equity']['available'].get('cash', 0)
                print(f"💰 Available Cash: ₹{available_cash:,.2f}")
        except Exception as e:
            print(f"❌ Account connection failed: {e}")
            raise
        
        # Load instruments
        print("Loading option contracts...")
        try:
            instruments_data = self.kite.instruments('NFO')
            self.instruments = pd.DataFrame(instruments_data)
            print(f"✅ Loaded {len(self.instruments)} option contracts")
        except Exception as e:
            print(f"❌ Failed to load instruments: {e}")
            sys.exit(1)
        
        # NIFTY50 watchlist
        self.watchlist = [
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
    
    def wait_for_market_open(self):
        """Wait until EXACTLY 9:15 AM or later"""
        market_open_time = time(9, 15, 0)  # 9:15:00 AM
        
        while True:
            now = datetime.now()
            current_time = now.time()
            
            # Check if market is open (9:15 AM or later)
            if current_time >= market_open_time:
                # Double check it's a weekday
                if now.weekday() < 5:  # Monday = 0, Friday = 4
                    print(f"\n✅ Market is OPEN! Current time: {now.strftime('%H:%M:%S')}")
                    return True
                else:
                    print("❌ Today is weekend. Markets are closed.")
                    return False
            
            # Calculate wait time
            target = datetime.combine(now.date(), market_open_time)
            wait_seconds = (target - now).total_seconds()
            
            if wait_seconds > 0:
                mins, secs = divmod(int(wait_seconds), 60)
                print(f"\r⏰ Waiting for market open (9:15 AM): {mins:02d}:{secs:02d} remaining", end="")
                time_module.sleep(1)
            else:
                # Should not happen but just in case
                time_module.sleep(1)
    
    def scan_after_market_open(self):
        """
        Scan IMMEDIATELY when market opens - NO DELAYS!
        The 9:15 strategy works on volatility - speed is critical!
        """
        print(f"\n⚡ IMMEDIATE SCAN at {datetime.now().strftime('%H:%M:%S')}")
        print("🔥 9:15 VOLATILITY STRATEGY - EXECUTING NOW!")
        
        try:
            # Fetch LIVE quotes after market open
            quotes = self.kite.quote(self.watchlist)
        except Exception as e:
            print(f"❌ Failed to fetch quotes: {e}")
            return None
        
        gainers = []
        
        for symbol in self.watchlist:
            try:
                if symbol in quotes:
                    data = quotes[symbol]
                    
                    # Get yesterday's close
                    if 'ohlc' in data and 'close' in data['ohlc']:
                        yesterday_close = data['ohlc']['close']
                    else:
                        continue
                    
                    # Get CURRENT market price (not pre-market!)
                    current_price = data.get('last_price', 0)
                    
                    # Get today's open price
                    today_open = data['ohlc'].get('open', 0)
                    
                    if yesterday_close > 0 and current_price > 0:
                        # Calculate gain from yesterday's close
                        change_from_close = ((current_price - yesterday_close) / yesterday_close) * 100
                        
                        # Calculate gain from today's open
                        change_from_open = 0
                        if today_open > 0:
                            change_from_open = ((current_price - today_open) / today_open) * 100
                        
                        if change_from_close > 0:  # Only gainers
                            gainers.append({
                                'symbol': symbol.split(':')[1],
                                'current_price': current_price,
                                'yesterday_close': yesterday_close,
                                'today_open': today_open,
                                'change_from_close': change_from_close,
                                'change_from_open': change_from_open,
                                'volume': data.get('volume', 0),
                                'timestamp': datetime.now().strftime('%H:%M:%S')
                            })
            except Exception as e:
                print(f"⚠️ Error processing {symbol}: {e}")
        
        if gainers:
            # Sort by gain from yesterday's close
            gainers.sort(key=lambda x: x['change_from_close'], reverse=True)
            
            print("\n📊 TOP GAINERS (After Market Open):")
            print("-" * 80)
            print(f"{'Rank':<5} {'Symbol':<12} {'Current':<10} {'From Close':<12} {'From Open':<12} {'Volume':<10}")
            print("-" * 80)
            
            for i, g in enumerate(gainers[:10], 1):
                print(f"{i:<5} {g['symbol']:<12} ₹{g['current_price']:<10.2f} "
                      f"+{g['change_from_close']:<11.2f}% "
                      f"{g['change_from_open']:+11.2f}% "
                      f"{g['volume']:<10,}")
            
            top_gainer = gainers[0]
            print("\n" + "="*80)
            print(f"🎯 SELECTED TOP GAINER: {top_gainer['symbol']}")
            print(f"   Current Price: ₹{top_gainer['current_price']:.2f}")
            print(f"   Gain from Close: +{top_gainer['change_from_close']:.2f}%")
            print(f"   Gain from Open: {top_gainer['change_from_open']:+.2f}%")
            print(f"   Scan Time: {top_gainer['timestamp']}")
            print("="*80)
            
            return top_gainer
        else:
            print("❌ No gainers found after market open")
            return None
    
    def find_option_contract(self, underlying, spot_price):
        """Find best option contract"""
        try:
            # Create mask for options
            name_mask = self.instruments['name'] == underlying
            type_mask = self.instruments['instrument_type'] == 'CE'
            combined_mask = name_mask & type_mask
            
            stock_options = self.instruments.loc[combined_mask].copy()
            
            if len(stock_options) == 0:
                print(f"❌ No options found for {underlying}")
                return None
            
            # Find next expiry
            current_date = datetime.now().date()
            
            if not pd.api.types.is_datetime64_any_dtype(stock_options['expiry']):
                stock_options['expiry'] = pd.to_datetime(stock_options['expiry'])
            
            future_mask = stock_options['expiry'].dt.date > current_date
            
            if not future_mask.any():
                return None
            
            future_expiries = stock_options.loc[future_mask, 'expiry'].dt.date.unique()
            
            if len(future_expiries) == 0:
                return None
            
            expiry = sorted(future_expiries)[0]
            
            expiry_mask = stock_options['expiry'].dt.date == expiry
            options_df = stock_options.loc[expiry_mask].copy()
            
            if len(options_df) == 0:
                return None
            
            # Find ATM strike
            strikes = sorted(options_df['strike'].unique())
            if not strikes:
                return None
            
            atm_strike = min(strikes, key=lambda x: abs(x - spot_price))
            
            strike_mask = options_df['strike'] == atm_strike
            final_options = options_df.loc[strike_mask]
            
            if len(final_options) == 0:
                return None
            
            option = final_options.iloc[0]
            print(f"\n✅ Found Option:")
            print(f"   Symbol: {option['tradingsymbol']}")
            print(f"   Strike: {atm_strike}")
            print(f"   Expiry: {expiry}")
            print(f"   Lot Size: {option['lot_size']}")
            
            return option
            
        except Exception as e:
            print(f"❌ Error finding option: {e}")
            return None
    
    def place_order(self, option, quantity, is_paper_trade=True):
        """Place order (paper or live)"""
        
        if is_paper_trade:
            print("\n📝 PAPER TRADE EXECUTION")
            print("="*50)
            
            try:
                # Get current option price
                option_quote = self.kite.quote([f"NFO:{option['tradingsymbol']}"])
                if option_quote and f"NFO:{option['tradingsymbol']}" in option_quote:
                    option_price = option_quote[f"NFO:{option['tradingsymbol']}"].get('last_price', 0)
                    total_value = option_price * quantity
                    
                    print(f"✅ PAPER TRADE EXECUTED")
                    print(f"   Symbol: {option['tradingsymbol']}")
                    print(f"   Quantity: {quantity}")
                    print(f"   Price: ₹{option_price:.2f}")
                    print(f"   Total Value: ₹{total_value:,.2f}")
                    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
                    
                    return {
                        'status': 'EXECUTED',
                        'price': option_price,
                        'quantity': quantity,
                        'value': total_value
                    }
            except Exception as e:
                print(f"❌ Paper trade error: {e}")
                return None
        else:
            # Live trading code here
            print("\n🚨 LIVE ORDER - REAL MONEY!")
            # ... live order code ...
    
    def execute_strategy(self, is_paper_trade=True):
        """Main strategy execution"""
        
        print("\n" + "="*80)
        if is_paper_trade:
            print("📝 PAPER TRADING MODE (No Real Money)")
        else:
            print("🚨 LIVE TRADING MODE (REAL MONEY!)")
        print("="*80)
        
        # Step 1: Wait for market to open
        print("\n📅 Step 1: Checking market status...")
        if not self.wait_for_market_open():
            print("❌ Market is closed. Exiting.")
            return
        
        # Step 2: Scan IMMEDIATELY when market opens - NO DELAYS!
        print("\n📊 Step 2: Scanning for top gainers...")
        top_gainer = self.scan_after_market_open()
        
        if not top_gainer:
            print("❌ No suitable stock found")
            return
        
        # Step 3: Minimum gain check (lowered to 0.3% for testing)
        MIN_GAIN_THRESHOLD = 0.3  # Lowered from 1.0% to 0.3%
        if top_gainer['change_from_close'] < MIN_GAIN_THRESHOLD:
            print(f"\n⚠️ Top gainer only up {top_gainer['change_from_close']:.2f}%")
            print(f"Minimum {MIN_GAIN_THRESHOLD}% gain required. Exiting.")
            return
        
        # Step 4: Find option contract
        print("\n🔍 Step 3: Finding option contract...")
        option = self.find_option_contract(
            top_gainer['symbol'], 
            top_gainer['current_price']
        )
        
        if option is None:
            print("❌ No suitable option found")
            return
        
        # Step 5: Execute trade
        print("\n💼 Step 4: Executing trade...")
        quantity = int(option['lot_size'])
        
        if not is_paper_trade:
            # Extra confirmation for live trading
            print("\n⚠️  FINAL WARNING!")
            print("This will place a REAL order with REAL money!")
            print("Type 'CONFIRM LIVE TRADING' to proceed:")
            
            confirmation = input().strip()
            if confirmation != "CONFIRM LIVE TRADING":
                print("❌ Live trading cancelled")
                return
        
        # Execute order
        result = self.place_order(option, quantity, is_paper_trade)
        
        if result and result['status'] == 'EXECUTED':
            print("\n" + "="*80)
            print("✅ TRADE SUCCESSFULLY EXECUTED!")
            print(f"   Stock: {top_gainer['symbol']}")
            print(f"   Stock Price: ₹{top_gainer['current_price']:.2f}")
            print(f"   Stock Gain: +{top_gainer['change_from_close']:.2f}%")
            print(f"   Option: {option['tradingsymbol']}")
            print(f"   Option Price: ₹{result['price']:.2f}")
            print(f"   Total Investment: ₹{result['value']:,.2f}")
            print("="*80)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='9:15 AM Trading Strategy')
    parser.add_argument('--live', action='store_true', help='Enable LIVE trading (real money)')
    args = parser.parse_args()
    
    print("="*80)
    print("🕐 9:15 AM MARKET OPEN TRADING STRATEGY")
    print("="*80)
    
    if args.live:
        print("⚠️  LIVE TRADING MODE - REAL MONEY AT RISK!")
        print("⚠️  Options can lose 100% of premium!")
    else:
        print("📝 PAPER TRADING MODE - No real money")
    
    try:
        trader = MarketOpen915Trader()
        
        # Important: Strategy will wait for 9:15 AM automatically
        # and scan AFTER market opens with real-time prices
        trader.execute_strategy(is_paper_trade=not args.live)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Trading cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()