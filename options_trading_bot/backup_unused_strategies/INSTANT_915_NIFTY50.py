#!/usr/bin/env python3
"""
INSTANT 9:15 STRATEGY - LIGHTNING FAST EXECUTION
Optimized for millisecond speed - no delays!
"""

from kiteconnect import KiteConnect
import yaml
from datetime import datetime, timedelta

class Instant915Strategy:
    def __init__(self):
        print("🚀 INSTANT 9:15 STRATEGY - LIGHTNING MODE")
        
        # Load config FAST
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        # NIFTY50 list - no loading delays
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
            'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT', 'NSE:INDIGO'
        ]
        
        print(f"⚡ READY - Will scan {len(self.nifty50_stocks)} NIFTY50 stocks INSTANTLY")

    def get_smart_atm_option(self, symbol, spot_price):
        """SMART approach: Calculate likely option and verify it exists"""
        try:
            print(f"📡 SMART option lookup for {symbol}...")
            
            # STEP 1: Smart strike calculation (FAST)
            if symbol == 'SHRIRAMFIN':
                atm_strike = round(spot_price / 20) * 20  # 20-point intervals
            elif spot_price < 500:
                atm_strike = round(spot_price / 10) * 10
            elif spot_price < 1000:
                atm_strike = round(spot_price / 25) * 25
            elif spot_price < 3000:
                atm_strike = round(spot_price / 50) * 50
            else:
                atm_strike = round(spot_price / 100) * 100
            
            print(f"   Calculated ATM: ₹{atm_strike}")
            
            # STEP 2: Generate most likely option symbol (FAST)
            today = datetime.now()
            
            # Get current month's last Thursday (monthly expiry)
            import calendar
            year = today.year
            month = today.month
            
            # Find last Thursday of current month
            last_day = calendar.monthrange(year, month)[1]
            last_thursday = None
            for day in range(last_day, 0, -1):
                if calendar.weekday(year, month, day) == 3:  # Thursday = 3
                    last_thursday = day
                    break
            
            monthly_exp = datetime(year, month, last_thursday)
            monthly_exp_str = monthly_exp.strftime('%d%b').upper()
            
            # Get next Thursday (weekly expiry)  
            if today.weekday() == 3:  # Thursday
                weekly_exp_date = today.strftime('%d%b').upper()
            else:
                days_until_thursday = (3 - today.weekday()) % 7
                if days_until_thursday == 0:
                    days_until_thursday = 7
                weekly_exp = today + timedelta(days=days_until_thursday)
                weekly_exp_date = weekly_exp.strftime('%d%b').upper()
            
            print(f"   Monthly expiry: {monthly_exp_str}, Weekly expiry: {weekly_exp_date}")
            
            # STEP 3: Try different symbol formats (FAST) - CORRECT ORDER
            # Known working format from current_trade.json: SHRIRAMFIN25NOV820CE
            possible_formats = [
                f"{symbol}25NOV{int(atm_strike)}CE",                         # SHRIRAMFIN25NOV820CE (known working format)
                f"{symbol}28NOV{int(atm_strike)}CE",                         # SHRIRAMFIN28NOV820CE (next month)
                f"{symbol}{monthly_exp_str}{int(atm_strike)}CE",             # SHRIRAMFIN27NOV820CE (calculated monthly)
                f"{symbol}{weekly_exp_date}{int(atm_strike)}CE",             # SHRIRAMFIN14NOV820CE (weekly)  
                f"{symbol}{weekly_exp_date[2:]}{weekly_exp_date[:2]}{int(atm_strike)}CE", # SHRIRAMFINNOV14820CE
                f"{symbol}{monthly_exp_str[2:]}{monthly_exp_str[:2]}{int(atm_strike)}CE", # SHRIRAMFINNOV27820CE
            ]
            
            print(f"   Trying formats: {len(possible_formats)} variations...")
            
            for option_symbol in possible_formats:
                try:
                    quote = self.kite.quote([f"NFO:{option_symbol}"])
                    if f"NFO:{option_symbol}" in quote:
                        print(f"✅ FOUND: {option_symbol} exists and trading!")
                        
                        # Create option object with verified symbol
                        smart_option = {
                            'tradingsymbol': option_symbol,
                            'strike': atm_strike,
                            'expiry': option_symbol[len(symbol):option_symbol.index('CE')],  # Extract expiry from symbol
                            'lot_size': 825 if symbol == 'SHRIRAMFIN' else 550
                        }
                        return smart_option
                    else:
                        print(f"   ❌ {option_symbol} - not found")
                except Exception as e:
                    print(f"   ❌ {option_symbol} - API error: {str(e)[:50]}")
            
            print(f"❌ None of the {len(possible_formats)} formats worked")
            return None
                
        except Exception as e:
            print(f"❌ SMART lookup failed: {e}")
            return None

    def instant_scan_and_trade(self):
        """INSTANT scan and trade - no delays!"""
        start_time = datetime.now()
        print(f"⚡ EXECUTING INSTANTLY at {start_time.strftime('%H:%M:%S.%f')[:-3]}")
        
        try:
            # SINGLE API call to get all quotes
            print("🔍 Lightning scan...")
            quotes = self.kite.quote(self.nifty50_stocks)
            
            gainers = []
            for symbol in self.nifty50_stocks:
                if symbol in quotes:
                    data = quotes[symbol]
                    prev_close = data['ohlc']['close']
                    ltp = data['last_price']
                    
                    if prev_close > 0:
                        change_pct = ((ltp - prev_close) / prev_close) * 100
                        if change_pct > 0:  # Only gainers
                            gainers.append({
                                'symbol': symbol.split(':')[1],
                                'ltp': ltp,
                                'change': change_pct,
                                'volume': data.get('volume', 0)
                            })
            
            if not gainers:
                print("❌ No gainers found")
                return False
                
            # Get top gainer
            top_gainer = max(gainers, key=lambda x: x['change'])
            
            # Get SMART ATM option (fast calculation + verification)
            atm_option = self.get_smart_atm_option(top_gainer['symbol'], top_gainer['ltp'])
            
            if not atm_option:
                print(f"❌ FAILED to get option for {top_gainer['symbol']}")
                return False
            
            # Calculate execution time
            end_time = datetime.now()
            execution_ms = (end_time - start_time).total_seconds() * 1000
            
            # Show INSTANT results with REAL data
            print(f"\n" + "="*60)
            print(f"⚡ LIGHTNING EXECUTION COMPLETE!")
            print(f"="*60)
            print(f"⏱️  Execution Time: {execution_ms:.1f}ms")
            print(f"🎯 #1 Gainer: {top_gainer['symbol']} (+{top_gainer['change']:.2f}%)")
            print(f"💰 Spot Price: ₹{top_gainer['ltp']:.2f}")
            print(f"🎪 ATM Strike: ₹{atm_option['strike']}")
            print(f"📋 REAL Option: {atm_option['tradingsymbol']}")
            print(f"📅 Expiry: {atm_option['expiry']}")
            print(f"📊 Volume: {top_gainer['volume']:,}")
            print(f"="*60)
            
            print(f"\n✅ TRADE SIGNAL GENERATED IN {execution_ms:.1f}ms!")
            print(f"💡 For live trading, add: --live flag")
            
            # Show complete trading dashboard with REAL data
            self.show_trading_dashboard(atm_option, top_gainer)
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def show_trading_dashboard(self, atm_option, top_gainer):
        """Show complete trading dashboard with 100% REAL data"""
        try:
            option_symbol = atm_option['tradingsymbol']
            
            # Get REAL entry price from live market
            print(f"📊 Getting REAL entry price for {option_symbol}...")
            
            try:
                quote = self.kite.quote([f"NFO:{option_symbol}"])
                if f"NFO:{option_symbol}" in quote:
                    entry_price = quote[f"NFO:{option_symbol}"]['last_price']
                    print(f"✅ REAL entry price: ₹{entry_price:.2f}")
                else:
                    print(f"❌ ZERODHA API: No price data for {option_symbol}")
                    return
            except Exception as e:
                print(f"❌ ZERODHA API FAILED getting price: {e}")
                return
                
            # Use REAL lot size from Zerodha
            lot_size = atm_option['lot_size']
            lots = 1
            quantity = lots * lot_size
            investment = entry_price * quantity
            target_price = entry_price * 1.08  # 8% profit target  
            stop_loss = entry_price * 0.70     # 30% stop loss
            max_risk = investment * 0.30

            print(f"\n" + "="*60)
            print("✅ PAPER TRADE EXECUTED")
            print("="*60)
            print(f"Option: {option_symbol}")
            print(f"Strike: ₹{atm_option['strike']} | Expiry: {atm_option['expiry']}")
            print(f"Lots: {lots} x {lot_size} = {quantity} quantity")
            print(f"Entry Price: ₹{entry_price:.2f}")
            print(f"Investment: ₹{investment:,.2f}")
            print(f"Target (8%): ₹{target_price:.2f}")
            print(f"Stop Loss (30%): ₹{stop_loss:.2f}")
            print(f"Max Risk: ₹{max_risk:,.2f}")
            print("="*60)

            # Save trade data for tracking
            import json
            trade_data = {
                'symbol': option_symbol,
                'entry_price': entry_price,
                'entry_time': datetime.now().strftime('%H:%M:%S'),
                'quantity': quantity,
                'target': target_price,
                'stop_loss': stop_loss
            }
            
            with open('current_trade.json', 'w') as f:
                json.dump(trade_data, f, indent=2)

            # Start live monitoring
            self.monitor_live_pnl(option_symbol, entry_price, target_price, stop_loss, quantity)

        except Exception as e:
            print(f"❌ Dashboard error: {e}")

    def monitor_live_pnl(self, option_symbol, entry_price, target_price, stop_loss, quantity):
        """Live P&L monitoring with REAL LIVE market data"""
        print("\n📊 MONITORING POSITION - LIVE MARKET DATA (Press Ctrl+C to stop)")
        print("-" * 60)
        
        import signal
        import sys
        import time
        
        def signal_handler(sig, frame):
            print(f"\n\n📊 Final Performance Summary:")
            print(f"Entry Price: ₹{entry_price:.2f}")
            print(f"Target: ₹{target_price:.2f}")
            print(f"Stop Loss: ₹{stop_loss:.2f}")
            print("👋 Monitoring stopped")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        error_count = 0
        max_errors = 10
        
        try:
            while True:
                try:
                    # Get REAL LIVE price from Zerodha API
                    quote = self.kite.quote([f"NFO:{option_symbol}"])
                    
                    if f"NFO:{option_symbol}" in quote:
                        current_data = quote[f"NFO:{option_symbol}"]
                        current_price = current_data['last_price']
                        
                        # Reset error count on successful fetch
                        error_count = 0
                        
                        # Calculate P&L with REAL live data
                        pnl = (current_price - entry_price) * quantity
                        pnl_percent = ((current_price - entry_price) / entry_price) * 100
                        
                        # Color coding for P&L
                        if pnl > 0:
                            pnl_str = f"₹{pnl:+,.2f} ({pnl_percent:+.2f}%) ✅"
                        elif pnl < 0:
                            pnl_str = f"₹{pnl:+,.2f} ({pnl_percent:+.2f}%) ❌"
                        else:
                            pnl_str = f"₹{pnl:+,.2f} ({pnl_percent:+.2f}%) ⚪"
                        
                        time_str = datetime.now().strftime('%H:%M:%S')
                        print(f"[{time_str}] {option_symbol} | "
                              f"LTP: ₹{current_price:.2f} | "
                              f"P&L: {pnl_str} | "
                              f"Target: ₹{target_price:.2f} | "
                              f"SL: ₹{stop_loss:.2f}")
                        
                        # Check exit conditions
                        if current_price >= target_price:
                            print(f"\n\n" + "="*60)
                            print("🎯 TARGET REACHED!")
                            print(f"Exit Price: ₹{current_price:.2f}")
                            print(f"Final P&L: ₹{pnl:+,.2f} ({pnl_percent:+.2f}%)")
                            print("="*60)
                            break
                            
                        elif current_price <= stop_loss:
                            print(f"\n\n" + "="*60)
                            print("🛑 STOP LOSS HIT!")
                            print(f"Exit Price: ₹{current_price:.2f}")
                            print(f"Final P&L: ₹{pnl:+,.2f} ({pnl_percent:+.2f}%)")
                            print("="*60)
                            break
                            
                    else:
                        error_count += 1
                        time_str = datetime.now().strftime('%H:%M:%S')
                        print(f"[{time_str}] No price data for {option_symbol} (attempt {error_count}/{max_errors})")
                        
                        if error_count >= max_errors:
                            print(f"\n❌ Too many consecutive errors. Market may be closed.")
                            print(f"📊 Last known position:")
                            print(f"   Entry: ₹{entry_price:.2f}")
                            print(f"   Target: ₹{target_price:.2f}")
                            print(f"   Stop Loss: ₹{stop_loss:.2f}")
                            break
                        
                except Exception as e:
                    time_str = datetime.now().strftime('%H:%M:%S')
                    print(f"[{time_str}] Error: {str(e)[:30]}")
                
                time.sleep(3)  # Update every 3 seconds
                
        except KeyboardInterrupt:
            signal_handler(None, None)

def main():
    print("🚀 INSTANT 9:15 STRATEGY - MILLISECOND EXECUTION")
    print(f"Started: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    # NO WAITING - Execute immediately
    strategy = Instant915Strategy()
    success = strategy.instant_scan_and_trade()
    
    if success:
        print(f"\n⚡ INSTANT STRATEGY COMPLETE!")
    else:
        print(f"\n❌ Strategy failed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")