#!/usr/bin/env python3
"""
PRECISION 9:15 STRATEGY - Ultra-Fast Top Gainer Detection
Scans every 5 seconds for 30 seconds to catch the fastest mover
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import time

class Precision915Strategy:
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
        print("PRECISION 9:15 STRATEGY - RAPID TOP GAINER DETECTION")
        print("=" * 80)
        print(f"Strategy: Scan every 5 seconds for 30 seconds to catch fastest mover")
        print(f"Virtual Capital: ₹{self.capital:,.2f}")
        
        # Load NFO instruments
        print("\nLoading option contracts...")
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
        
    def scan_gainers(self, scan_number):
        """Single scan for top gainers"""
        try:
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
                top_gainer = gainers[0]
                
                time_str = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                print(f"[{time_str}] Scan #{scan_number}: {top_gainer['symbol']} +{top_gainer['change']:.2f}% @ ₹{top_gainer['ltp']:.2f}")
                
                return top_gainer
                
        except Exception as e:
            print(f"Scan #{scan_number} failed: {e}")
            
        return None
        
    def rapid_scan_strategy(self):
        """Execute rapid scanning strategy"""
        print(f"\n⚡ STARTING RAPID SCAN AT {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        scan_results = []
        
        # Scan 6 times over 30 seconds (every 5 seconds)
        for scan_num in range(1, 7):
            start_time = time.time()
            
            top_gainer = self.scan_gainers(scan_num)
            if top_gainer:
                scan_results.append({
                    'scan': scan_num,
                    'time': datetime.now(),
                    'gainer': top_gainer
                })
            
            # Wait exactly 5 seconds between scans
            elapsed = time.time() - start_time
            if scan_num < 6:  # Don't sleep after last scan
                sleep_time = max(0, 5 - elapsed)
                time.sleep(sleep_time)
        
        # Analyze results to find the most consistent top performer
        if scan_results:
            print(f"\n📊 SCAN ANALYSIS COMPLETE")
            print("=" * 60)
            
            # Count appearances of each stock
            stock_appearances = {}
            for result in scan_results:
                symbol = result['gainer']['symbol']
                if symbol not in stock_appearances:
                    stock_appearances[symbol] = []
                stock_appearances[symbol].append(result)
            
            # Find most frequent top gainer
            best_stock = max(stock_appearances.items(), 
                           key=lambda x: len(x[1]))
            
            symbol, appearances = best_stock
            latest_data = appearances[-1]['gainer']  # Most recent data
            
            print(f"🎯 SELECTED STOCK: {symbol}")
            print(f"   Appeared as top gainer: {len(appearances)}/6 scans")
            print(f"   Latest price: ₹{latest_data['ltp']:.2f}")
            print(f"   Latest change: +{latest_data['change']:.2f}%")
            print(f"   Consistency score: {len(appearances)/6*100:.1f}%")
            
            return latest_data
        
        print("❌ No consistent top gainer found")
        return None
        
    def wait_for_market_open(self):
        """Wait until exactly 9:15:00"""
        now = datetime.now()
        current_time = now.time()
        
        if current_time < datetime.strptime("09:15", "%H:%M").time():
            target_time = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
            wait_seconds = (target_time - now).total_seconds()
            
            print(f"⏰ WAITING FOR MARKET OPEN")
            print(f"   Current time: {current_time.strftime('%H:%M:%S')}")
            print(f"   Market opens in: {wait_seconds:.1f} seconds")
            print(f"   Will start rapid scanning at 9:15:00 sharp")
            print("\nPress Ctrl+C to cancel")
            
            time.sleep(wait_seconds)
            print(f"\n🚀 MARKET OPEN! Starting rapid scan...")
            
        elif current_time > datetime.strptime("09:16", "%H:%M").time():
            print("⚠️  Market already open for more than 1 minute")
            print("   May have missed optimal timing")
            
        return True
        
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
        
    def execute_trade(self, top_gainer):
        """Execute the complete trade based on selected stock"""
        print(f"\n🔄 PROCEEDING TO OPTION SELECTION AND EXECUTION")
        print("=" * 60)
        
        # Step 1: Find option contract
        option = self.find_option_contract(top_gainer['symbol'], top_gainer['ltp'])
        
        if option is None:
            print("❌ Could not find suitable option contract")
            return None
            
        # Step 2: Get option price
        option_data = self.get_option_price(option)
        
        if option_data is None:
            print("❌ Could not get option price")
            return None
            
        ltp = option_data['last_price']
        lot_size = option['lot_size']
        
        # Step 3: Calculate position size
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
        
        return position
        
    async def monitor_position(self, position):
        """Monitor the virtual position with live prices"""
        print(f"\n📊 MONITORING VIRTUAL POSITION")
        print("-" * 60)
        
        monitor_count = 0
        while position['status'] == 'OPEN' and monitor_count < 20:  # Monitor for 20 updates
            try:
                # Get live price
                quote = self.kite.quote([position['token']])
                
                if position['token'] in quote:
                    data = quote[position['token']]
                    current_price = data['last_price']
                    
                    # Calculate P&L
                    pnl = (current_price - position['entry_price']) * position['quantity']
                    pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    
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
                          f"P&L: {pnl_str}")
                    
                    # Check exit conditions
                    if current_price >= position['target']:
                        position['status'] = 'TARGET'
                        print(f"\n🎯 VIRTUAL TARGET REACHED!")
                        print(f"Virtual Profit: ₹{pnl:,.2f}")
                        break
                        
                    elif current_price <= position['stop_loss']:
                        position['status'] = 'STOPLOSS'
                        print(f"\n🛑 VIRTUAL STOP LOSS HIT!")
                        print(f"Virtual Loss: ₹{pnl:,.2f}")
                        break
                
                monitor_count += 1
                await asyncio.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
                
        if monitor_count >= 20:
            print(f"\n⏰ Monitoring stopped after 20 updates")

def main():
    print("\n🎯 PRECISION 9:15 STRATEGY - RAPID GAINER DETECTION\n")
    
    try:
        strategy = Precision915Strategy()
        
        # Wait for market open
        if not strategy.wait_for_market_open():
            return
        
        # Execute rapid scanning
        top_gainer = strategy.rapid_scan_strategy()
        
        if top_gainer:
            print(f"\n✅ STRATEGY COMPLETE")
            print(f"   Selected: {top_gainer['symbol']}")
            print(f"   Entry price: ₹{top_gainer['ltp']:.2f}")
            print(f"   Change: +{top_gainer['change']:.2f}%")
            
            # Execute the trade
            position = strategy.execute_trade(top_gainer)
            
            if position:
                print(f"\n🎯 VIRTUAL TRADE EXECUTION SUCCESSFUL!")
                print(f"   Position created for {position['option_symbol']}")
                print(f"   Investment: ₹{position['investment']:,.2f}")
                print(f"   Target: ₹{position['target']:.2f}")
                print(f"   Stop Loss: ₹{position['stop_loss']:.2f}")
                
                # Start monitoring the virtual position
                import asyncio
                print(f"\n🔄 Starting virtual position monitoring...")
                asyncio.run(strategy.monitor_position(position))
            else:
                print(f"\n❌ Trade execution failed")
        else:
            print(f"\n❌ No suitable stock found")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Strategy cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()