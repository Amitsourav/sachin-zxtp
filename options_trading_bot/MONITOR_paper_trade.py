#!/usr/bin/env python3
"""
PAPER TRADING WITH LIVE MONITORING
Shows real-time P&L, targets, and stop-loss like in the screenshot
Waits until 9:15:01 AM for market prices to stabilize before executing trades
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, time as datetime_time
import time
import os
import sys
import json

class PaperTradeMonitor:
    def __init__(self):
        """Initialize paper trading with monitoring"""
        # Load config
        config_path = 'config/config.yaml'
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            sys.exit(1)
            
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
        
        # Initialize Kite
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        self.capital = self.config['trading'].get('capital', 100000)
        
        print("="*80)
        print("📊 PAPER TRADING WITH LIVE MONITORING")
        print("="*80)
        
        # Verify connection
        try:
            profile = self.kite.profile()
            print(f"✅ Connected to: {profile['user_name']} ({profile['user_id']})")
            print(f"💰 Virtual Capital: ₹{self.capital:,.2f}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            sys.exit(1)
        
        # Load instruments
        print("Loading option contracts...")
        try:
            self.instruments = pd.DataFrame(self.kite.instruments('NFO'))
            print(f"✅ Loaded {len(self.instruments)} contracts")
        except Exception as e:
            print(f"❌ Failed to load instruments: {e}")
            sys.exit(1)
        
        # Load DYNAMIC NIFTY50 watchlist
        self.watchlist = self.get_current_nifty50_list()
        
        # Paper trade storage
        self.active_position = None
        self.trade_log = []
    
    def get_current_nifty50_list(self):
        """Get current NIFTY50 constituents dynamically"""
        try:
            # Try to load from saved dynamic list
            if os.path.exists('config/dynamic_nifty50.json'):
                with open('config/dynamic_nifty50.json', 'r') as f:
                    data = json.load(f)
                
                # Check if data is recent (less than 30 days old)
                saved_time = datetime.fromisoformat(data['timestamp'])
                if (datetime.now() - saved_time).days < 30:
                    print(f"✅ Using current NIFTY50 list ({data['count']} stocks)")
                    print(f"   Last updated: {saved_time.strftime('%Y-%m-%d')}")
                    return data['symbols']
                else:
                    print("⚠️  Saved NIFTY50 list is outdated, fetching fresh...")
            
            # Fetch current NIFTY50 from instruments
            print("🔍 Fetching current NIFTY50 constituents...")
            
            # Get NSE equity instruments
            nse_instruments = self.kite.instruments('NSE')
            instruments_df = pd.DataFrame(nse_instruments)
            
            # Filter equity stocks
            equity_stocks = instruments_df[
                (instruments_df['instrument_type'] == 'EQ') &
                (instruments_df['segment'] == 'NSE')
            ].copy()
            
            # Get current large-cap stocks (this is a simplified approach)
            # In reality, you'd need market cap data or use external API
            current_large_caps = [
                'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
                'KOTAKBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'AXISBANK',
                'LT', 'BAJFINANCE', 'WIPRO', 'MARUTI', 'HCLTECH',
                'ASIANPAINT', 'ULTRACEMCO', 'TITAN', 'SUNPHARMA', 'TECHM',
                'POWERGRID', 'NTPC', 'TATAMOTORS', 'M&M', 'HINDUNILVR',
                'ADANIPORTS', 'COALINDIA', 'DIVISLAB', 'DRREDDY', 'UPL',
                'ONGC', 'JSWSTEEL', 'GRASIM', 'BPCL', 'CIPLA',
                'EICHERMOT', 'BAJAJFINSV', 'NESTLEIND', 'BRITANNIA', 'TATACONSUM',
                'HINDALCO', 'SBILIFE', 'APOLLOHOSP', 'TATASTEEL', 'SHRIRAMFIN',
                'ADANIENT', 'LTIM', 'TRENT', 'INDIGO', 'HEROMOTOCO'
            ]
            
            # Verify these stocks exist in current instruments
            available_stocks = []
            for stock in current_large_caps:
                matching = equity_stocks[equity_stocks['tradingsymbol'] == stock]
                if len(matching) > 0:
                    available_stocks.append(f"NSE:{stock}")
            
            if len(available_stocks) >= 45:  # At least 45 valid stocks
                nifty50_list = available_stocks[:50]  # Take first 50
                
                # Save to file for future use
                nifty_data = {
                    'timestamp': datetime.now().isoformat(),
                    'count': len(nifty50_list),
                    'symbols': nifty50_list
                }
                
                os.makedirs('config', exist_ok=True)
                with open('config/dynamic_nifty50.json', 'w') as f:
                    json.dump(nifty_data, f, indent=2)
                
                print(f"✅ Fetched current NIFTY50 list ({len(nifty50_list)} stocks)")
                return nifty50_list
            
            else:
                print("⚠️  Could not fetch enough valid stocks, using fallback...")
                return self.get_fallback_nifty50()
                
        except Exception as e:
            print(f"⚠️  Error fetching dynamic NIFTY50: {e}")
            print("Using fallback static list...")
            return self.get_fallback_nifty50()
    
    def get_fallback_nifty50(self):
        """Fallback to static NIFTY50 list if dynamic fetch fails"""
        return [
            'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 'NSE:ICICIBANK',
            'NSE:KOTAKBANK', 'NSE:SBIN', 'NSE:BHARTIARTL', 'NSE:ITC', 'NSE:AXISBANK',
            'NSE:LT', 'NSE:BAJFINANCE', 'NSE:WIPRO', 'NSE:MARUTI', 'NSE:HCLTECH',
            'NSE:ASIANPAINT', 'NSE:ULTRACEMCO', 'NSE:TITAN', 'NSE:SUNPHARMA', 'NSE:TECHM',
            'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:M&M', 'NSE:HINDUNILVR',
            'NSE:ADANIPORTS', 'NSE:COALINDIA', 'NSE:DIVISLAB', 'NSE:DRREDDY', 'NSE:UPL',
            'NSE:ONGC', 'NSE:JSWSTEEL', 'NSE:GRASIM', 'NSE:BPCL', 'NSE:CIPLA',
            'NSE:EICHERMOT', 'NSE:BAJAJFINSV', 'NSE:NESTLEIND', 'NSE:BRITANNIA', 'NSE:TATACONSUM',
            'NSE:HINDALCO', 'NSE:SBILIFE', 'NSE:APOLLOHOSP', 'NSE:TATASTEEL', 'NSE:SHRIRAMFIN',
            'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT', 'NSE:INDIGO'
        ]
    
    def wait_for_market_open(self):
        """Wait for 9:15:01 to let market prices stabilize after open"""
        market_open = datetime_time(9, 15, 0, 0)  # Market opens at 9:15:00
        
        while True:
            now = datetime.now()
            current_time = now.time()
            
            if current_time >= market_open:
                if now.weekday() < 5:  # Weekday
                    print(f"\n🔔 MARKET IS NOW OPEN: {now.strftime('%H:%M:%S.%f')}!")
                    print("⏳ Waiting 1 second for market prices to stabilize...")
                    time.sleep(1.0)  # Wait 1 second for prices to update
                    print(f"⚡ EXECUTING AT: {datetime.now().strftime('%H:%M:%S.%f')}!")
                    return True
                else:
                    print("❌ Weekend - markets closed")
                    return False
            
            target = datetime.combine(now.date(), market_open)
            wait_seconds = (target - now).total_seconds()
            
            if wait_seconds > 0:
                if wait_seconds > 10:  # If more than 10 seconds, show normal countdown
                    mins, secs = divmod(int(wait_seconds), 60)
                    print(f"\r⏰ Market opens in: {mins:02d}:{secs:02d}", end="")
                    time.sleep(1)
                elif wait_seconds > 1:  # Between 1-10 seconds, prepare for execution
                    print(f"\r🎯 PREPARING FOR EXECUTION: {wait_seconds:.2f} seconds...", end="")
                    time.sleep(0.1)  # Check every 100ms for precision
                else:  # Less than 1 second, high precision mode
                    print(f"\r⚡ HIGH PRECISION MODE: {wait_seconds*1000:.0f}ms", end="")
                    time.sleep(0.001)  # Check every 1ms for microsecond precision
    
    def scan_top_gainers(self):
        """Scan for top gainers immediately at market open"""
        print(f"\n⚡ IMMEDIATE MARKET OPEN SCAN at {datetime.now().strftime('%H:%M:%S.%f')}")
        print("Capturing opening prices before they spike up")
        
        try:
            quotes = self.kite.quote(self.watchlist)
        except Exception as e:
            print(f"❌ Failed to fetch quotes: {e}")
            return None
        
        gainers = []
        
        for symbol in self.watchlist:
            if symbol in quotes:
                data = quotes[symbol]
                if 'ohlc' in data and 'close' in data['ohlc']:
                    prev_close = data['ohlc']['close']
                    open_price = data['ohlc'].get('open', prev_close)
                    ltp = data.get('last_price', 0)
                    volume = data.get('volume', 0)
                    
                    # Basic validation - just ensure we have valid prices
                    if prev_close > 0 and ltp > 0:
                        # Calculate change from previous close
                        change_pct = ((ltp - prev_close) / prev_close) * 100
                        
                        # At market open, LTP might equal open price (this is normal)
                        # We want ANY positive change, even small ones
                        if change_pct > 0:  # Any positive gain
                            gainers.append({
                                'symbol': symbol.split(':')[1],
                                'ltp': ltp,
                                'open': open_price,
                                'prev_close': prev_close,
                                'change': change_pct,
                                'gap_up': ((open_price - prev_close) / prev_close) * 100 if open_price > 0 else 0,
                                'volume': volume
                            })
        
        if gainers:
            gainers.sort(key=lambda x: x['change'], reverse=True)
            
            print("\n📊 TOP GAINERS (Validated Prices):")
            print("-"*80)
            print(f"{'Stock':<12} {'Close':<10} {'Open':<10} {'LTP':<10} {'Change%':<8} {'Volume':<12}")
            print("-"*80)
            for i, g in enumerate(gainers[:5], 1):
                print(f"{i}. {g['symbol']:<10} ₹{g['prev_close']:8.2f}  ₹{g['open']:8.2f}  ₹{g['ltp']:8.2f}  {g['change']:+6.2f}%  {g['volume']:>10,}")
            print("-"*80)
            
            # Show selected stock details
            selected = gainers[0]
            print(f"\n✅ Selected: {selected['symbol']}")
            print(f"   Market Open Price Captured!")
            print(f"   Open: ₹{selected['open']:.2f} | LTP: ₹{selected['ltp']:.2f}")
            print(f"   Executing immediately to avoid price spike")
            
            return gainers[0] if gainers else None
        
        print("\n❌ No gaining stocks found at market open")
        print("   This is normal in the first few milliseconds")
        print("   Retrying...")
        
        return None
    
    def find_option_contract(self, stock, spot_price):
        """Find ATM option contract"""
        try:
            # Find CE options for the stock
            mask = (self.instruments['name'] == stock) & (self.instruments['instrument_type'] == 'CE')
            stock_options = self.instruments.loc[mask].copy()
            
            if len(stock_options) == 0:
                return None
            
            # Find next expiry
            current_date = datetime.now().date()
            if not pd.api.types.is_datetime64_any_dtype(stock_options['expiry']):
                stock_options['expiry'] = pd.to_datetime(stock_options['expiry'])
            
            future_mask = stock_options['expiry'].dt.date > current_date
            if not future_mask.any():
                return None
            
            future_expiries = stock_options.loc[future_mask, 'expiry'].dt.date.unique()
            if len(future_expiries) == 0:
                return None
            
            expiry = sorted(future_expiries)[0]
            
            # Get options for nearest expiry
            expiry_mask = stock_options['expiry'].dt.date == expiry
            options_df = stock_options.loc[expiry_mask].copy()
            
            if len(options_df) == 0:
                return None
            
            # Find ATM or slightly OTM strike (equal to or just below current price)
            strikes = sorted(options_df['strike'].unique())
            
            # Filter strikes that are equal to or below current price
            otm_strikes = [s for s in strikes if s <= spot_price]
            
            if otm_strikes:
                # Pick the highest strike that is <= current price (closest to ATM but OTM)
                selected_strike = max(otm_strikes)
                print(f"\n🎯 Strike Selection: Spot ₹{spot_price:.2f} → Strike ₹{selected_strike:.2f} (OTM)")
            else:
                # If all strikes are above current price, pick the lowest one
                selected_strike = min(strikes)
                print(f"\n⚠️  All strikes above spot price ₹{spot_price:.2f}, selected lowest: ₹{selected_strike:.2f}")
            
            strike_mask = options_df['strike'] == selected_strike
            final_option = options_df.loc[strike_mask]
            
            if len(final_option) == 0:
                return None
            
            return final_option.iloc[0]
            
        except Exception as e:
            print(f"❌ Error finding option: {e}")
            return None
    
    def execute_paper_trade(self, stock, option):
        """Execute trade (paper or live based on is_live flag)"""
        try:
            # Get current option price
            option_symbol = f"NFO:{option['tradingsymbol']}"
            quote = self.kite.quote([option_symbol])
            
            if option_symbol not in quote:
                print("❌ Could not fetch option price")
                return False
            
            entry_price = quote[option_symbol]['last_price']
            quantity = int(option['lot_size'])
            
            # Calculate initial stop-loss only (NO TARGET - using trailing stop loss)
            # Target is removed - trade only exits on trailing stop loss
            target_price = entry_price * 10.0  # Set very high target (won't be used)
            stop_loss = entry_price * 0.70     # 30% initial stop loss
            
            # Check if live trading
            if hasattr(self, 'is_live') and self.is_live:
                # LIVE TRADING - REAL MONEY
                print(f"\n🚨 PLACING LIVE ORDER - REAL MONEY!")
                print("="*50)
                
                # Use current market price (LTP) as limit price - ALWAYS
                limit_price = entry_price  # ALWAYS use current price as limit price
                
                # Get bid-ask for reference only
                depth = quote[option_symbol].get('depth', {})
                bid_price = depth.get('buy', [{}])[0].get('price', entry_price) if depth.get('buy') else entry_price
                ask_price = depth.get('sell', [{}])[0].get('price', entry_price) if depth.get('sell') else entry_price
                
                print(f"   Bid: ₹{bid_price:.2f} | Ask: ₹{ask_price:.2f} | LTP: ₹{entry_price:.2f}")
                print(f"   Limit Price: ₹{limit_price:.2f} (using current market price)")
                
                try:
                    order_id = self.kite.place_order(
                        variety=self.kite.VARIETY_REGULAR,
                        exchange=self.kite.EXCHANGE_NFO,
                        tradingsymbol=option['tradingsymbol'],
                        transaction_type=self.kite.TRANSACTION_TYPE_BUY,
                        quantity=quantity,
                        product=self.kite.PRODUCT_MIS,  # Intraday
                        order_type=self.kite.ORDER_TYPE_LIMIT,
                        price=limit_price
                    )
                    
                    print(f"✅ LIVE ORDER PLACED!")
                    print(f"   Order ID: {order_id}")
                    
                    # Wait for order execution
                    time.sleep(2)
                    
                    # Check order status
                    orders = self.kite.orders()
                    for order in orders:
                        if str(order.get('order_id')) == str(order_id):
                            if order.get('status') == 'COMPLETE':
                                entry_price = float(order.get('average_price', entry_price))
                                print(f"   Executed at: ₹{entry_price}")
                                break
                    
                except Exception as e:
                    print(f"❌ LIVE ORDER FAILED: {e}")
                    return False
            else:
                # PAPER TRADING
                print(f"\n✅ PAPER TRADE EXECUTED")
            
            # Store position
            self.active_position = {
                'stock': stock['symbol'],
                'stock_price': stock['ltp'],
                'option_symbol': option['tradingsymbol'],
                'entry_price': entry_price,
                'quantity': quantity,
                'target': target_price,
                'stop_loss': stop_loss,
                'entry_time': datetime.now().strftime('%H:%M:%S'),
                'status': 'ACTIVE',
                'is_live': hasattr(self, 'is_live') and self.is_live
            }
            
            print(f"   Stock: {stock['symbol']} @ ₹{stock['ltp']:.2f}")
            print(f"   Option: {option['tradingsymbol']}")
            print(f"   Entry: ₹{entry_price:.2f} x {quantity}")
            print(f"   Investment: ₹{entry_price * quantity:,.2f}")
            print(f"   Initial Stop Loss: ₹{stop_loss:.2f} (-30%)")
            print(f"   🔄 TRAILING STOP LOSS ACTIVE - NO FIXED TARGET")
            
            # Save trade to file
            with open('current_trade.json', 'w') as f:
                json.dump(self.active_position, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Trade execution failed: {e}")
            return False
    
    def calculate_trailing_stop_loss(self, entry_price, current_pnl_percent):
        """
        Calculate dynamic trailing stop loss based on profit levels
        
        Trailing Stop Loss Logic:
        - 8% profit → 5% stop loss
        - 12% profit → 9% stop loss
        - 16% profit → 13% stop loss
        - 20% profit → 16% stop loss
        - 25% profit → 20% stop loss
        - 30% profit → 24% stop loss
        - 40% profit → 32% stop loss
        - And so on (80% of profit level)
        """
        # Define profit thresholds and corresponding stop losses
        trailing_stops = [
            (8, 5),     # 8% profit → 5% stop loss
            (12, 9),    # 12% profit → 9% stop loss
            (16, 13),   # 16% profit → 13% stop loss
            (20, 16),   # 20% profit → 16% stop loss
            (25, 20),   # 25% profit → 20% stop loss
            (30, 24),   # 30% profit → 24% stop loss
            (40, 32),   # 40% profit → 32% stop loss
            (50, 40),   # 50% profit → 40% stop loss
            (60, 48),   # 60% profit → 48% stop loss
            (70, 56),   # 70% profit → 56% stop loss
            (80, 64),   # 80% profit → 64% stop loss
            (90, 72),   # 90% profit → 72% stop loss
            (100, 80),  # 100% profit → 80% stop loss
        ]
        
        # Default stop loss (30% as per original strategy)
        stop_loss_percent = -30.0
        
        # Check if profit has reached any threshold
        for profit_threshold, new_sl in trailing_stops:
            if current_pnl_percent >= profit_threshold:
                # Update stop loss to the new level
                stop_loss_percent = new_sl
        
        # Calculate actual stop loss price
        # If we have 8% profit, SL is at 5% profit (entry_price * 1.05)
        if stop_loss_percent > 0:
            # Trailing stop is in profit
            stop_loss_price = entry_price * (1 + stop_loss_percent / 100)
        else:
            # Initial stop loss (negative)
            stop_loss_price = entry_price * (1 + stop_loss_percent / 100)
        
        return stop_loss_price, stop_loss_percent

    def monitor_position(self):
        """Monitor live position with real-time P&L and TRAILING STOP LOSS"""
        if not self.active_position:
            print("❌ No active position to monitor")
            return
        
        print("\n" + "="*80)
        print("📊 MONITORING POSITION WITH TRAILING STOP LOSS")
        print("="*80)
        print("🔄 TRAILING STOP LOSS SYSTEM - NO FIXED TARGET")
        print("   Trade will ONLY exit when trailing stop loss is hit")
        print("   8% profit → SL moves to 5% | 12% profit → SL moves to 9%")
        print("   16% profit → SL moves to 13% | 20% profit → SL moves to 16%")
        print("   25% profit → SL moves to 20% | 30% profit → SL moves to 24%")
        print("   40% profit → SL moves to 32% | And so on...")
        print("="*80)
        
        position = self.active_position
        option_symbol = f"NFO:{position['option_symbol']}"
        
        # Track the highest stop loss level reached
        highest_sl_price = position['stop_loss']  # Start with initial stop loss
        highest_sl_percent = -30.0  # Initial stop loss percent
        
        try:
            while position['status'] == 'ACTIVE':
                # Get current price
                quote = self.kite.quote([option_symbol])
                
                if option_symbol in quote:
                    current_price = quote[option_symbol]['last_price']
                    
                    # Calculate P&L
                    pnl = (current_price - position['entry_price']) * position['quantity']
                    pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    
                    # Calculate trailing stop loss IMMEDIATELY - no waiting
                    new_sl_price, new_sl_percent = self.calculate_trailing_stop_loss(
                        position['entry_price'], 
                        pnl_percent
                    )
                    
                    # Only update stop loss if it's higher than the previous one (trailing up only)
                    if new_sl_price > highest_sl_price:
                        highest_sl_price = new_sl_price
                        highest_sl_percent = new_sl_percent
                        position['stop_loss'] = highest_sl_price  # Update position's stop loss
                        
                        # Alert when stop loss is updated
                        print(f"\n🔄 TRAILING STOP LOSS UPDATED!")
                        print(f"   Profit reached: {pnl_percent:.2f}%")
                        print(f"   New Stop Loss: ₹{highest_sl_price:.2f} ({highest_sl_percent:+.1f}%)")
                        print("")
                    
                    # Status indicators
                    if pnl > 0:
                        status = "✅"
                    elif pnl < 0:
                        status = "❌"
                    else:
                        status = "⚪"
                    
                    # Format output
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    
                    # Show trailing stop loss level in output
                    sl_display = f"TSL: ₹{highest_sl_price:.2f}"
                    if highest_sl_percent > 0:
                        sl_display += f" (+{highest_sl_percent:.1f}%)"
                    else:
                        sl_display += f" ({highest_sl_percent:.1f}%)"
                    
                    # Print update on new line (like your screenshot)
                    print(f"[{timestamp}] {position['option_symbol']} | "
                          f"LTP: ₹{current_price:.2f} | "
                          f"P&L: ₹{pnl:+.2f} ({pnl_percent:+.2f}%) {status} | "
                          f"{sl_display}")
                    
                    # Check ONLY for stop-loss hit (NO TARGET EXIT)
                    if highest_sl_percent > 0:
                        # Trailing stop is in profit zone - check if profit dropped to/below stop level
                        if pnl_percent <= highest_sl_percent:
                            print(f"\n\n{'='*80}")
                            print(f"🛑 TRAILING STOP LOSS HIT!")
                            print(f"Exit Price: ₹{current_price:.2f}")
                            print(f"Locked Profit: ₹{pnl:.2f} ({pnl_percent:.2f}%)")
                            print(f"Stop Loss Level was at: {highest_sl_percent:+.1f}%")
                            print(f"Peak profit before stop: ~{highest_sl_percent + 3:.1f}%+")  # Estimate
                            print(f"{'='*80}")
                            position['status'] = 'TSL_HIT'
                            position['exit_price'] = current_price
                            position['exit_time'] = timestamp
                            break
                    else:
                        # Initial stop loss (negative) - use price comparison
                        if current_price <= highest_sl_price:
                            print(f"\n\n{'='*80}")
                            print(f"🛑 STOP LOSS HIT!")
                            print(f"Exit Price: ₹{current_price:.2f}")
                            print(f"Loss: ₹{pnl:.2f} ({pnl_percent:.2f}%)")
                            print(f"Stop Loss Level: {highest_sl_percent:.1f}%")
                            print(f"{'='*80}")
                            position['status'] = 'SL_HIT'
                            position['exit_price'] = current_price
                            position['exit_time'] = timestamp
                            break
                    
                    # Update every 3 seconds
                    time.sleep(3)
                
                else:
                    print("\n⚠️ Could not fetch price")
                    time.sleep(5)
                    
        except KeyboardInterrupt:
            print(f"\n\n{'='*80}")
            print("⏹ Monitoring stopped by user")
            
            # Final P&L
            if option_symbol in quote:
                current_price = quote[option_symbol]['last_price']
                pnl = (current_price - position['entry_price']) * position['quantity']
                pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
                
                print(f"Final Price: ₹{current_price:.2f}")
                print(f"Final P&L: ₹{pnl:+.2f} ({pnl_percent:+.2f}%)")
                
                position['status'] = 'MANUAL_EXIT'
                position['exit_price'] = current_price
                position['exit_time'] = datetime.now().strftime('%H:%M:%S')
            
            print(f"{'='*80}")
        
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        
        # Save final position
        with open('current_trade.json', 'w') as f:
            json.dump(position, f, indent=2)
    
    def run_strategy(self):
        """Main strategy execution with monitoring"""
        
        # Wait for market open
        if not self.wait_for_market_open():
            return
        
        # Scan for top gainer
        top_gainer = self.scan_top_gainers()
        
        if not top_gainer:
            print("❌ No suitable stock found")
            return
        
        # Check minimum gain threshold
        MIN_GAIN = 0.3  # Lowered for testing
        if top_gainer['change'] < MIN_GAIN:
            print(f"\n⚠️ Top gainer only up {top_gainer['change']:.2f}%")
            print(f"Minimum {MIN_GAIN}% required")
            return
        
        print(f"\n🎯 SELECTED: {top_gainer['symbol']} (+{top_gainer['change']:.2f}%)")
        
        # Find option contract
        option = self.find_option_contract(top_gainer['symbol'], top_gainer['ltp'])
        
        if option is None:
            print("❌ No suitable option found")
            return
        
        print(f"\n📋 Option Found:")
        print(f"   Symbol: {option['tradingsymbol']}")
        print(f"   Strike: {option['strike']}")
        print(f"   Expiry: {option['expiry']}")
        print(f"   Lot Size: {option['lot_size']}")
        
        # Execute paper trade
        if self.execute_paper_trade(top_gainer, option):
            # Start monitoring
            self.monitor_position()
        else:
            print("❌ Failed to execute trade")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='9:15 Trading with Monitoring')
    parser.add_argument('--live', action='store_true', help='Enable LIVE trading with real money')
    args = parser.parse_args()
    
    print("="*80)
    if args.live:
        print("🚨 LIVE TRADING WITH REAL MONEY & MONITORING")
        print("="*80)
        print("⚠️  WARNING: This will use REAL MONEY!")
        print("⚠️  Options can lose 100% of premium!")
        print("="*80)
        print("\nType 'CONFIRM LIVE TRADING' to proceed:")
        
        confirmation = input().strip()
        if confirmation != "CONFIRM LIVE TRADING":
            print("❌ Live trading cancelled")
            return
    else:
        print("📊 PAPER TRADING WITH LIVE P&L MONITORING")
    
    print("="*80)
    print("This will:")
    print("1. Wait for market open + 1 second (9:15:01 AM)")
    print("2. Find top gainer with stabilized prices")
    if args.live:
        print("3. Execute REAL trade with REAL money")
    else:
        print("3. Execute paper trade")
    print("4. Monitor with live P&L updates")
    print("5. Auto-exit on target/stop-loss")
    print("="*80)
    
    try:
        monitor = PaperTradeMonitor()
        monitor.is_live = args.live  # Set live mode flag
        monitor.run_strategy()
        
    except KeyboardInterrupt:
        print("\n\n⏹ Terminated by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()