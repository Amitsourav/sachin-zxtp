#!/usr/bin/env python3
"""
INSTANT 9:15 TRADER - REAL ORDERS IN MILLISECONDS
Pre-loads everything, executes instantly, places real orders
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor
import threading

class Instant915Trader:
    def __init__(self, live_mode=False):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        self.live_mode = live_mode
        self.capital = self.config['trading']['capital']
        
        print("🚀" * 40)
        if self.live_mode:
            print("⚠️  LIVE TRADING MODE - REAL MONEY!")
        else:
            print("📝 PAPER TRADING MODE")
        print("🚀" * 40)
        
        # Pre-load EVERYTHING at 9:14
        self.pre_market_setup()
        
    def pre_market_setup(self):
        """Pre-load all data at 9:14 for instant execution"""
        print(f"\n⚡ PRE-LOADING at {datetime.now().strftime('%H:%M:%S')}")
        
        # 1. Pre-load NFO instruments
        print("Loading options...")
        self.instruments = pd.DataFrame(self.kite.instruments('NFO'))
        
        # 2. Pre-calculate option chains for likely movers
        self.option_chains = {}
        likely_movers = ['SHRIRAMFIN', 'VEDL', 'BPCL', 'M&M', 'TATASTEEL', 
                        'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'BAJFINANCE']
        
        for stock in likely_movers:
            options = self.instruments[
                (self.instruments['name'] == stock) &
                (self.instruments['instrument_type'] == 'CE') &
                (self.instruments['expiry'] > datetime.now().date())
            ]
            if not options.empty:
                # Get nearest expiry
                nearest_expiry = options['expiry'].min()
                self.option_chains[stock] = options[options['expiry'] == nearest_expiry]
        
        print(f"✅ Pre-loaded {len(self.option_chains)} option chains")
        
        # 3. NIFTY50 list ready
        self.nifty50 = [
            'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 'NSE:ICICIBANK',
            'NSE:KOTAKBANK', 'NSE:SBIN', 'NSE:BHARTIARTL', 'NSE:ITC', 'NSE:AXISBANK',
            'NSE:LT', 'NSE:BAJFINANCE', 'NSE:WIPRO', 'NSE:MARUTI', 'NSE:HCLTECH',
            'NSE:ASIANPAINT', 'NSE:ULTRACEMCO', 'NSE:TITAN', 'NSE:SUNPHARMA', 'NSE:TECHM',
            'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:M&M',
            'NSE:HINDUNILVR', 'NSE:ADANIPORTS', 'NSE:COALINDIA', 'NSE:DIVISLAB', 'NSE:DRREDDY',
            'NSE:UPL', 'NSE:ONGC', 'NSE:JSWSTEEL', 'NSE:GRASIM', 'NSE:BPCL',
            'NSE:CIPLA', 'NSE:EICHERMOT', 'NSE:MAXHEALTH', 'NSE:BAJAJFINSV', 'NSE:NESTLEIND',
            'NSE:BRITANNIA', 'NSE:TATACONSUM', 'NSE:HINDALCO', 'NSE:SBILIFE', 'NSE:APOLLOHOSP',
            'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT'
        ]
        
        # 4. Pre-warm API connection
        try:
            self.kite.quote(['NSE:NIFTY50'])
            print("✅ API connection warmed")
        except:
            pass
    
    def instant_scan_and_execute(self):
        """Complete scan + trade in <300ms"""
        execution_log = []
        start = time.perf_counter()
        
        # PHASE 1: TOP GAINER (Target: <150ms)
        t1 = time.perf_counter()
        
        # Parallel batch fetch
        def fetch_batch(batch):
            try:
                return self.kite.quote(batch)
            except:
                return {}
        
        # Split and fetch in parallel
        batches = [self.nifty50[i:i+10] for i in range(0, len(self.nifty50), 10)]
        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(fetch_batch, batches))
        
        # Merge results
        quotes = {}
        for result in results:
            quotes.update(result)
        
        # Fast calculation
        top_gainer = None
        max_gain = -100
        
        for symbol in self.nifty50:
            if symbol in quotes:
                data = quotes[symbol]
                change = ((data['last_price'] - data['ohlc']['close']) / data['ohlc']['close']) * 100
                if change > max_gain:
                    max_gain = change
                    top_gainer = {
                        'symbol': symbol.split(':')[1],
                        'ltp': data['last_price'],
                        'change': change
                    }
        
        phase1_time = (time.perf_counter() - t1) * 1000
        execution_log.append(f"Scan: {phase1_time:.0f}ms")
        
        if not top_gainer:
            print("❌ No gainer found")
            return
        
        print(f"⚡ {top_gainer['symbol']} (+{top_gainer['change']:.2f}%) in {phase1_time:.0f}ms")
        
        # PHASE 2: OPTION SELECTION (Target: <50ms)
        t2 = time.perf_counter()
        
        # Use pre-loaded option chain
        if top_gainer['symbol'] in self.option_chains:
            options = self.option_chains[top_gainer['symbol']]
            strikes = options['strike'].values
            atm_strike = strikes[abs(strikes - top_gainer['ltp']).argmin()]
            option = options[options['strike'] == atm_strike].iloc[0]
        else:
            # Fallback to real-time
            options = self.instruments[
                (self.instruments['name'] == top_gainer['symbol']) &
                (self.instruments['instrument_type'] == 'CE')
            ]
            if options.empty:
                print("❌ No options")
                return
            expiry = options['expiry'].min()
            options = options[options['expiry'] == expiry]
            strikes = options['strike'].values
            atm_strike = strikes[abs(strikes - top_gainer['ltp']).argmin()]
            option = options[options['strike'] == atm_strike].iloc[0]
        
        phase2_time = (time.perf_counter() - t2) * 1000
        execution_log.append(f"Option: {phase2_time:.0f}ms")
        
        # PHASE 3: PRICE & ORDER (Target: <100ms)
        t3 = time.perf_counter()
        
        # Get option price
        option_quote = self.kite.quote([f"NFO:{option['tradingsymbol']}"])
        option_ltp = option_quote[f"NFO:{option['tradingsymbol']}"]['last_price']
        
        # Calculate order
        lot_size = option['lot_size']
        quantity = lot_size  # 1 lot for speed
        investment = option_ltp * quantity
        
        phase3_time = (time.perf_counter() - t3) * 1000
        execution_log.append(f"Price: {phase3_time:.0f}ms")
        
        # PHASE 4: ORDER PLACEMENT (if live)
        if self.live_mode:
            t4 = time.perf_counter()
            try:
                order_id = self.kite.place_order(
                    variety=self.kite.VARIETY_REGULAR,
                    exchange=self.kite.EXCHANGE_NFO,
                    tradingsymbol=option['tradingsymbol'],
                    transaction_type=self.kite.TRANSACTION_TYPE_BUY,
                    quantity=quantity,
                    product=self.kite.PRODUCT_MIS,
                    order_type=self.kite.ORDER_TYPE_MARKET
                )
                phase4_time = (time.perf_counter() - t4) * 1000
                execution_log.append(f"Order: {phase4_time:.0f}ms")
                print(f"✅ LIVE ORDER: {order_id}")
            except Exception as e:
                print(f"❌ Order failed: {e}")
        
        # TOTAL TIME
        total_time = (time.perf_counter() - start) * 1000
        
        print(f"\n{'='*60}")
        print(f"⚡ EXECUTION COMPLETE IN {total_time:.0f}ms")
        print(f"{'='*60}")
        print(f"Stock: {top_gainer['symbol']} @ ₹{top_gainer['ltp']:.2f}")
        print(f"Option: {option['tradingsymbol']} @ ₹{option_ltp:.2f}")
        print(f"Investment: ₹{investment:,.2f}")
        print(f"Breakdown: {' -> '.join(execution_log)}")
        print(f"{'='*60}")
        
        if total_time < 300:
            print("🏆 WORLD CLASS: Under 300ms!")
        elif total_time < 500:
            print("⚡ EXCELLENT: Under 500ms!")
        elif total_time < 1000:
            print("✅ GOOD: Under 1 second")
        else:
            print("⚠️  SLOW: Need optimization")
        
        return total_time

def main():
    import sys
    
    # Check for live mode
    live_mode = '--live' in sys.argv
    
    if live_mode:
        print("🚨 LIVE TRADING MODE REQUESTED")
        print("This will place REAL orders with REAL money!")
        print("Type 'CONFIRM LIVE' to proceed:")
        if input().strip() != "CONFIRM LIVE":
            print("Cancelled")
            return
    
    print(f"\n⚡ INSTANT 9:15 TRADER")
    print(f"Mode: {'LIVE' if live_mode else 'PAPER'}")
    
    # Initialize trader (pre-loads data)
    trader = Instant915Trader(live_mode=live_mode)
    
    # Wait for 9:15:00.000
    now = datetime.now()
    if now.time() < datetime.strptime("09:15", "%H:%M").time():
        target = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
        wait = (target - now).total_seconds()
        
        print(f"\n⏰ Waiting {wait:.1f}s for 9:15:00...")
        
        # Sleep until 50ms before
        if wait > 0.05:
            time.sleep(wait - 0.05)
        
        # Busy wait for precision
        while datetime.now() < target:
            pass
        
        print(f"🚀 GO! {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    # INSTANT EXECUTION
    execution_time = trader.instant_scan_and_execute()
    
    if execution_time and execution_time < 500:
        print(f"\n🏁 YOU WON THE RACE!")
        print(f"   Your time: {execution_time:.0f}ms")
        print(f"   You're in the top 1% of traders!")

if __name__ == "__main__":
    main()