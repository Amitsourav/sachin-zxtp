#!/usr/bin/env python3
"""
FINAL WORKING VERSION - Paper Trading with Actual Zerodha Option Prices
This version correctly fetches real option prices with proper expiry dates
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import asyncio

class ZerodhaOptionTrading:
    def __init__(self):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        # Virtual capital for paper trading
        self.capital = self.config['trading']['capital']
        self.positions = []
        
        print("=" * 80)
        print("PAPER TRADING WITH ACTUAL ZERODHA OPTION PRICES")
        print("=" * 80)
        print(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Virtual Capital: ₹{self.capital:,.2f}")
        
        # Load NFO instruments
        print("\nLoading option contracts from NSE...")
        self.instruments = pd.DataFrame(self.kite.instruments('NFO'))
        print(f"Loaded {len(self.instruments)} option contracts")
        
    def find_top_gainer(self):
        """Find top gaining stock from FULL NIFTY50"""
        # UPDATED NIFTY50 list (November 2025)
        watchlist = [
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
        
        print("\n📊 Scanning for top gainers...")
        quotes = self.kite.quote(watchlist)
        
        gainers = []
        for symbol in watchlist:
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
            
            print("\nTop 3 Gainers:")
            print("-" * 50)
            for i, stock in enumerate(gainers[:3], 1):
                print(f"{i}. {stock['symbol']:<12} ₹{stock['ltp']:8.2f}  +{stock['change']:.2f}%")
            
            return gainers[0]
        
        return None
        
    def find_option_contract(self, underlying, spot_price):
        """Find the best option contract for the stock"""
        
        # Get tomorrow's date (Oct 28, 2025)
        tomorrow = datetime(2025, 10, 28).date()
        
        # Find options for this stock
        stock_options = self.instruments[
            (self.instruments['name'] == underlying) &
            (self.instruments['instrument_type'] == 'CE')
        ]
        
        if stock_options.empty:
            print(f"❌ No options found for {underlying}")
            return None
            
        # Check if tomorrow expiry exists
        tomorrow_options = stock_options[stock_options['expiry'] == tomorrow]
        
        if not tomorrow_options.empty:
            expiry = tomorrow
            options_df = tomorrow_options
            print(f"\n📅 Using tomorrow's expiry: {expiry} (Tuesday)")
        else:
            # Find next available expiry
            future_expiries = stock_options[stock_options['expiry'] > datetime.now().date()]['expiry'].unique()
            
            if len(future_expiries) == 0:
                print(f"❌ No future expiries available for {underlying}")
                return None
                
            expiry = sorted(future_expiries)[0]
            options_df = stock_options[stock_options['expiry'] == expiry]
            print(f"\n📅 Next available expiry: {expiry} ({expiry.strftime('%A')})")
        
        # Find ATM strike
        strikes = sorted(options_df['strike'].unique())
        atm_strike = min(strikes, key=lambda x: abs(x - spot_price))
        
        # Get the specific option contract
        option = options_df[options_df['strike'] == atm_strike].iloc[0]
        
        days_to_expiry = (expiry - datetime.now().date()).days
        
        print(f"\n📋 Selected Option Contract:")
        print(f"   Symbol: {option['tradingsymbol']}")
        print(f"   Strike: {option['strike']}")
        print(f"   Expiry: {expiry} ({days_to_expiry} days)")
        print(f"   Lot Size: {option['lot_size']}")
        
        return option
        
    def get_option_price(self, option):
        """Get live price for the option"""
        # Use NFO: prefix with trading symbol
        symbol_with_exchange = f"NFO:{option['tradingsymbol']}"
        
        try:
            quote = self.kite.quote([symbol_with_exchange])
            
            if symbol_with_exchange in quote:
                data = quote[symbol_with_exchange]
                
                print(f"\n💰 Live Option Price:")
                print(f"   LTP: ₹{data['last_price']:.2f}")
                
                if data['depth']['buy'] and data['depth']['sell']:
                    bid = data['depth']['buy'][0]['price']
                    ask = data['depth']['sell'][0]['price']
                    spread = ask - bid
                    print(f"   Bid: ₹{bid:.2f}")
                    print(f"   Ask: ₹{ask:.2f}")
                    print(f"   Spread: ₹{spread:.2f}")
                
                print(f"   Volume: {data.get('volume', 0):,}")
                print(f"   OI: {data.get('oi', 0):,}")
                
                return data
                
        except Exception as e:
            print(f"❌ Error fetching option price: {e}")
            
        return None
        
    def execute_strategy(self):
        """Execute the 9:15 strategy with paper trading"""
        print("\n" + "="*60)
        print("EXECUTING 9:15 STRATEGY - REAL-TIME SCAN")
        print("="*60)
        
        # Step 1: Find top gainer AT MARKET OPEN (critical timing)
        print("🔍 Scanning for top gainer at market open...")
        top_gainer = self.find_top_gainer()
        
        if not top_gainer:
            print("❌ No gaining stocks found")
            return
            
        print(f"\n✅ Selected Stock: {top_gainer['symbol']}")
        print(f"   Current Price: ₹{top_gainer['ltp']:.2f}")
        print(f"   Day Change: +{top_gainer['change']:.2f}%")
        print(f"   Volume: {top_gainer['volume']:,}")
        
        # Step 2: Find option contract
        option = self.find_option_contract(top_gainer['symbol'], top_gainer['ltp'])
        
        if option is None:
            return
            
        # Step 3: Get option price
        option_data = self.get_option_price(option)
        
        if option_data is None:
            return
            
        ltp = option_data['last_price']
        lot_size = option['lot_size']
        
        # Step 4: Calculate position size
        risk_per_trade = 0.02  # 2% of capital
        risk_amount = self.capital * risk_per_trade
        
        # Calculate lots based on 30% stop loss
        max_loss_per_lot = ltp * lot_size * 0.30
        
        if max_loss_per_lot > 0:
            num_lots = max(1, int(risk_amount / max_loss_per_lot))
        else:
            num_lots = 1
            
        quantity = num_lots * lot_size
        investment = ltp * quantity
        
        # Position details
        position = {
            'timestamp': datetime.now(),
            'underlying': top_gainer['symbol'],
            'option_symbol': option['tradingsymbol'],
            'strike': option['strike'],
            'expiry': option['expiry'],
            'lots': num_lots,
            'quantity': quantity,
            'lot_size': lot_size,
            'entry_price': ltp,
            'target': ltp * 1.08,  # 8% profit target
            'stop_loss': ltp * 0.70,  # 30% stop loss
            'investment': investment,
            'max_risk': investment * 0.30,
            'token': f"NFO:{option['tradingsymbol']}",
            'status': 'OPEN'
        }
        
        self.positions.append(position)
        
        print(f"\n" + "="*60)
        print("✅ PAPER TRADE EXECUTED")
        print("="*60)
        print(f"Option: {position['option_symbol']}")
        print(f"Strike: {position['strike']} | Expiry: {position['expiry']}")
        print(f"Lots: {num_lots} x {lot_size} = {quantity} quantity")
        print(f"Entry Price: ₹{ltp:.2f}")
        print(f"Investment: ₹{investment:,.2f}")
        print(f"Target (8%): ₹{position['target']:.2f}")
        print(f"Stop Loss (30%): ₹{position['stop_loss']:.2f}")
        print(f"Max Risk: ₹{position['max_risk']:,.2f}")
        print("="*60)
        
        # Start monitoring
        asyncio.run(self.monitor_position(position))
        
    async def monitor_position(self, position):
        """Monitor the position with live prices"""
        print("\n📊 MONITORING POSITION (Press Ctrl+C to stop)")
        print("-" * 60)
        
        while position['status'] == 'OPEN':
            try:
                # Get live price
                quote = self.kite.quote([position['token']])
                
                if position['token'] in quote:
                    data = quote[position['token']]
                    current_price = data['last_price']
                    
                    # Calculate P&L
                    pnl = (current_price - position['entry_price']) * position['quantity']
                    pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    
                    # Display update on new line each time
                    time_str = datetime.now().strftime('%H:%M:%S')
                    
                    # Color coding for P&L
                    if pnl > 0:
                        pnl_str = f"₹{pnl:+,.2f} ({pnl_percent:+.2f}%) ✅"
                    elif pnl < 0:
                        pnl_str = f"₹{pnl:+,.2f} ({pnl_percent:+.2f}%) ❌"
                    else:
                        pnl_str = f"₹{pnl:+,.2f} ({pnl_percent:+.2f}%) ⚪"
                    
                    print(f"[{time_str}] {position['option_symbol']} | "
                          f"LTP: ₹{current_price:.2f} | "
                          f"P&L: {pnl_str} | "
                          f"Target: ₹{position['target']:.2f} | "
                          f"SL: ₹{position['stop_loss']:.2f}")
                    
                    # Check exit conditions
                    if current_price >= position['target']:
                        position['status'] = 'TARGET'
                        position['exit_price'] = current_price
                        position['pnl'] = pnl
                        
                        print(f"\n\n" + "="*60)
                        print("🎯 TARGET REACHED!")
                        print(f"Exit Price: ₹{current_price:.2f}")
                        print(f"Profit: ₹{pnl:,.2f} ({pnl_percent:.2f}%)")
                        print("="*60)
                        break
                        
                    elif current_price <= position['stop_loss']:
                        position['status'] = 'STOPLOSS'
                        position['exit_price'] = current_price
                        position['pnl'] = pnl
                        
                        print(f"\n\n" + "="*60)
                        print("🛑 STOP LOSS HIT!")
                        print(f"Exit Price: ₹{current_price:.2f}")
                        print(f"Loss: ₹{pnl:,.2f} ({pnl_percent:.2f}%)")
                        print("="*60)
                        break
                        
                await asyncio.sleep(3)  # Check every 3 seconds
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\nError: {e}")
                await asyncio.sleep(5)

def main():
    print("\n🚀 STARTING PAPER TRADING WITH REAL ZERODHA DATA\n")
    
    try:
        trader = ZerodhaOptionTrading()
        
        # Check if market hours
        now = datetime.now()
        current_time = now.time()
        
        # CRITICAL TIMING: Wait until exactly 9:15:00 to catch real top gainer
        if current_time < datetime.strptime("09:15", "%H:%M").time():
            target_time = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
            wait_seconds = (target_time - now).total_seconds()
            
            print(f"⏰ WAITING FOR MARKET OPEN - 9:15:00 SHARP")
            print(f"   Current time: {current_time.strftime('%H:%M:%S')}")
            print(f"   Will execute in: {wait_seconds:.1f} seconds")
            print(f"   Strategy: Scan + Execute at EXACTLY 9:15:00")
            print(f"   Reason: Top gainer changes at market open!")
            print("\nPress Ctrl+C to cancel")
            
            import time
            # Sleep until exactly 9:15:00
            time.sleep(wait_seconds)
            
            print(f"\n⚡ MARKET OPEN! Executing at {datetime.now().strftime('%H:%M:%S')}")
        
        # If at 9:15, proceed immediately
        elif datetime.strptime("09:15", "%H:%M").time() <= current_time <= datetime.strptime("09:16", "%H:%M").time():
            print("✅ Perfect timing! Market is open - executing NOW...")
        
        # If after 9:16, warn but proceed
        elif current_time > datetime.strptime("09:16", "%H:%M").time():
            print("⚠️  Running after 9:15 AM - may have missed optimal entry")
        
        trader.execute_strategy()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Strategy cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()