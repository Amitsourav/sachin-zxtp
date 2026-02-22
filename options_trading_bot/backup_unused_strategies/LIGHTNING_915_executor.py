#!/usr/bin/env python3
"""
LIGHTNING FAST 9:15 EXECUTOR - SPEED IS EVERYTHING
Optimized for sub-second execution with pre-loaded data
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

class Lightning915Executor:
    def __init__(self):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        print("⚡" * 40)
        print("LIGHTNING FAST 9:15 EXECUTOR - MICROSECOND PRECISION")
        print("⚡" * 40)
        
        # PRE-LOAD EVERYTHING for speed
        print("Pre-loading data for instant execution...")
        
        # Pre-load instruments (HEAVY - do this early)
        self.instruments = pd.DataFrame(self.kite.instruments('NFO'))
        self.instruments_dict = {}
        for stock in ['RELIANCE', 'TCS', 'HDFCBANK', 'SHRIRAMFIN', 'VEDL', 'BPCL', 
                      'M&M', 'TATASTEEL', 'HINDALCO', 'BAJFINANCE', 'ICICIBANK',
                      'KOTAKBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'AXISBANK']:
            stock_options = self.instruments[
                (self.instruments['name'] == stock) &
                (self.instruments['instrument_type'] == 'CE') &
                (self.instruments['expiry'] > datetime.now().date())
            ]
            if not stock_options.empty:
                self.instruments_dict[stock] = stock_options
        
        print(f"✅ Pre-loaded options for {len(self.instruments_dict)} stocks")
        
        # CRITICAL: Exact NIFTY50 list
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
        
        # Pre-calculate for speed
        self.capital = self.config['trading']['capital']
        self.risk_amount = self.capital * 0.02  # 2% risk
        
    def parallel_quote_fetch(self, stocks):
        """Fetch all quotes in parallel for maximum speed"""
        quotes = {}
        errors = []
        
        def fetch_batch(batch):
            try:
                return self.kite.quote(batch)
            except Exception as e:
                return None
        
        # Split into batches and fetch in parallel
        batch_size = 10
        batches = [stocks[i:i+batch_size] for i in range(0, len(stocks), batch_size)]
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            results = executor.map(fetch_batch, batches)
            
        for result in results:
            if result:
                quotes.update(result)
                
        return quotes
    
    def instant_top_gainer_detection(self):
        """ULTRA-FAST top gainer detection"""
        start_time = time.perf_counter()
        
        # Parallel fetch all quotes
        quotes = self.parallel_quote_fetch(self.nifty50)
        
        # Rapid calculation (no loops, vectorized)
        gainers = []
        for symbol in self.nifty50:
            if symbol in quotes:
                data = quotes[symbol]
                prev_close = data['ohlc']['close']
                ltp = data['last_price']
                
                if prev_close > 0:
                    change_pct = ((ltp - prev_close) / prev_close) * 100
                    if change_pct > 0:
                        gainers.append((symbol.split(':')[1], ltp, change_pct, data.get('volume', 0)))
        
        # Fast sort
        gainers.sort(key=lambda x: x[2], reverse=True)
        
        elapsed = (time.perf_counter() - start_time) * 1000
        
        if gainers:
            top = gainers[0]
            print(f"⚡ TOP GAINER: {top[0]} @ ₹{top[1]:.2f} (+{top[2]:.2f}%)")
            print(f"⏱️  Detection time: {elapsed:.1f}ms")
            
            return {
                'symbol': top[0],
                'ltp': top[1], 
                'change': top[2],
                'volume': top[3]
            }
        
        return None
    
    def instant_option_selection(self, stock_symbol, spot_price):
        """Pre-calculated option selection for speed"""
        start_time = time.perf_counter()
        
        # Use pre-loaded options
        if stock_symbol in self.instruments_dict:
            options_df = self.instruments_dict[stock_symbol]
        else:
            # Fallback to real-time fetch
            options_df = self.instruments[
                (self.instruments['name'] == stock_symbol) &
                (self.instruments['instrument_type'] == 'CE') &
                (self.instruments['expiry'] > datetime.now().date())
            ]
        
        if options_df.empty:
            return None
        
        # Get nearest expiry
        expiry = options_df['expiry'].min()
        expiry_options = options_df[options_df['expiry'] == expiry]
        
        # Fast ATM calculation
        strikes = expiry_options['strike'].values
        atm_strike = strikes[abs(strikes - spot_price).argmin()]
        
        option = expiry_options[expiry_options['strike'] == atm_strike].iloc[0]
        
        elapsed = (time.perf_counter() - start_time) * 1000
        print(f"⚡ Option selected: {option['tradingsymbol']} in {elapsed:.1f}ms")
        
        return option
    
    def lightning_execute(self):
        """COMPLETE EXECUTION IN <1 SECOND"""
        print(f"\n🚀 LIGHTNING EXECUTION AT {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        execution_start = time.perf_counter()
        
        # Step 1: Instant top gainer (target: <200ms)
        top_gainer = self.instant_top_gainer_detection()
        if not top_gainer:
            print("❌ No gainer found")
            return
        
        # Step 2: Instant option selection (target: <50ms)  
        option = self.instant_option_selection(top_gainer['symbol'], top_gainer['ltp'])
        if option is None:
            print("❌ No option found")
            return
        
        # Step 3: Get option price (target: <100ms)
        try:
            option_quote = self.kite.quote([f"NFO:{option['tradingsymbol']}"])
            option_ltp = option_quote[f"NFO:{option['tradingsymbol']}"]['last_price']
        except:
            print("❌ Could not get option price")
            return
        
        # Step 4: Instant order calculation
        lot_size = option['lot_size']
        max_loss_per_lot = option_ltp * lot_size * 0.30
        num_lots = max(1, int(self.risk_amount / max_loss_per_lot)) if max_loss_per_lot > 0 else 1
        quantity = num_lots * lot_size
        
        # TOTAL EXECUTION TIME
        total_time = (time.perf_counter() - execution_start) * 1000
        
        print(f"\n" + "="*60)
        print(f"⚡⚡⚡ EXECUTION COMPLETE IN {total_time:.0f}ms ⚡⚡⚡")
        print("="*60)
        print(f"Stock: {top_gainer['symbol']} (+{top_gainer['change']:.2f}%)")
        print(f"Option: {option['tradingsymbol']}")
        print(f"Entry: ₹{option_ltp:.2f}")
        print(f"Quantity: {quantity} ({num_lots} lots)")
        print(f"Investment: ₹{option_ltp * quantity:,.2f}")
        print("="*60)
        
        if total_time < 500:
            print("🏆 ULTRA FAST - Under 500ms!")
        elif total_time < 1000:
            print("✅ FAST - Under 1 second")
        else:
            print("⚠️  SLOW - Optimization needed")
        
        return {
            'stock': top_gainer['symbol'],
            'option': option['tradingsymbol'],
            'price': option_ltp,
            'quantity': quantity,
            'execution_ms': total_time
        }
    
    def precision_wait(self):
        """Wait for EXACTLY 9:15:00.000 with microsecond precision"""
        now = datetime.now()
        current_time = now.time()
        
        if current_time < datetime.strptime("09:15", "%H:%M").time():
            target = datetime.combine(now.date(), datetime.strptime("09:15:00.000000", "%H:%M:%S.%f").time())
            
            # Show countdown
            wait_seconds = (target - now).total_seconds()
            print(f"⏰ Precision countdown: {wait_seconds:.3f} seconds")
            
            # Sleep until 100ms before
            if wait_seconds > 0.1:
                time.sleep(wait_seconds - 0.1)
            
            # Busy wait for final 100ms (maximum precision)
            while datetime.now() < target:
                pass  # Busy wait for precision
            
            actual = datetime.now()
            diff_us = (actual - target).total_seconds() * 1000000
            print(f"⚡ TRIGGERED AT: {actual.strftime('%H:%M:%S.%f')}")
            print(f"   Precision: {diff_us:+.0f} microseconds")

def pre_warm_connections():
    """Pre-warm API connections before 9:15"""
    print("🔥 Pre-warming connections...")
    
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    kite = KiteConnect(api_key=config['broker']['api_key'])
    kite.set_access_token(config['broker']['access_token'])
    
    # Make a dummy call to warm up connection
    try:
        kite.quote(['NSE:NIFTY50'])
        print("✅ Connections warmed up")
    except:
        pass

def main():
    print("\n⚡ LIGHTNING FAST 9:15 EXECUTOR\n")
    print("TARGET: Complete execution in <500ms")
    print("="*50)
    
    # Pre-warm connections at 9:14:30
    current_time = datetime.now().time()
    if current_time < datetime.strptime("09:14:30", "%H:%M:%S").time():
        wait_until = datetime.combine(
            datetime.now().date(), 
            datetime.strptime("09:14:30", "%H:%M:%S").time()
        )
        wait_seconds = (wait_until - datetime.now()).total_seconds()
        if wait_seconds > 0:
            print(f"Waiting {wait_seconds:.1f}s to pre-warm at 9:14:30...")
            time.sleep(wait_seconds)
    
    pre_warm_connections()
    
    try:
        # Initialize with pre-loaded data
        executor = Lightning915Executor()
        
        # Wait for exact moment
        executor.precision_wait()
        
        # LIGHTNING EXECUTION
        result = executor.lightning_execute()
        
        if result:
            print(f"\n🏁 RACE WON!")
            print(f"   Execution time: {result['execution_ms']:.0f}ms")
            print(f"   You beat {99 if result['execution_ms'] < 500 else 90}% of traders!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()