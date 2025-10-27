#!/usr/bin/env python3
"""
Paper Trading with CORRECT EXPIRY and ACTUAL OPTION PRICES
Uses real option contracts from Zerodha with proper expiry dates
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from kiteconnect import KiteConnect
import yaml
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class ZerodhaPaperTradingFixed:
    """Paper trading using actual Zerodha option contracts"""
    
    def __init__(self):
        # Load configuration
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.api_key = self.config['broker']['api_key']
        self.access_token = self.config['broker']['access_token']
        
        # Initialize Zerodha connection
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        
        # Load all NFO instruments once
        print("Loading NFO instruments...")
        self.instruments = pd.DataFrame(self.kite.instruments("NFO"))
        
        # Virtual trading account
        self.virtual_capital = self.config['trading']['capital']
        self.current_capital = self.virtual_capital
        self.positions = []
        self.pnl = 0
        
        # NIFTY 50 stocks
        self.nifty50_symbols = [
            'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 
            'NSE:ICICIBANK', 'NSE:KOTAKBANK', 'NSE:SBIN', 'NSE:BHARTIARTL', 
            'NSE:ITC', 'NSE:AXISBANK', 'NSE:LT', 'NSE:BAJFINANCE', 
            'NSE:WIPRO', 'NSE:MARUTI', 'NSE:HCLTECH', 'NSE:ASIANPAINT',
            'NSE:SBILIFE', 'NSE:HDFC', 'NSE:TATAMOTORS', 'NSE:HINDALCO'
        ]
        
        print("=" * 80)
        print("PAPER TRADING WITH ACTUAL ZERODHA OPTIONS")
        print("=" * 80)
        print(f"✅ Using REAL option contracts and prices")
        print(f"✅ Virtual Capital: ₹{self.virtual_capital:,.2f}")
        print(f"✅ Today: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 80)
        
    def get_nearest_expiry(self, symbol: str):
        """Get the nearest expiry for a symbol (weekly or monthly)"""
        # Filter options for this symbol
        symbol_options = self.instruments[self.instruments['name'] == symbol]
        
        if symbol_options.empty:
            return None
            
        # Get unique expiry dates
        expiries = sorted(symbol_options['expiry'].unique())
        
        # Get the nearest expiry (first one after today)
        today = datetime.now().date()
        for exp in expiries:
            if exp >= today:
                return exp
                
        return None
        
    def get_option_contract(self, underlying: str, strike: float, expiry, option_type: str = 'CE'):
        """Get specific option contract details"""
        # Filter for exact contract
        options = self.instruments[
            (self.instruments['name'] == underlying) &
            (self.instruments['instrument_type'] == option_type) &
            (self.instruments['strike'] == strike) &
            (self.instruments['expiry'] == expiry)
        ]
        
        if not options.empty:
            return options.iloc[0]
        return None
        
    def get_option_price(self, instrument_token):
        """Get live price for an option contract"""
        try:
            quote = self.kite.quote([instrument_token])
            if instrument_token in quote:
                return quote[instrument_token]
        except Exception as e:
            print(f"Error fetching option price: {e}")
        return None
        
    def get_top_gainers(self):
        """Get top gainers from NIFTY 50"""
        print("\n📊 Fetching top gainers from Zerodha...")
        
        try:
            # Fetch quotes for NIFTY 50
            quotes = self.kite.quote(self.nifty50_symbols[:20])
            
            gainers = []
            for symbol in self.nifty50_symbols[:20]:
                if symbol in quotes:
                    data = quotes[symbol]
                    close_price = data['ohlc']['close']
                    last_price = data['last_price']
                    
                    if close_price and close_price > 0:
                        change_percent = ((last_price - close_price) / close_price) * 100
                        
                        if change_percent > 0:
                            gainers.append({
                                'symbol': symbol.split(':')[1],
                                'ltp': last_price,
                                'change_percent': change_percent,
                                'volume': data.get('volume', 0)
                            })
            
            gainers.sort(key=lambda x: x['change_percent'], reverse=True)
            
            if gainers:
                print(f"\nTop 3 Gainers:")
                print("-" * 60)
                for i, stock in enumerate(gainers[:3], 1):
                    print(f"{i}. {stock['symbol']:<12} | ₹{stock['ltp']:8.2f} | +{stock['change_percent']:.2f}%")
                    
                return gainers[0] if gainers else None
                
        except Exception as e:
            print(f"Error: {e}")
            
        return None
        
    def execute_paper_trade(self):
        """Execute paper trade with actual option contracts"""
        print("\n" + "="*60)
        print("EXECUTING 9:15 STRATEGY WITH REAL OPTIONS")
        print("="*60)
        
        # Get top gainer
        top_gainer = self.get_top_gainers()
        
        if not top_gainer:
            print("❌ No gaining stocks found")
            return
            
        underlying = top_gainer['symbol']
        spot_price = top_gainer['ltp']
        
        print(f"\n🎯 Selected Stock: {underlying}")
        print(f"   Spot Price: ₹{spot_price:.2f}")
        print(f"   Day Change: +{top_gainer['change_percent']:.2f}%")
        
        # Get nearest expiry
        expiry = self.get_nearest_expiry(underlying)
        
        if not expiry:
            print(f"❌ No options available for {underlying}")
            return
            
        days_to_expiry = (expiry - datetime.now().date()).days
        print(f"   Expiry: {expiry} ({expiry.strftime('%A')}) - {days_to_expiry} days")
        
        # Calculate ATM strike
        if spot_price < 100:
            strike_gap = 2.5
        elif spot_price < 500:
            strike_gap = 5
        elif spot_price < 1000:
            strike_gap = 10
        elif spot_price < 2000:
            strike_gap = 20
        elif spot_price < 5000:
            strike_gap = 50
        else:
            strike_gap = 100
            
        atm_strike = round(spot_price / strike_gap) * strike_gap
        print(f"   ATM Strike: {atm_strike}")
        
        # Get the actual option contract
        option_contract = self.get_option_contract(underlying, atm_strike, expiry, 'CE')
        
        if option_contract is None:
            # Try nearby strikes
            print(f"   Exact strike {atm_strike} not found, trying nearby...")
            for offset in [strike_gap, -strike_gap, strike_gap*2, -strike_gap*2]:
                test_strike = atm_strike + offset
                option_contract = self.get_option_contract(underlying, test_strike, expiry, 'CE')
                if option_contract is not None:
                    atm_strike = test_strike
                    print(f"   Using strike: {atm_strike}")
                    break
                    
        if option_contract is None:
            print(f"❌ No suitable option contract found")
            return
            
        # Get live option price
        option_data = self.get_option_price(option_contract['instrument_token'])
        
        if not option_data:
            print("❌ Could not fetch option price")
            return
            
        option_price = option_data['last_price']
        lot_size = option_contract['lot_size']
        
        print(f"\n📊 Option Contract Details:")
        print(f"   Symbol: {option_contract['tradingsymbol']}")
        print(f"   Strike: {option_contract['strike']}")
        print(f"   Expiry: {option_contract['expiry']}")
        print(f"   Lot Size: {lot_size}")
        print(f"   Current Premium: ₹{option_price:.2f}")
        
        # Calculate position size
        risk_amount = self.virtual_capital * 0.02
        max_loss_per_lot = option_price * lot_size * 0.30  # 30% SL
        num_lots = max(1, int(risk_amount / max_loss_per_lot))
        quantity = num_lots * lot_size
        
        # Create position
        position = {
            'tradingsymbol': option_contract['tradingsymbol'],
            'instrument_token': option_contract['instrument_token'],
            'underlying': underlying,
            'strike': atm_strike,
            'expiry': expiry,
            'entry_price': option_price,
            'quantity': quantity,
            'lots': num_lots,
            'lot_size': lot_size,
            'entry_time': datetime.now(),
            'target': option_price * 1.08,  # 8% target
            'stop_loss': option_price * 0.70,  # 30% stop
            'status': 'OPEN',
            'investment': option_price * quantity
        }
        
        self.positions.append(position)
        
        print(f"\n✅ PAPER TRADE EXECUTED:")
        print(f"   Option: {position['tradingsymbol']}")
        print(f"   Lots: {num_lots} x {lot_size} = {quantity} qty")
        print(f"   Entry: ₹{option_price:.2f}")
        print(f"   Target: ₹{position['target']:.2f} (+8%)")
        print(f"   Stop Loss: ₹{position['stop_loss']:.2f} (-30%)")
        print(f"   Investment: ₹{position['investment']:,.2f}")
        print(f"   Max Risk: ₹{position['investment'] * 0.30:,.2f}")
        
        # Monitor position
        asyncio.run(self.monitor_position(position))
        
    async def monitor_position(self, position):
        """Monitor position with live option prices"""
        print("\n📊 Monitoring with LIVE option prices...")
        print("Press Ctrl+C to stop\n")
        
        update_count = 0
        
        while position['status'] == 'OPEN':
            try:
                # Get live option price
                option_data = self.get_option_price(position['instrument_token'])
                
                if option_data:
                    current_price = option_data['last_price']
                    bid = option_data['depth']['buy'][0]['price'] if option_data['depth']['buy'] else current_price
                    ask = option_data['depth']['sell'][0]['price'] if option_data['depth']['sell'] else current_price
                    
                    # Calculate P&L
                    pnl = (current_price - position['entry_price']) * position['quantity']
                    pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    
                    # Display update
                    update_count += 1
                    if update_count % 2 == 0:
                        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                              f"{position['tradingsymbol']} "
                              f"LTP: ₹{current_price:.2f} "
                              f"(Bid: {bid:.2f}/Ask: {ask:.2f}) | "
                              f"P&L: ₹{pnl:+,.2f} ({pnl_percent:+.2f}%) | "
                              f"Target: {position['target']:.2f} | "
                              f"SL: {position['stop_loss']:.2f}", end='', flush=True)
                    
                    # Check exit conditions
                    if current_price >= position['target']:
                        position['status'] = 'TARGET_HIT'
                        position['exit_price'] = current_price
                        position['pnl'] = pnl
                        print(f"\n\n🎯 TARGET REACHED!")
                        print(f"   Exit Price: ₹{current_price:.2f}")
                        print(f"   Profit: ₹{pnl:,.2f} ({pnl_percent:.2f}%)")
                        break
                        
                    elif current_price <= position['stop_loss']:
                        position['status'] = 'STOP_LOSS_HIT'
                        position['exit_price'] = current_price
                        position['pnl'] = pnl
                        print(f"\n\n🛑 STOP LOSS HIT!")
                        print(f"   Exit Price: ₹{current_price:.2f}")
                        print(f"   Loss: ₹{pnl:,.2f} ({pnl_percent:.2f}%)")
                        break
                        
                await asyncio.sleep(3)
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Stopped by user")
                break
            except Exception as e:
                print(f"\nError: {e}")
                await asyncio.sleep(5)
                
        # Summary
        if position.get('pnl'):
            self.pnl += position['pnl']
            self.current_capital += position['pnl']
            
            print("\n" + "="*60)
            print("TRADE SUMMARY")
            print("="*60)
            print(f"Option: {position['tradingsymbol']}")
            print(f"Entry: ₹{position['entry_price']:.2f}")
            print(f"Exit: ₹{position.get('exit_price', position['entry_price']):.2f}")
            print(f"Trade P&L: ₹{position['pnl']:+,.2f}")
            print(f"Total P&L: ₹{self.pnl:+,.2f}")
            print(f"Current Capital: ₹{self.current_capital:,.2f}")
            print("="*60)

def main():
    """Main execution"""
    print("\n🚀 Starting Paper Trading with ACTUAL Option Contracts...")
    
    trader = ZerodhaPaperTradingFixed()
    
    try:
        trader.execute_paper_trade()
        
    except KeyboardInterrupt:
        print("\n\n👋 Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()