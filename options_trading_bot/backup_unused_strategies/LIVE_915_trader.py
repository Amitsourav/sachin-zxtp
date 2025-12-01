#!/usr/bin/env python3
"""
LIVE 9:15 STRATEGY - REAL MONEY TRADING
⚠️  WARNING: This places REAL orders with REAL money!
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import time

class Live915Trader:
    def __init__(self):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        self.capital = self.config['trading']['capital']
        self.live_positions = []
        
        print("🚨" * 40)
        print("⚠️  LIVE TRADING MODE - REAL MONEY AT RISK!")
        print("🚨" * 40)
        print(f"Capital: ₹{self.capital:,.2f}")
        
        # Verify account access
        try:
            profile = self.kite.profile()
            print(f"✅ Connected to: {profile['user_name']} ({profile['user_id']})")
            
            # Check available margin
            margins = self.kite.margins()
            available_cash = margins['equity']['available']['cash']
            print(f"💰 Available Cash: ₹{available_cash:,.2f}")
            
            if available_cash < 50000:
                print("⚠️  WARNING: Low account balance!")
                
        except Exception as e:
            print(f"❌ Account connection failed: {e}")
            raise
        
        # Load instruments
        print("Loading option contracts...")
        self.instruments = pd.DataFrame(self.kite.instruments('NFO'))
        
        # NIFTY50 watchlist
        self.watchlist = [
            'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 'NSE:HDFC',
            'NSE:ICICIBANK', 'NSE:KOTAKBANK', 'NSE:SBIN', 'NSE:BHARTIARTL', 'NSE:ITC',
            'NSE:AXISBANK', 'NSE:LT', 'NSE:BAJFINANCE', 'NSE:WIPRO', 'NSE:MARUTI',
            'NSE:HCLTECH', 'NSE:ASIANPAINT', 'NSE:ULTRACEMCO', 'NSE:TITAN', 'NSE:SUNPHARMA',
            'NSE:TECHM', 'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:INDUSINDBK',
            'NSE:M&M', 'NSE:HINDUNILVR', 'NSE:ADANIPORTS', 'NSE:COALINDIA', 'NSE:DIVISLAB',
            'NSE:DRREDDY', 'NSE:UPL', 'NSE:ONGC', 'NSE:JSWSTEEL', 'NSE:GRASIM',
            'NSE:BPCL', 'NSE:CIPLA', 'NSE:EICHERMOT', 'NSE:SHREECEM', 'NSE:MAXHEALTH',
            'NSE:BAJAJFINSV', 'NSE:NESTLEIND', 'NSE:BRITANNIA', 'NSE:TATACONSUM', 'NSE:ADANIENT',
            'NSE:HINDALCO', 'NSE:SBILIFE', 'NSE:APOLLOHOSP', 'NSE:TATASTEEL', 'NSE:VEDL'
        ]
        
    def find_top_gainer(self):
        """Find top gainer at market open"""
        print(f"🔍 LIVE SCAN at {datetime.now().strftime('%H:%M:%S')}")
        
        quotes = self.kite.quote(self.watchlist)
        gainers = []
        
        for symbol in self.watchlist:
            if symbol in quotes:
                data = quotes[symbol]
                prev_close = data['ohlc']['close']
                ltp = data['last_price']
                
                if prev_close > 0:
                    change_pct = ((ltp - prev_close) / prev_close) * 100
                    if change_pct > 0:
                        gainers.append({
                            'symbol': symbol.split(':')[1],
                            'ltp': ltp,
                            'change': change_pct,
                            'volume': data.get('volume', 0)
                        })
        
        if gainers:
            gainers.sort(key=lambda x: x['change'], reverse=True)
            print(f"🎯 TOP GAINER: {gainers[0]['symbol']} (+{gainers[0]['change']:.2f}%)")
            return gainers[0]
        
        return None
        
    def find_option_contract(self, underlying, spot_price):
        """Find tradeable option contract"""
        # Fix: Use .loc to avoid ambiguous truth value
        mask = (self.instruments['name'] == underlying) & (self.instruments['instrument_type'] == 'CE')
        stock_options = self.instruments.loc[mask]
        
        if len(stock_options) == 0:
            return None
            
        # Find next expiry
        current_date = datetime.now().date()
        future_mask = stock_options['expiry'] > current_date
        future_expiries = stock_options.loc[future_mask, 'expiry'].unique()
        if len(future_expiries) == 0:
            return None
            
        expiry = sorted(future_expiries)[0]
        expiry_mask = stock_options['expiry'] == expiry
        options_df = stock_options.loc[expiry_mask]
        
        # Find ATM strike
        strikes = sorted(options_df['strike'].unique())
        atm_strike = min(strikes, key=lambda x: abs(x - spot_price))
        
        strike_mask = options_df['strike'] == atm_strike
        return options_df.loc[strike_mask].iloc[0]
        
    def place_live_order(self, option, quantity):
        """⚠️  PLACE REAL ORDER WITH REAL MONEY!"""
        
        print(f"\n🚨 PLACING LIVE ORDER - REAL MONEY!")
        print("=" * 50)
        
        try:
            # Place BUY order
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=self.kite.EXCHANGE_NFO,
                tradingsymbol=option['tradingsymbol'],
                transaction_type=self.kite.TRANSACTION_TYPE_BUY,
                quantity=quantity,
                product=self.kite.PRODUCT_MIS,  # Intraday
                order_type=self.kite.ORDER_TYPE_MARKET
            )
            
            print(f"✅ ORDER PLACED!")
            print(f"   Order ID: {order_id}")
            print(f"   Symbol: {option['tradingsymbol']}")
            print(f"   Quantity: {quantity}")
            
            # Wait and check order status
            time.sleep(2)
            
            orders = self.kite.orders()
            for order in orders:
                if order['order_id'] == order_id:
                    print(f"   Status: {order['status']}")
                    if order['status'] == 'COMPLETE':
                        print(f"   Executed at: ₹{order['average_price']}")
                        return {
                            'order_id': order_id,
                            'symbol': option['tradingsymbol'],
                            'quantity': quantity,
                            'price': float(order['average_price']),
                            'status': 'EXECUTED'
                        }
            
            return {'order_id': order_id, 'status': 'PENDING'}
            
        except Exception as e:
            print(f"❌ ORDER FAILED: {e}")
            return None
            
    def execute_live_strategy(self):
        """⚠️  EXECUTE WITH REAL MONEY!"""
        
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
            print("❌ No gainer found")
            return
            
        # Find option
        option = self.find_option_contract(top_gainer['symbol'], top_gainer['ltp'])
        if not option:
            print("❌ No option found")
            return
            
        print(f"📋 Option: {option['tradingsymbol']}")
        
        # Calculate quantity (1 lot for safety)
        quantity = option['lot_size']
        
        # Place live order
        result = self.place_live_order(option, quantity)
        
        if result and result['status'] == 'EXECUTED':
            print(f"\n✅ LIVE TRADE EXECUTED!")
            print(f"   Investment: ₹{result['price'] * quantity:,.2f}")
            print(f"   Check your Zerodha account for position")
        else:
            print(f"\n❌ Trade failed or pending")

def main():
    print("🚨 LIVE 9:15 TRADING - REAL MONEY MODE")
    print("=" * 50)
    print("⚠️  WARNING: This uses REAL money!")
    print("⚠️  Only proceed if you understand the risks!")
    print("⚠️  Options can lose 100% of premium!")
    
    try:
        trader = Live915Trader()
        
        # Wait for market open
        now = datetime.now()
        current_time = now.time()
        
        if current_time < datetime.strptime("09:15", "%H:%M").time():
            target_time = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
            wait_seconds = (target_time - now).total_seconds()
            
            print(f"⏰ Waiting {wait_seconds:.1f} seconds for market open...")
            time.sleep(wait_seconds)
        
        # Execute live strategy
        trader.execute_live_strategy()
        
    except KeyboardInterrupt:
        print("\n⏹️  Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()