#!/usr/bin/env python3
"""
CORRECT 9:15 STRATEGY - Scans ALL NIFTY50 stocks at last second
Finds REAL top gainer in entire NIFTY50, not just 10 stocks
"""

from kiteconnect import KiteConnect
import yaml
from datetime import datetime
import time

class Correct915Strategy:
    def __init__(self):
        print("Initializing FULL NIFTY50 scanner...")
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        # COMPLETE NIFTY50 LIST (ALL 50 STOCKS)
        self.nifty50_stocks = [
            'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 'NSE:ICICIBANK',
            'NSE:KOTAKBANK', 'NSE:SBIN', 'NSE:BHARTIARTL', 'NSE:ITC', 'NSE:AXISBANK',
            'NSE:LT', 'NSE:BAJFINANCE', 'NSE:WIPRO', 'NSE:MARUTI', 'NSE:HCLTECH',
            'NSE:ASIANPAINT', 'NSE:ULTRACEMCO', 'NSE:TITAN', 'NSE:SUNPHARMA', 'NSE:TECHM',
            'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:INDUSINDBK', 'NSE:M&M',
            'NSE:HINDUNILVR', 'NSE:ADANIPORTS', 'NSE:COALINDIA', 'NSE:DIVISLAB', 'NSE:DRREDDY',
            'NSE:UPL', 'NSE:ONGC', 'NSE:JSWSTEEL', 'NSE:GRASIM', 'NSE:BPCL',
            'NSE:CIPLA', 'NSE:EICHERMOT', 'NSE:HEROMOTOCO', 'NSE:BAJAJFINSV', 'NSE:NESTLEIND',
            'NSE:BRITANNIA', 'NSE:TATACONSUM', 'NSE:HINDALCO', 'NSE:SBILIFE', 'NSE:APOLLOHOSP',
            'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT'
        ]
        
        print(f"✅ Connected - Will scan ALL {len(self.nifty50_stocks)} NIFTY50 stocks")
        
    def scan_all_nifty50(self):
        """Scan ALL 50 NIFTY50 stocks at 9:15:00 sharp"""
        print(f"🔍 SCANNING ALL {len(self.nifty50_stocks)} NIFTY50 STOCKS...")
        
        try:
            # Fetch quotes for ALL NIFTY50 stocks
            quotes = self.kite.quote(self.nifty50_stocks)
            
            all_gainers = []
            
            for symbol in self.nifty50_stocks:
                if symbol in quotes:
                    data = quotes[symbol]
                    prev_close = data['ohlc']['close']
                    ltp = data['last_price']
                    
                    if prev_close > 0:
                        change_pct = ((ltp - prev_close) / prev_close) * 100
                        
                        # Include all stocks (gainers and losers)
                        all_gainers.append({
                            'symbol': symbol.split(':')[1],
                            'ltp': ltp,
                            'change': change_pct,
                            'volume': data.get('volume', 0)
                        })
            
            # Sort by percentage change (highest first)
            all_gainers.sort(key=lambda x: x['change'], reverse=True)
            
            print(f"\n📊 TOP 5 NIFTY50 PERFORMERS:")
            print("-" * 50)
            for i, stock in enumerate(all_gainers[:5], 1):
                symbol = "🟢" if stock['change'] > 0 else "🔴"
                print(f"{i}. {stock['symbol']:<12} {stock['change']:+6.2f}% {symbol}")
            
            # Get the #1 performer (could be gainer or least loser)
            if all_gainers:
                top_performer = all_gainers[0]
                
                if top_performer['change'] > 0:
                    print(f"\n🎯 NIFTY50 #1 GAINER: {top_performer['symbol']}")
                else:
                    print(f"\n📉 MARKET IS RED - Best performer: {top_performer['symbol']}")
                
                return top_performer
            
        except Exception as e:
            print(f"❌ Error scanning NIFTY50: {e}")
        
        return None
    
    def execute_at_915(self):
        """Execute at exactly 9:15:00"""
        print(f"\n⚡ EXECUTING AT {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        
        # Scan ALL NIFTY50 at last second
        top_stock = self.scan_all_nifty50()
        
        if top_stock:
            print(f"\n" + "="*60)
            print(f"🎯 REAL-TIME NIFTY50 ANALYSIS COMPLETE")
            print(f"="*60)
            print(f"#1 Stock: {top_stock['symbol']}")
            print(f"Price: ₹{top_stock['ltp']:.2f}")
            print(f"Change: {top_stock['change']:+.2f}%")
            print(f"Volume: {top_stock['volume']:,}")
            
            if top_stock['change'] > 0:
                print(f"Action: BUY {top_stock['symbol']} CALL OPTION")
                print(f"Strategy: Market is bullish")
            else:
                print(f"Action: AVOID TRADING")
                print(f"Strategy: Market is bearish")
            
            print(f"="*60)
            return True
        else:
            print("❌ Could not determine top stock")
            return False

def main():
    print("🎯 CORRECT 9:15 STRATEGY - FULL NIFTY50 SCAN")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Initialize
    strategy = Correct915Strategy()
    
    # Wait for 9:15:00
    now = datetime.now()
    if now.time() < datetime.strptime("09:15", "%H:%M").time():
        target = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
        wait = (target - now).total_seconds()
        
        print(f"\n⏰ Waiting {wait:.0f} seconds to scan ALL NIFTY50 at 9:15:00...")
        print(f"📈 Will find REAL top gainer among all 50 stocks")
        
        # Countdown
        while datetime.now() < target:
            remaining = (target - datetime.now()).total_seconds()
            if remaining <= 10:
                print(f"   {remaining:.1f} seconds... GET READY!", end='\r')
                time.sleep(0.1)
            elif remaining <= 60:
                print(f"   {remaining:.0f} seconds remaining...", end='\r')
                time.sleep(1)
            else:
                time.sleep(10)
        
        print(f"\n🔔 9:15:00 MARKET OPEN!")
    
    # Execute at 9:15:00
    success = strategy.execute_at_915()
    
    if success:
        print(f"\n✅ CORRECT 9:15 STRATEGY COMPLETE!")
    else:
        print(f"\n❌ Strategy failed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()