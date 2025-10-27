#!/usr/bin/env python3
"""
Paper Trading with ACTUAL Zerodha Option Data
Shows real expiry dates and real option prices
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import sys

class RealOptionTrading:
    def __init__(self):
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.kite = KiteConnect(api_key=self.config['broker']['api_key'])
        self.kite.set_access_token(self.config['broker']['access_token'])
        
        # Virtual capital
        self.capital = self.config['trading']['capital']
        
        print("=" * 80)
        print("PAPER TRADING WITH ACTUAL OPTION CONTRACTS AND PRICES")
        print("=" * 80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Capital: ₹{self.capital:,.2f}")
        
        # Load instruments
        print("\nLoading option contracts...")
        self.instruments = pd.DataFrame(self.kite.instruments('NFO'))
        
    def get_top_gainer(self):
        """Get top gainer from watchlist"""
        stocks = ['NSE:SBILIFE', 'NSE:RELIANCE', 'NSE:TCS', 'NSE:INFY', 'NSE:BHARTIARTL']
        
        quotes = self.kite.quote(stocks)
        
        gainers = []
        for symbol in stocks:
            if symbol in quotes:
                data = quotes[symbol]
                change = ((data['last_price'] - data['ohlc']['close']) / data['ohlc']['close'] * 100)
                if change > 0:
                    gainers.append({
                        'symbol': symbol.split(':')[1],
                        'ltp': data['last_price'],
                        'change': change
                    })
        
        gainers.sort(key=lambda x: x['change'], reverse=True)
        return gainers[0] if gainers else None
        
    def execute_trade(self):
        """Execute paper trade with real option"""
        print("\n" + "="*60)
        print("FINDING TRADE OPPORTUNITY")
        print("="*60)
        
        # Get top gainer
        top = self.get_top_gainer()
        
        if not top:
            print("No gainers found")
            return
            
        print(f"\n✅ Selected: {top['symbol']}")
        print(f"   Spot Price: ₹{top['ltp']:.2f} (+{top['change']:.2f}%)")
        
        # Find nearest expiry (tomorrow Oct 28)
        tomorrow = datetime(2025, 10, 28).date()
        
        # Filter options for this stock
        stock_options = self.instruments[
            (self.instruments['name'] == top['symbol']) &
            (self.instruments['expiry'] == tomorrow) &
            (self.instruments['instrument_type'] == 'CE')
        ]
        
        if stock_options.empty:
            print(f"❌ No options expiring tomorrow for {top['symbol']}")
            
            # Find next expiry
            next_expiries = self.instruments[
                (self.instruments['name'] == top['symbol']) &
                (self.instruments['instrument_type'] == 'CE')
            ]['expiry'].unique()
            
            next_expiries = sorted([e for e in next_expiries if e > datetime.now().date()])
            
            if next_expiries:
                next_expiry = next_expiries[0]
                print(f"   Next expiry available: {next_expiry}")
                
                stock_options = self.instruments[
                    (self.instruments['name'] == top['symbol']) &
                    (self.instruments['expiry'] == next_expiry) &
                    (self.instruments['instrument_type'] == 'CE')
                ]
            else:
                return
        
        # Find ATM strike
        strikes = sorted(stock_options['strike'].unique())
        atm_strike = min(strikes, key=lambda x: abs(x - top['ltp']))
        
        # Get the option contract
        option = stock_options[stock_options['strike'] == atm_strike].iloc[0]
        
        print(f"\n📊 OPTION CONTRACT:")
        print(f"   Symbol: {option['tradingsymbol']}")
        print(f"   Strike: {option['strike']}")
        print(f"   Expiry: {option['expiry']} ({(option['expiry'] - datetime.now().date()).days} days)")
        print(f"   Lot Size: {option['lot_size']}")
        
        # Get live option price
        try:
            quote = self.kite.quote([option['instrument_token']])
            if option['instrument_token'] in quote:
                opt_data = quote[option['instrument_token']]
                
                ltp = opt_data['last_price']
                bid = opt_data['depth']['buy'][0]['price'] if opt_data['depth']['buy'] else 0
                ask = opt_data['depth']['sell'][0]['price'] if opt_data['depth']['sell'] else 0
                volume = opt_data.get('volume', 0)
                oi = opt_data.get('oi', 0)
                
                print(f"\n💰 LIVE OPTION PRICE:")
                print(f"   LTP: ₹{ltp:.2f}")
                print(f"   Bid/Ask: ₹{bid:.2f} / ₹{ask:.2f}")
                print(f"   Volume: {volume:,}")
                print(f"   OI: {oi:,}")
                
                # Calculate position
                risk_per_trade = 0.02  # 2% risk
                risk_amount = self.capital * risk_per_trade
                
                # With 30% stop loss
                max_loss_per_lot = ltp * option['lot_size'] * 0.30
                num_lots = max(1, int(risk_amount / max_loss_per_lot))
                quantity = num_lots * option['lot_size']
                investment = ltp * quantity
                
                print(f"\n📈 PAPER POSITION:")
                print(f"   Action: BUY {num_lots} lot(s)")
                print(f"   Quantity: {quantity} ({num_lots} x {option['lot_size']})")
                print(f"   Entry Price: ₹{ltp:.2f}")
                print(f"   Investment: ₹{investment:,.2f}")
                print(f"   Target (8%): ₹{ltp * 1.08:.2f}")
                print(f"   Stop Loss (30%): ₹{ltp * 0.70:.2f}")
                print(f"   Max Risk: ₹{investment * 0.30:,.2f}")
                
                # Start monitoring
                position = {
                    'symbol': option['tradingsymbol'],
                    'token': option['instrument_token'],
                    'entry': ltp,
                    'quantity': quantity,
                    'target': ltp * 1.08,
                    'stop_loss': ltp * 0.70,
                    'investment': investment
                }
                
                asyncio.run(self.monitor(position))
                
            else:
                print("❌ Could not get option quote")
                
        except Exception as e:
            print(f"❌ Error getting option price: {e}")
            
    async def monitor(self, position):
        """Monitor position with live data"""
        print("\n" + "="*60)
        print("MONITORING POSITION (Press Ctrl+C to stop)")
        print("="*60)
        
        check_count = 0
        
        while True:
            try:
                quote = self.kite.quote([position['token']])
                
                if position['token'] in quote:
                    data = quote[position['token']]
                    ltp = data['last_price']
                    
                    pnl = (ltp - position['entry']) * position['quantity']
                    pnl_pct = ((ltp - position['entry']) / position['entry']) * 100
                    
                    check_count += 1
                    if check_count % 2 == 0:  # Update every 2 checks
                        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                              f"{position['symbol']} @ ₹{ltp:.2f} | "
                              f"P&L: ₹{pnl:+,.2f} ({pnl_pct:+.2f}%) | "
                              f"Target: {position['target']:.2f} | "
                              f"SL: {position['stop_loss']:.2f}    ", 
                              end='', flush=True)
                    
                    # Check exit
                    if ltp >= position['target']:
                        print(f"\n\n✅ TARGET HIT! Profit: ₹{pnl:,.2f}")
                        break
                    elif ltp <= position['stop_loss']:
                        print(f"\n\n❌ STOP LOSS! Loss: ₹{pnl:,.2f}")
                        break
                        
                await asyncio.sleep(3)
                
            except KeyboardInterrupt:
                print("\n\nStopped by user")
                break
            except Exception as e:
                print(f"\nError: {e}")
                await asyncio.sleep(5)

def main():
    trader = RealOptionTrading()
    trader.execute_trade()

if __name__ == "__main__":
    main()