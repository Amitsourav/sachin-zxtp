#!/usr/bin/env python3
"""
FIXED LIVE 9:15 STRATEGY - REAL MONEY TRADING
All pandas errors and edge cases fixed
⚠️  WARNING: This places REAL orders with REAL money!
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys

class FixedLive915Trader:
    def __init__(self):
        # Load config - with better error handling
        config_path = 'config/config.yaml'
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            print("Please create config/config.yaml with your Zerodha credentials")
            sys.exit(1)
            
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
            
        # Validate config has required fields
        required_fields = ['broker', 'trading']
        for field in required_fields:
            if field not in self.config:
                print(f"❌ Missing '{field}' section in config.yaml")
                sys.exit(1)
                
        if 'api_key' not in self.config['broker'] or 'access_token' not in self.config['broker']:
            print("❌ Missing api_key or access_token in config.yaml")
            sys.exit(1)
            
        # Initialize Kite Connect
        try:
            self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
            self.kite.set_access_token(self.config['broker']['access_token'])
        except Exception as e:
            print(f"❌ Failed to initialize KiteConnect: {e}")
            sys.exit(1)
        
        self.capital = self.config['trading'].get('capital', 100000)
        self.live_positions = []
        
        print("🚨" * 40)
        print("⚠️  LIVE TRADING MODE - REAL MONEY AT RISK!")
        print("🚨" * 40)
        print(f"Capital: ₹{self.capital:,.2f}")
        
        # Verify account access with better error handling
        try:
            profile = self.kite.profile()
            print(f"✅ Connected to: {profile['user_name']} ({profile['user_id']})")
            
            # Check available margin
            margins = self.kite.margins()
            if 'equity' in margins and 'available' in margins['equity']:
                available_cash = margins['equity']['available'].get('cash', 0)
                print(f"💰 Available Cash: ₹{available_cash:,.2f}")
                
                if available_cash < 50000:
                    print("⚠️  WARNING: Low account balance!")
            else:
                print("⚠️  Could not fetch margin details")
                
        except Exception as e:
            print(f"❌ Account connection failed: {e}")
            print("\nPossible reasons:")
            print("1. Access token expired - regenerate using get_access_token.py")
            print("2. API credentials incorrect")
            print("3. Internet connection issues")
            raise
        
        # Load instruments with error handling
        print("Loading option contracts...")
        try:
            instruments_data = self.kite.instruments('NFO')
            if not instruments_data:
                print("❌ No NFO instruments data received")
                sys.exit(1)
            self.instruments = pd.DataFrame(instruments_data)
            print(f"✅ Loaded {len(self.instruments)} option contracts")
        except Exception as e:
            print(f"❌ Failed to load instruments: {e}")
            sys.exit(1)
        
        # Updated NIFTY50 watchlist (January 2025)
        self.watchlist = [
            'NSE:ADANIENT', 'NSE:ADANIPORTS', 'NSE:APOLLOHOSP', 'NSE:ASIANPAINT',
            'NSE:AXISBANK', 'NSE:BAJAJ-AUTO', 'NSE:BAJAJFINSV', 'NSE:BAJFINANCE',
            'NSE:BEL', 'NSE:BHARTIARTL', 'NSE:CIPLA', 'NSE:COALINDIA',
            'NSE:DRREDDY', 'NSE:EICHERMOT', 'NSE:ETERNAL', 'NSE:GRASIM',
            'NSE:HCLTECH', 'NSE:HDFCBANK', 'NSE:HDFCLIFE', 'NSE:HINDALCO',
            'NSE:HINDUNILVR', 'NSE:ICICIBANK', 'NSE:INDIGO', 'NSE:INFY',
            'NSE:ITC', 'NSE:JIOFIN', 'NSE:JSWSTEEL', 'NSE:KOTAKBANK',
            'NSE:LT', 'NSE:M&M', 'NSE:MARUTI', 'NSE:MAXHEALTH',
            'NSE:NESTLEIND', 'NSE:NTPC', 'NSE:ONGC', 'NSE:POWERGRID',
            'NSE:RELIANCE', 'NSE:SBILIFE', 'NSE:SBIN', 'NSE:SHRIRAMFIN',
            'NSE:SUNPHARMA', 'NSE:TATACONSUM', 'NSE:TATASTEEL', 'NSE:TCS',
            'NSE:TECHM', 'NSE:TITAN', 'NSE:TMPV', 'NSE:TRENT',
            'NSE:ULTRACEMCO', 'NSE:WIPRO'
        ]
        
    def find_top_gainer(self):
        """Find top gainer at market open with error handling"""
        print(f"🔍 LIVE SCAN at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            quotes = self.kite.quote(self.watchlist)
        except Exception as e:
            print(f"❌ Failed to fetch quotes: {e}")
            return None
            
        gainers = []
        failed_symbols = []
        
        for symbol in self.watchlist:
            try:
                if symbol in quotes:
                    data = quotes[symbol]
                    
                    # Safely access nested dictionary
                    if 'ohlc' in data and 'close' in data['ohlc']:
                        prev_close = data['ohlc']['close']
                    else:
                        failed_symbols.append(symbol)
                        continue
                        
                    ltp = data.get('last_price', 0)
                    
                    if prev_close > 0 and ltp > 0:
                        change_pct = ((ltp - prev_close) / prev_close) * 100
                        if change_pct > 0:
                            gainers.append({
                                'symbol': symbol.split(':')[1],
                                'ltp': ltp,
                                'change': change_pct,
                                'volume': data.get('volume', 0)
                            })
                else:
                    failed_symbols.append(symbol)
            except Exception as e:
                print(f"⚠️  Error processing {symbol}: {e}")
                failed_symbols.append(symbol)
                
        if failed_symbols:
            print(f"⚠️  Could not fetch data for: {', '.join(failed_symbols[:5])}")
        
        if gainers:
            gainers.sort(key=lambda x: x['change'], reverse=True)
            print(f"🎯 TOP GAINER: {gainers[0]['symbol']} (+{gainers[0]['change']:.2f}%)")
            
            # Show top 5 gainers
            print("\n📊 Top 5 Gainers:")
            for i, g in enumerate(gainers[:5], 1):
                print(f"   {i}. {g['symbol']}: +{g['change']:.2f}%")
            
            return gainers[0]
        else:
            print("❌ No gainers found in NIFTY50")
            return None
        
    def find_option_contract(self, underlying, spot_price):
        """Find tradeable option contract with comprehensive error handling"""
        try:
            # Create mask safely
            name_mask = self.instruments['name'] == underlying
            type_mask = self.instruments['instrument_type'] == 'CE'
            combined_mask = name_mask & type_mask
            
            # Apply mask using .loc to avoid ambiguous truth value
            stock_options = self.instruments.loc[combined_mask].copy()
            
            if len(stock_options) == 0:
                print(f"❌ No options found for {underlying}")
                return None
                
            # Find next expiry safely
            current_date = datetime.now().date()
            
            # Convert expiry to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(stock_options['expiry']):
                stock_options['expiry'] = pd.to_datetime(stock_options['expiry'])
            
            # Create future mask
            future_mask = stock_options['expiry'].dt.date > current_date
            
            if not future_mask.any():
                print(f"❌ No future expiries found for {underlying}")
                return None
                
            future_expiries = stock_options.loc[future_mask, 'expiry'].dt.date.unique()
            
            if len(future_expiries) == 0:
                print(f"❌ No valid future expiries for {underlying}")
                return None
                
            # Get nearest expiry
            expiry = sorted(future_expiries)[0]
            
            # Filter for selected expiry
            expiry_mask = stock_options['expiry'].dt.date == expiry
            options_df = stock_options.loc[expiry_mask].copy()
            
            if len(options_df) == 0:
                print(f"❌ No options for expiry {expiry}")
                return None
                
            # Find ATM strike
            strikes = sorted(options_df['strike'].unique())
            if not strikes:
                print(f"❌ No strikes available")
                return None
                
            atm_strike = min(strikes, key=lambda x: abs(x - spot_price))
            
            # Get the option contract
            strike_mask = options_df['strike'] == atm_strike
            final_options = options_df.loc[strike_mask]
            
            if len(final_options) == 0:
                print(f"❌ No option at strike {atm_strike}")
                return None
                
            option = final_options.iloc[0]
            print(f"✅ Found option: {option['tradingsymbol']} (Strike: {atm_strike}, Expiry: {expiry})")
            return option
            
        except Exception as e:
            print(f"❌ Error finding option contract: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def place_live_order(self, option, quantity):
        """⚠️  PLACE REAL ORDER WITH REAL MONEY - with error handling"""
        
        print(f"\n🚨 PLACING LIVE ORDER - REAL MONEY!")
        print("=" * 50)
        print(f"Symbol: {option['tradingsymbol']}")
        print(f"Strike: {option['strike']}")
        print(f"Quantity: {quantity} (Lot size: {option['lot_size']})")
        
        try:
            # Get current bid-ask for limit price
            option_symbol = f"NFO:{option['tradingsymbol']}"
            quote = self.kite.quote([option_symbol])
            
            if option_symbol in quote:
                option_data = quote[option_symbol]
                last_price = option_data['last_price']
                
                # Use current market price (LTP) as limit price for immediate execution
                limit_price = last_price  # Use LTP as limit price
                
                # Also get bid-ask for reference
                bid_price = option_data.get('depth', {}).get('buy', [{}])[0].get('price', last_price)
                ask_price = option_data.get('depth', {}).get('sell', [{}])[0].get('price', last_price)
                
                print(f"   Bid: ₹{bid_price:.2f} | Ask: ₹{ask_price:.2f} | LTP: ₹{last_price:.2f}")
                print(f"   Limit Price: ₹{limit_price:.2f} (using current market price)")
            else:
                print("⚠️  Could not fetch quote, using estimated price")
                limit_price = 100  # Fallback price
            
            # Place BUY order with LIMIT
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=self.kite.EXCHANGE_NFO,
                tradingsymbol=option['tradingsymbol'],
                transaction_type=self.kite.TRANSACTION_TYPE_BUY,
                quantity=quantity,
                product=self.kite.PRODUCT_MIS,  # Intraday
                order_type=self.kite.ORDER_TYPE_LIMIT,
                price=limit_price
            )
            
            print(f"✅ ORDER PLACED!")
            print(f"   Order ID: {order_id}")
            
            # Wait and check order status
            time.sleep(3)
            
            try:
                orders = self.kite.orders()
                for order in orders:
                    if str(order.get('order_id')) == str(order_id):
                        print(f"   Status: {order.get('status', 'UNKNOWN')}")
                        if order.get('status') == 'COMPLETE':
                            avg_price = order.get('average_price', 0)
                            print(f"   Executed at: ₹{avg_price}")
                            return {
                                'order_id': order_id,
                                'symbol': option['tradingsymbol'],
                                'quantity': quantity,
                                'price': float(avg_price),
                                'status': 'EXECUTED'
                            }
            except Exception as e:
                print(f"⚠️  Could not verify order status: {e}")
            
            return {'order_id': order_id, 'status': 'PENDING'}
            
        except Exception as e:
            print(f"❌ ORDER FAILED: {e}")
            
            # Provide specific error guidance
            error_str = str(e).lower()
            if 'insufficient' in error_str or 'margin' in error_str:
                print("💡 Insufficient funds. Please add more capital.")
            elif 'token' in error_str or 'session' in error_str:
                print("💡 Session expired. Regenerate access token.")
            elif 'symbol' in error_str:
                print("💡 Invalid symbol. Check if option is active.")
            else:
                print(f"💡 Check Zerodha terminal for more details")
                
            return None
            
    def execute_live_strategy(self):
        """⚠️  EXECUTE WITH REAL MONEY - with comprehensive error handling"""
        
        # Final safety check
        print(f"\n🚨 FINAL WARNING!")
        print("=" * 50)
        print("This will place REAL orders with REAL money!")
        print("Type 'CONFIRM LIVE TRADING' to proceed:")
        
        confirmation = input().strip()
        if confirmation != "CONFIRM LIVE TRADING":
            print("❌ Live trading cancelled")
            return
            
        print(f"\n⚡ EXECUTING LIVE STRATEGY")
        print("=" * 50)
        
        # Find top gainer
        top_gainer = self.find_top_gainer()
        if not top_gainer:
            print("❌ No gainer found - strategy aborted")
            return
            
        # Minimum gain threshold
        if top_gainer['change'] < 1.0:
            print(f"⚠️  Top gainer only up {top_gainer['change']:.2f}% - too low")
            print("Strategy requires minimum 1% gain")
            return
            
        # Find option
        option = self.find_option_contract(top_gainer['symbol'], top_gainer['ltp'])
        if option is None:
            print("❌ No suitable option found")
            return
            
        # Calculate quantity (using lot size)
        quantity = int(option['lot_size'])
        
        # Estimate required capital
        try:
            # Get current option price
            option_quote = self.kite.quote([f"NFO:{option['tradingsymbol']}"])
            if option_quote and f"NFO:{option['tradingsymbol']}" in option_quote:
                option_ltp = option_quote[f"NFO:{option['tradingsymbol']}"].get('last_price', 100)
                required_capital = option_ltp * quantity
                print(f"💰 Estimated capital required: ₹{required_capital:,.2f}")
            else:
                print("⚠️  Could not fetch option price for estimation")
        except:
            print("⚠️  Could not estimate required capital")
        
        # Place live order
        result = self.place_live_order(option, quantity)
        
        if result:
            if result.get('status') == 'EXECUTED':
                print(f"\n✅ LIVE TRADE EXECUTED SUCCESSFULLY!")
                print(f"   Order ID: {result.get('order_id')}")
                print(f"   Symbol: {result.get('symbol')}")
                print(f"   Quantity: {result.get('quantity')}")
                print(f"   Price: ₹{result.get('price', 0)}")
                investment = result.get('price', 0) * result.get('quantity', 0)
                print(f"   Total Investment: ₹{investment:,.2f}")
                print(f"\n📱 Check your Zerodha app for live position")
            elif result.get('status') == 'PENDING':
                print(f"\n⏳ Order placed but pending execution")
                print(f"   Order ID: {result.get('order_id')}")
                print("   Check Zerodha for status")
        else:
            print(f"\n❌ Trade failed - check error messages above")

def main():
    print("🚨 FIXED LIVE 9:15 TRADING - REAL MONEY MODE")
    print("=" * 50)
    print("⚠️  WARNING: This uses REAL money!")
    print("⚠️  Only proceed if you understand the risks!")
    print("⚠️  Options can lose 100% of premium!")
    
    try:
        trader = FixedLive915Trader()
        
        # Wait for market open if needed
        now = datetime.now()
        market_open = datetime.strptime("09:15", "%H:%M").time()
        current_time = now.time()
        
        if current_time < market_open:
            target_time = datetime.combine(now.date(), market_open)
            wait_seconds = (target_time - now).total_seconds()
            
            if wait_seconds > 0:
                print(f"\n⏰ Market opens at 9:15 AM")
                print(f"   Current time: {now.strftime('%H:%M:%S')}")
                print(f"   Waiting {wait_seconds:.0f} seconds...")
                
                # Show countdown
                while wait_seconds > 0:
                    mins, secs = divmod(int(wait_seconds), 60)
                    print(f"\r   Time to market open: {mins:02d}:{secs:02d}", end="")
                    time.sleep(1)
                    wait_seconds -= 1
                print("\n\n🔔 MARKET IS NOW OPEN!")
        
        # Add 1-1.5 second delay at 9:15 to let market stabilize
        import random
        delay = random.uniform(1.0, 1.5)
        print(f"⏳ Waiting {delay:.2f} seconds for market to stabilize...")
        time.sleep(delay)
        
        # Execute live strategy
        trader.execute_live_strategy()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Trading cancelled by user")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        import traceback
        print("\nFull error trace:")
        traceback.print_exc()

if __name__ == "__main__":
    main()