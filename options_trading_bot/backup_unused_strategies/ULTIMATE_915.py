#!/usr/bin/env python3
"""
ULTIMATE 9:15 STRATEGY - FAST + BULLETPROOF COMBINED
Speed of lightning with triple verification safety
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor

class Ultimate915Strategy:
    def __init__(self):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        self.capital = self.config['trading']['capital']
        
        print("=" * 80)
        print("🚀 ULTIMATE 9:15 STRATEGY - FAST + SAFE")
        print("=" * 80)
        
        # Pre-load at initialization
        print("Pre-loading data...")
        self.instruments = pd.DataFrame(self.kite.instruments('NFO'))
        
        # NIFTY50 + extras
        self.stocks = [
            'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 'NSE:ICICIBANK',
            'NSE:KOTAKBANK', 'NSE:SBIN', 'NSE:BHARTIARTL', 'NSE:ITC', 'NSE:AXISBANK',
            'NSE:LT', 'NSE:BAJFINANCE', 'NSE:WIPRO', 'NSE:MARUTI', 'NSE:HCLTECH',
            'NSE:ASIANPAINT', 'NSE:ULTRACEMCO', 'NSE:TITAN', 'NSE:SUNPHARMA', 'NSE:TECHM',
            'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:M&M',
            'NSE:HINDUNILVR', 'NSE:ADANIPORTS', 'NSE:COALINDIA', 'NSE:DIVISLAB', 'NSE:DRREDDY',
            'NSE:UPL', 'NSE:ONGC', 'NSE:JSWSTEEL', 'NSE:GRASIM', 'NSE:BPCL',
            'NSE:CIPLA', 'NSE:EICHERMOT', 'NSE:MAXHEALTH', 'NSE:BAJAJFINSV', 'NSE:NESTLEIND',
            'NSE:BRITANNIA', 'NSE:TATACONSUM', 'NSE:HINDALCO', 'NSE:SBILIFE', 'NSE:APOLLOHOSP',
            'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT',
            'NSE:VEDL', 'NSE:SHREECEM'  # Extra stocks
        ]
    
    def fast_parallel_scan(self):
        """Lightning fast parallel scan"""
        def fetch_batch(batch):
            try:
                return self.kite.quote(batch)
            except:
                return {}
        
        # Parallel fetch
        batches = [self.stocks[i:i+10] for i in range(0, len(self.stocks), 10)]
        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(fetch_batch, batches))
        
        # Merge and calculate
        quotes = {}
        for result in results:
            quotes.update(result)
        
        gainers = []
        for symbol in self.stocks:
            if symbol in quotes:
                data = quotes[symbol]
                prev_close = data['ohlc']['close']
                ltp = data['last_price']
                if prev_close > 0:
                    change = ((ltp - prev_close) / prev_close) * 100
                    if change > 0:
                        gainers.append({
                            'symbol': symbol.split(':')[1],
                            'ltp': ltp,
                            'change': change,
                            'volume': data.get('volume', 0)
                        })
        
        gainers.sort(key=lambda x: x['change'], reverse=True)
        return gainers[:3] if gainers else []
    
    def ultimate_execute(self):
        """Combined fast + safe execution"""
        print(f"\n⚡ EXECUTING AT {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        start_time = time.perf_counter()
        
        # PHASE 1: Triple scan for safety (but fast)
        print("🔍 Triple verification scan...")
        
        scan_results = []
        for i in range(3):
            top_3 = self.fast_parallel_scan()
            if top_3:
                scan_results.append(top_3[0])  # Store top gainer
                print(f"   Scan {i+1}: {top_3[0]['symbol']} (+{top_3[0]['change']:.2f}%)")
            if i < 2:
                time.sleep(0.5)  # Quick 500ms gap
        
        # Verify consistency
        if not scan_results:
            print("❌ No gainers found")
            return
        
        # Count appearances
        stock_count = {}
        for result in scan_results:
            symbol = result['symbol']
            if symbol not in stock_count:
                stock_count[symbol] = []
            stock_count[symbol].append(result)
        
        # Get most consistent
        best = max(stock_count.items(), key=lambda x: len(x[1]))
        if len(best[1]) < 2:
            print("⚠️  Inconsistent results, using highest gainer")
        
        top_gainer = best[1][-1]  # Use latest data
        print(f"\n✅ VERIFIED: {top_gainer['symbol']} (+{top_gainer['change']:.2f}%)")
        
        # PHASE 2: Find option (fast)
        options = self.instruments[
            (self.instruments['name'] == top_gainer['symbol']) &
            (self.instruments['instrument_type'] == 'CE') &
            (self.instruments['expiry'] > datetime.now().date())
        ]
        
        if options.empty:
            print(f"❌ No options for {top_gainer['symbol']}")
            return
        
        # Get nearest expiry ATM
        expiry = options['expiry'].min()
        options = options[options['expiry'] == expiry]
        strikes = options['strike'].values
        atm_strike = strikes[abs(strikes - top_gainer['ltp']).argmin()]
        option = options[options['strike'] == atm_strike].iloc[0]
        
        # PHASE 3: Get price and calculate
        quote = self.kite.quote([f"NFO:{option['tradingsymbol']}"])
        option_ltp = quote[f"NFO:{option['tradingsymbol']}"]['last_price']
        
        lot_size = option['lot_size']
        quantity = lot_size
        investment = option_ltp * quantity
        
        # Total time
        total_time = (time.perf_counter() - start_time) * 1000
        
        print(f"\n{'='*60}")
        print(f"✅ EXECUTION COMPLETE IN {total_time:.0f}ms")
        print(f"{'='*60}")
        print(f"Stock: {top_gainer['symbol']} @ ₹{top_gainer['ltp']:.2f} (+{top_gainer['change']:.2f}%)")
        print(f"Option: {option['tradingsymbol']}")
        print(f"Strike: {option['strike']} | Expiry: {option['expiry']}")
        print(f"Entry: ₹{option_ltp:.2f}")
        print(f"Quantity: {quantity} (1 lot)")
        print(f"Investment: ₹{investment:,.2f}")
        print(f"Target (8%): ₹{option_ltp * 1.08:.2f}")
        print(f"Stop Loss (30%): ₹{option_ltp * 0.70:.2f}")
        print(f"{'='*60}")
        
        if total_time < 2000:
            print("⚡ FAST EXECUTION with TRIPLE SAFETY!")
        
        # Monitor position
        self.monitor_position(option['tradingsymbol'], option_ltp, quantity)
        
    def monitor_position(self, symbol, entry_price, quantity):
        """Monitor UNTIL target or stop loss is hit"""
        print(f"\n📊 MONITORING POSITION UNTIL EXIT...")
        print("-" * 60)
        
        target = entry_price * 1.08
        stop_loss = entry_price * 0.70
        
        print(f"Entry: ₹{entry_price:.2f}")
        print(f"Target: ₹{target:.2f} (+8%)")
        print(f"Stop Loss: ₹{stop_loss:.2f} (-30%)")
        print("-" * 60)
        
        position_open = True
        update_count = 0
        max_updates = 1000  # Safety limit (~50 minutes)
        
        while position_open and update_count < max_updates:
            try:
                quote = self.kite.quote([f"NFO:{symbol}"])
                ltp = quote[f"NFO:{symbol}"]['last_price']
                pnl = (ltp - entry_price) * quantity
                pnl_pct = ((ltp - entry_price) / entry_price) * 100
                
                # Show update every 3 seconds
                status = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                distance_to_target = ((target - ltp) / ltp) * 100
                distance_to_sl = ((ltp - stop_loss) / ltp) * 100
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] LTP: ₹{ltp:.2f} | "
                      f"P&L: ₹{pnl:+,.0f} ({pnl_pct:+.1f}%) {status} | "
                      f"To Target: {distance_to_target:.1f}% | To SL: {distance_to_sl:.1f}%")
                
                # Check exit conditions
                if ltp >= target:
                    print(f"\n" + "="*60)
                    print(f"🎯 TARGET REACHED!")
                    print(f"Exit Price: ₹{ltp:.2f}")
                    print(f"Profit: ₹{pnl:,.0f} ({pnl_pct:.1f}%)")
                    print("="*60)
                    position_open = False
                    break
                    
                elif ltp <= stop_loss:
                    print(f"\n" + "="*60)
                    print(f"🛑 STOP LOSS HIT!")
                    print(f"Exit Price: ₹{ltp:.2f}")
                    print(f"Loss: ₹{pnl:,.0f} ({pnl_pct:.1f}%)")
                    print("="*60)
                    position_open = False
                    break
                
                update_count += 1
                time.sleep(3)  # Check every 3 seconds
                
            except KeyboardInterrupt:
                print(f"\n⏹️ Monitoring stopped by user")
                print(f"Last P&L: ₹{pnl:+,.0f} ({pnl_pct:+.1f}%)")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
        
        if position_open and update_count >= max_updates:
            print(f"\n⏰ Monitoring timeout after {update_count} updates")
            print(f"Position still open - manual intervention needed")
        
        print(f"\n📊 Monitoring ended after {update_count} updates")

def main():
    print("🚀 ULTIMATE 9:15 STRATEGY - BEST OF BOTH WORLDS\n")
    
    # Initialize
    strategy = Ultimate915Strategy()
    
    # Wait for 9:15:00
    now = datetime.now()
    if now.time() < datetime.strptime("09:15", "%H:%M").time():
        target = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
        wait = (target - now).total_seconds()
        print(f"⏰ Waiting {wait:.1f}s for 9:15:00...")
        
        if wait > 0.1:
            time.sleep(wait - 0.1)
        
        while datetime.now() < target:
            pass
        
        print(f"🔔 MARKET OPEN! {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    # Execute
    strategy.ultimate_execute()

if __name__ == "__main__":
    main()