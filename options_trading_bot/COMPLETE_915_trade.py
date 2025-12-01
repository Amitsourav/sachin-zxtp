#!/usr/bin/env python3
"""
COMPLETE 9:15 STRATEGY - Find Top Gainer and Execute Trade Immediately
Single scan at 9:15:00 with immediate option trade execution
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import time

class Complete915Strategy:
    def __init__(self):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        self.capital = self.config['trading']['capital']
        self.positions = []
        
        print("=" * 80)
        print("COMPLETE 9:15 STRATEGY - INSTANT TRADE EXECUTION")
        print("=" * 80)
        print(f"Virtual Capital: ₹{self.capital:,.2f}")
        
        # Load NFO instruments
        print("Loading option contracts...")
        self.instruments = pd.DataFrame(self.kite.instruments('NFO'))
        print(f"Loaded {len(self.instruments)} option contracts")
        
        # UPDATED NIFTY50 watchlist (November 2025)
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
        
    def find_top_gainer(self):
        """Find top gaining stock RIGHT NOW"""
        print(f"🔍 Scanning NIFTY50 at {datetime.now().strftime('%H:%M:%S')}...")
        
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
            
            print("\nTop 3 Gainers RIGHT NOW:")
            print("-" * 50)
            for i, stock in enumerate(gainers[:3], 1):
                print(f"{i}. {stock['symbol']:<12} ₹{stock['ltp']:8.2f}  +{stock['change']:.2f}%")
            
            return gainers[0]
        
        return None
        
    def find_option_contract(self, underlying, spot_price):
        """Find option contract"""
        # Get next available expiry
        stock_options = self.instruments[
            (self.instruments['name'] == underlying) &
            (self.instruments['instrument_type'] == 'CE')
        ]
        
        if stock_options.empty:
            print(f"❌ No options found for {underlying}")
            return None
            
        # Find next available expiry
        future_expiries = stock_options[stock_options['expiry'] > datetime.now().date()]['expiry'].unique()
        
        if len(future_expiries) == 0:
            print(f"❌ No future expiries available for {underlying}")
            return None
            
        expiry = sorted(future_expiries)[0]
        options_df = stock_options[stock_options['expiry'] == expiry]
        
        # Find ATM strike
        strikes = sorted(options_df['strike'].unique())
        atm_strike = min(strikes, key=lambda x: abs(x - spot_price))
        
        option = options_df[options_df['strike'] == atm_strike].iloc[0]
        
        print(f"\n📋 Option Contract:")
        print(f"   {option['tradingsymbol']}")
        print(f"   Strike: {option['strike']} | Expiry: {expiry}")
        
        return option
        
    def get_option_price(self, option):
        """Get option price"""
        symbol_with_exchange = f"NFO:{option['tradingsymbol']}"
        
        try:
            quote = self.kite.quote([symbol_with_exchange])
            
            if symbol_with_exchange in quote:
                data = quote[symbol_with_exchange]
                print(f"💰 Option LTP: ₹{data['last_price']:.2f}")
                return data
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        return None
        
    def execute_complete_strategy(self):
        """Execute complete strategy in one go"""
        print(f"\n⚡ EXECUTING AT {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Step 1: Find top gainer
        top_gainer = self.find_top_gainer()
        
        if not top_gainer:
            print("❌ No gainers found")
            return
            
        print(f"\n✅ Selected: {top_gainer['symbol']} (+{top_gainer['change']:.2f}%)")
        
        # Step 2: Find option
        option = self.find_option_contract(top_gainer['symbol'], top_gainer['ltp'])
        
        if not option:
            print("❌ No option found")
            return
            
        # Step 3: Get option price
        option_data = self.get_option_price(option)
        
        if not option_data:
            print("❌ Could not get option price")
            return
            
        # Step 4: Calculate trade
        ltp = option_data['last_price']
        lot_size = option['lot_size']
        quantity = lot_size  # 1 lot
        investment = ltp * quantity
        
        # Step 5: Execute paper trade
        position = {
            'timestamp': datetime.now(),
            'underlying': top_gainer['symbol'],
            'option_symbol': option['tradingsymbol'],
            'entry_price': ltp,
            'target': ltp * 1.08,  # 8% target
            'stop_loss': ltp * 0.70,  # 30% stop loss
            'quantity': quantity,
            'investment': investment,
            'status': 'EXECUTED'
        }
        
        print(f"\n" + "="*60)
        print("🎯 TRADE EXECUTED!")
        print("="*60)
        print(f"Stock: {position['underlying']}")
        print(f"Option: {position['option_symbol']}")
        print(f"Entry: ₹{position['entry_price']:.2f}")
        print(f"Target: ₹{position['target']:.2f} (+8%)")
        print(f"Stop Loss: ₹{position['stop_loss']:.2f} (-30%)")
        print(f"Investment: ₹{position['investment']:,.2f}")
        print("="*60)
        
        return position

def main():
    print("🚀 COMPLETE 9:15 STRATEGY - INSTANT EXECUTION\n")
    
    try:
        strategy = Complete915Strategy()
        
        # Wait for 9:15:00 if needed
        now = datetime.now()
        current_time = now.time()
        
        if current_time < datetime.strptime("09:15", "%H:%M").time():
            target_time = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
            wait_seconds = (target_time - now).total_seconds()
            
            print(f"⏰ Waiting for market open: {wait_seconds:.1f} seconds")
            time.sleep(wait_seconds)
            print("🚀 MARKET OPEN! Executing now...")
        
        # Execute complete strategy
        position = strategy.execute_complete_strategy()
        
        if position:
            print(f"\n✅ SUCCESS: Trade executed for {position['underlying']}")
        else:
            print(f"\n❌ FAILED: Could not execute trade")
            
    except KeyboardInterrupt:
        print("\n⏹️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()