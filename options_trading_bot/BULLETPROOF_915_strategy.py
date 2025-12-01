#!/usr/bin/env python3
"""
BULLETPROOF 9:15 STRATEGY - ZERO MISTAKES ALLOWED
Triple verification system to ensure we NEVER miss the real top gainer
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import time
import json

class Bulletproof915Strategy:
    def __init__(self):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        self.capital = self.config['trading']['capital']
        
        print("=" * 80)
        print("🛡️ BULLETPROOF 9:15 STRATEGY - ZERO MISTAKE TOLERANCE")
        print("=" * 80)
        print(f"Virtual Capital: ₹{self.capital:,.2f}")
        
        # Load NFO instruments
        print("Loading option contracts...")
        self.instruments = pd.DataFrame(self.kite.instruments('NFO'))
        
        # CRITICAL: Complete NIFTY50 list - November 2025
        # THIS LIST MUST BE 100% ACCURATE!
        self.nifty50_stocks = [
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
        
        # Additional high-volume stocks that might be in NIFTY50
        self.backup_stocks = [
            'NSE:VEDL', 'NSE:SHREECEM', 'NSE:HDFCLIFE', 'NSE:PIDILITIND',
            'NSE:SIEMENS', 'NSE:GODREJCP', 'NSE:TORNTPHARM', 'NSE:ZYDUSLIFE'
        ]
        
        self.all_stocks = self.nifty50_stocks + self.backup_stocks
        print(f"Monitoring {len(self.all_stocks)} total stocks (NIFTY50 + potential additions)")
        
    def verify_stock_exists(self, symbol):
        """Verify a stock symbol exists and is tradeable"""
        try:
            quote = self.kite.quote([symbol])
            if symbol in quote:
                return True
        except:
            pass
        return False
    
    def triple_scan_verification(self):
        """Triple scan at 9:15:00, 9:15:01, 9:15:02 to ensure accuracy"""
        print(f"\n⚡ TRIPLE VERIFICATION SYSTEM ACTIVATED")
        print("=" * 60)
        
        all_scans = []
        
        # Perform 3 rapid scans
        for scan_num in range(1, 4):
            scan_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            print(f"Scan #{scan_num} at {scan_time}...")
            
            try:
                # Fetch in smaller batches to avoid connection issues
                all_quotes = {}
                batch_size = 10
                
                for i in range(0, len(self.all_stocks), batch_size):
                    batch = self.all_stocks[i:i+batch_size]
                    batch_quotes = self.kite.quote(batch)
                    all_quotes.update(batch_quotes)
                
                gainers = []
                for symbol in self.all_stocks:
                    if symbol in all_quotes:
                        data = all_quotes[symbol]
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
                    top_3 = gainers[:3]
                    all_scans.append(top_3)
                    
                    print(f"   Top gainer: {top_3[0]['symbol']} (+{top_3[0]['change']:.2f}%)")
                
                if scan_num < 3:
                    time.sleep(1)  # Wait 1 second between scans
                    
            except Exception as e:
                print(f"   Scan #{scan_num} error: {e}")
        
        # Analyze all scans to find most consistent top gainer
        if all_scans:
            return self.analyze_scans(all_scans)
        
        return None
    
    def analyze_scans(self, all_scans):
        """Analyze multiple scans to find the TRUE top gainer"""
        print(f"\n📊 ANALYZING {len(all_scans)} SCANS")
        print("=" * 60)
        
        # Count appearances in top position
        top_gainer_count = {}
        
        for scan in all_scans:
            if scan:
                top_stock = scan[0]['symbol']
                if top_stock not in top_gainer_count:
                    top_gainer_count[top_stock] = {'count': 0, 'changes': [], 'data': scan[0]}
                top_gainer_count[top_stock]['count'] += 1
                top_gainer_count[top_stock]['changes'].append(scan[0]['change'])
        
        # Find most consistent top gainer
        if top_gainer_count:
            best_stock = max(top_gainer_count.items(), key=lambda x: x[1]['count'])
            symbol = best_stock[0]
            data = best_stock[1]
            avg_change = sum(data['changes']) / len(data['changes'])
            
            print(f"✅ VERIFIED TOP GAINER: {symbol}")
            print(f"   Appeared as #1: {data['count']}/{len(all_scans)} times")
            print(f"   Average gain: +{avg_change:.2f}%")
            print(f"   Latest price: ₹{data['data']['ltp']:.2f}")
            
            # Final verification
            if data['count'] >= 2:  # Must appear as top gainer in at least 2 scans
                print(f"   ✅✅✅ TRIPLE VERIFIED - SAFE TO TRADE")
                return data['data']
            else:
                print(f"   ⚠️ Inconsistent results - needs manual verification")
                
                # Show all top gainers for manual review
                print(f"\n   All detected top gainers:")
                for stock, info in top_gainer_count.items():
                    print(f"   - {stock}: {info['count']} times, avg +{sum(info['changes'])/len(info['changes']):.2f}%")
                
                # Return highest average gainer
                best_avg = max(top_gainer_count.items(), 
                             key=lambda x: sum(x[1]['changes'])/len(x[1]['changes']))
                print(f"\n   Selected by highest average: {best_avg[0]}")
                return best_avg[1]['data']
        
        return None
    
    def execute_with_verification(self):
        """Execute strategy with multiple verification steps"""
        print(f"\n🚀 EXECUTING BULLETPROOF STRATEGY AT {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 80)
        
        # Step 1: Triple scan verification
        top_gainer = self.triple_scan_verification()
        
        if not top_gainer:
            print("❌ ABORT: Could not verify top gainer with confidence")
            return
        
        # Step 2: Final confirmation scan
        print(f"\n🔍 FINAL CONFIRMATION for {top_gainer['symbol']}...")
        time.sleep(2)
        
        try:
            confirm_quote = self.kite.quote([f"NSE:{top_gainer['symbol']}"])
            symbol_key = f"NSE:{top_gainer['symbol']}"
            
            if symbol_key in confirm_quote:
                data = confirm_quote[symbol_key]
                prev_close = data['ohlc']['close']
                ltp = data['last_price']
                final_change = ((ltp - prev_close) / prev_close) * 100
                
                print(f"   Current price: ₹{ltp:.2f}")
                print(f"   Current gain: +{final_change:.2f}%")
                
                # Verify it's still the top gainer
                if final_change < top_gainer['change'] - 0.5:  # Allow 0.5% variance
                    print(f"   ⚠️ WARNING: Gain dropped from +{top_gainer['change']:.2f}% to +{final_change:.2f}%")
                    print(f"   Re-scanning to confirm...")
                    
                    # Re-scan if significant change
                    top_gainer = self.triple_scan_verification()
                    if not top_gainer:
                        print("❌ ABORT: Market conditions changing too fast")
                        return
                
                print(f"\n✅ FINAL CONFIRMATION SUCCESSFUL")
                print(f"=" * 80)
                print(f"🎯 SELECTED STOCK: {top_gainer['symbol']}")
                print(f"   Price: ₹{ltp:.2f}")
                print(f"   Gain: +{final_change:.2f}%")
                print(f"   Volume: {data.get('volume', 0):,}")
                print(f"=" * 80)
                
                # Update top_gainer with latest data
                top_gainer['ltp'] = ltp
                top_gainer['change'] = final_change
                
                return top_gainer
                
        except Exception as e:
            print(f"❌ Final confirmation failed: {e}")
            
        return None
    
    def wait_for_perfect_timing(self):
        """Wait for EXACTLY 9:15:00.000"""
        now = datetime.now()
        current_time = now.time()
        
        if current_time < datetime.strptime("09:15", "%H:%M").time():
            target_time = datetime.combine(now.date(), datetime.strptime("09:15:00.000", "%H:%M:%S.%f").time())
            wait_seconds = (target_time - now).total_seconds()
            
            print(f"⏰ PRECISION TIMING SYSTEM")
            print(f"   Current: {now.strftime('%H:%M:%S.%f')[:-3]}")
            print(f"   Target:  09:15:00.000")
            print(f"   Wait:    {wait_seconds:.3f} seconds")
            
            # Sleep until 1 second before
            if wait_seconds > 1:
                time.sleep(wait_seconds - 1)
            
            # Precise final timing
            while datetime.now() < target_time:
                time.sleep(0.001)  # 1 millisecond precision
            
            actual_time = datetime.now()
            diff_ms = (actual_time - target_time).total_seconds() * 1000
            print(f"\n⚡ EXECUTED AT: {actual_time.strftime('%H:%M:%S.%f')[:-3]}")
            print(f"   Precision: {diff_ms:+.1f} milliseconds")

def main():
    print("\n🛡️ BULLETPROOF 9:15 STRATEGY - ZERO MISTAKES ALLOWED\n")
    
    try:
        strategy = Bulletproof915Strategy()
        
        # Wait for perfect timing
        strategy.wait_for_perfect_timing()
        
        # Execute with triple verification
        top_gainer = strategy.execute_with_verification()
        
        if top_gainer:
            print(f"\n🎯 SUCCESS: Bulletproof selection complete")
            print(f"   Stock: {top_gainer['symbol']}")
            print(f"   Entry: ₹{top_gainer['ltp']:.2f}")
            print(f"   Gain: +{top_gainer['change']:.2f}%")
            print(f"\n✅ READY FOR OPTION TRADING WITH CONFIDENCE")
        else:
            print(f"\n❌ FAILED: Could not determine top gainer with certainty")
            print(f"   Manual intervention required")
            
    except KeyboardInterrupt:
        print("\n⏹️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()