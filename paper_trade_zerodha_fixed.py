#!/usr/bin/env python3
"""
Fixed Paper Trading with ZERODHA LIVE DATA
Uses correct format for fetching Zerodha quotes
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from kiteconnect import KiteConnect
import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class ZerodhaPaperTrading:
    """Paper trading using Zerodha's real-time data"""
    
    def __init__(self):
        # Load configuration
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.api_key = self.config['broker']['api_key']
        self.access_token = self.config['broker']['access_token']
        
        # Initialize Zerodha connection
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        
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
            'NSE:ULTRACEMCO', 'NSE:TITAN', 'NSE:SUNPHARMA', 'NSE:TECHM',
            'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:INDUSINDBK',
            'NSE:M&M', 'NSE:HINDUNILVR', 'NSE:ADANIPORTS', 'NSE:COALINDIA',
            'NSE:DIVISLAB', 'NSE:DRREDDY', 'NSE:UPL', 'NSE:ONGC',
            'NSE:JSWSTEEL', 'NSE:GRASIM', 'NSE:BPCL', 'NSE:CIPLA',
            'NSE:EICHERMOT', 'NSE:SHREECEM', 'NSE:HEROMOTOCO', 'NSE:BAJAJFINSV',
            'NSE:NESTLEIND', 'NSE:BRITANNIA', 'NSE:TATACONSUM', 'NSE:ADANIENT',
            'NSE:HINDALCO', 'NSE:SBILIFE', 'NSE:APOLLOHOSP', 'NSE:TATASTEEL',
            'NSE:HDFC', 'NSE:VEDL'
        ]
        
        print("=" * 80)
        print("PAPER TRADING WITH ZERODHA LIVE DATA")
        print("=" * 80)
        print(f"✅ Using REAL Zerodha market data")
        print(f"✅ Virtual Capital: ₹{self.virtual_capital:,.2f}")
        print(f"✅ No real money at risk")
        print(f"✅ Market Status: {'OPEN' if self.is_market_open() else 'CLOSED'}")
        print("=" * 80)
        
    def is_market_open(self):
        """Check if market is open"""
        now = datetime.now()
        if now.weekday() in [5, 6]:  # Weekend
            return False
        if now.hour < 9 or (now.hour == 9 and now.minute < 15):
            return False
        if now.hour >= 15 and now.minute > 30:
            return False
        return True
        
    def connect_to_zerodha(self):
        """Test Zerodha connection and fetch live data"""
        try:
            # Test connection with profile
            profile = self.kite.profile()
            print(f"\n✅ Connected to Zerodha")
            print(f"User: {profile.get('user_name', 'Unknown')}")
            return True
            
        except Exception as e:
            print(f"\n❌ Zerodha connection failed: {e}")
            return False
            
    def get_top_gainers(self):
        """Get top gainers from NIFTY 50 using correct Zerodha format"""
        print("\n📊 Fetching NIFTY 50 gainers from Zerodha...")
        
        try:
            # Fetch quotes for all NIFTY 50 stocks
            # Split into batches to avoid API limits
            batch_size = 20
            all_gainers = []
            
            for i in range(0, len(self.nifty50_symbols), batch_size):
                batch = self.nifty50_symbols[i:i+batch_size]
                quotes = self.kite.quote(batch)
                
                for symbol in batch:
                    if symbol in quotes:
                        data = quotes[symbol]
                        
                        # Calculate change percentage
                        close_price = data['ohlc']['close']
                        last_price = data['last_price']
                        
                        if close_price and close_price > 0:
                            change_percent = ((last_price - close_price) / close_price) * 100
                            
                            # Only add gainers (positive change)
                            if change_percent > 0:
                                all_gainers.append({
                                    'symbol': symbol.split(':')[1],  # Remove NSE: prefix
                                    'ltp': last_price,
                                    'change_percent': change_percent,
                                    'volume': data.get('volume', 0)
                                })
            
            # Sort by gain percentage
            all_gainers.sort(key=lambda x: x['change_percent'], reverse=True)
            
            if all_gainers:
                print(f"\n✅ Found {len(all_gainers)} gaining stocks")
                print("\nTop 5 Gainers (Live Zerodha Data):")
                print("-" * 60)
                print(f"{'Rank':<5} {'Symbol':<15} {'LTP':<12} {'Change %':<10} {'Volume':<15}")
                print("-" * 60)
                
                for i, stock in enumerate(all_gainers[:5], 1):
                    print(f"{i:<5} {stock['symbol']:<15} ₹{stock['ltp']:<11.2f} {stock['change_percent']:+.2f}%      {stock['volume']:,}")
                    
                return all_gainers[0] if all_gainers else None
            else:
                print("\n⚠️  No gaining stocks found in NIFTY 50")
                print("Showing top movers instead:")
                
                # Show all stocks with their changes
                all_stocks = []
                quotes = self.kite.quote(self.nifty50_symbols[:10])
                
                for symbol in self.nifty50_symbols[:10]:
                    if symbol in quotes:
                        data = quotes[symbol]
                        close_price = data['ohlc']['close']
                        last_price = data['last_price']
                        
                        if close_price and close_price > 0:
                            change_percent = ((last_price - close_price) / close_price) * 100
                            print(f"  {symbol:<20} | ₹{last_price:8.2f} | {change_percent:+.2f}%")
                
                return None
                
        except Exception as e:
            print(f"Error fetching quotes: {e}")
            return None
            
    def execute_paper_trade(self):
        """Execute a paper trade with Zerodha data"""
        print("\n" + "="*60)
        print("EXECUTING PAPER TRADE - 9:15 STRATEGY")
        print("="*60)
        
        # Check connection
        if not self.connect_to_zerodha():
            print("⚠️  Cannot connect to Zerodha")
            return
            
        # Get top gainer
        top_gainer = self.get_top_gainers()
        
        if not top_gainer:
            print("\n❌ No suitable stocks found for trading")
            print("   Strategy requires at least one gaining stock")
            return
            
        print(f"\n🎯 SELECTED STOCK: {top_gainer['symbol']}")
        print(f"   Current Price: ₹{top_gainer['ltp']:.2f}")
        print(f"   Day Change: +{top_gainer['change_percent']:.2f}%")
        print(f"   Volume: {top_gainer['volume']:,}")
        
        # Calculate position size (2% risk)
        risk_amount = self.current_capital * 0.02
        stop_loss_percent = 30
        
        # For options, we'll simulate option pricing
        # Typically ATM options are 2-3% of stock price
        option_price = top_gainer['ltp'] * 0.025  # 2.5% of stock price
        
        # Option lot size (simplified)
        lot_size = 25 if top_gainer['ltp'] > 2000 else 50
        num_lots = int(risk_amount / (option_price * lot_size * 0.30))  # Based on 30% SL
        
        if num_lots < 1:
            num_lots = 1
            
        quantity = num_lots * lot_size
        
        # Calculate strike price (ATM)
        strike = round(top_gainer['ltp'] / 50) * 50 if top_gainer['ltp'] < 1000 else round(top_gainer['ltp'] / 100) * 100
        
        # Create virtual position
        position = {
            'symbol': f"{top_gainer['symbol']} {strike} CE",
            'underlying': top_gainer['symbol'],
            'type': 'CALL OPTION',
            'strike': strike,
            'entry_price': option_price,
            'quantity': quantity,
            'lots': num_lots,
            'lot_size': lot_size,
            'entry_time': datetime.now(),
            'target': option_price * 1.08,  # 8% target
            'stop_loss': option_price * 0.70,  # 30% stop
            'underlying_price': top_gainer['ltp'],
            'status': 'OPEN'
        }
        
        self.positions.append(position)
        
        print(f"\n✅ PAPER TRADE EXECUTED:")
        print(f"   Option: {position['symbol']}")
        print(f"   Strike: {strike}")
        print(f"   Type: BUY CALL OPTION")
        print(f"   Lots: {num_lots} (Qty: {quantity})")
        print(f"   Entry: ₹{position['entry_price']:.2f}")
        print(f"   Target: ₹{position['target']:.2f} (+8%)")
        print(f"   Stop Loss: ₹{position['stop_loss']:.2f} (-30%)")
        print(f"   Virtual Investment: ₹{quantity * position['entry_price']:,.2f}")
        
        # Monitor position
        asyncio.run(self.monitor_position(position))
        
    async def monitor_position(self, position):
        """Monitor paper position with live Zerodha data"""
        print("\n📊 Monitoring position with LIVE Zerodha data...")
        print("Press Ctrl+C to stop\n")
        
        monitor_count = 0
        
        while position['status'] == 'OPEN':
            try:
                # Get live underlying price from Zerodha
                symbol_with_exchange = f"NSE:{position['underlying']}"
                quotes = self.kite.quote([symbol_with_exchange])
                
                if symbol_with_exchange in quotes:
                    data = quotes[symbol_with_exchange]
                    current_underlying = data['last_price']
                    
                    # Simulate option price based on underlying movement
                    # This is simplified - real options have complex pricing
                    underlying_change = (current_underlying - position['underlying_price']) / position['underlying_price']
                    
                    # Options typically have 2-3x leverage
                    option_change = underlying_change * 2.5
                    current_option_price = position['entry_price'] * (1 + option_change)
                    
                    # Calculate P&L
                    pnl = (current_option_price - position['entry_price']) * position['quantity']
                    pnl_percent = ((current_option_price - position['entry_price']) / position['entry_price']) * 100
                    
                    # Display update
                    monitor_count += 1
                    if monitor_count % 2 == 0:  # Update display every 2 checks
                        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                              f"{position['underlying']} @ ₹{current_underlying:.2f} | "
                              f"Option: ₹{current_option_price:.2f} | "
                              f"P&L: ₹{pnl:+,.2f} ({pnl_percent:+.2f}%) | "
                              f"Target: ₹{position['target']:.2f} | "
                              f"SL: ₹{position['stop_loss']:.2f}", end='', flush=True)
                    
                    # Check exit conditions
                    if current_option_price >= position['target']:
                        position['status'] = 'TARGET_HIT'
                        position['exit_price'] = current_option_price
                        position['pnl'] = pnl
                        print(f"\n\n🎯 TARGET REACHED! Profit: ₹{pnl:,.2f} ({pnl_percent:.2f}%)")
                        break
                        
                    elif current_option_price <= position['stop_loss']:
                        position['status'] = 'STOP_LOSS_HIT'
                        position['exit_price'] = current_option_price
                        position['pnl'] = pnl
                        print(f"\n\n🛑 STOP LOSS HIT! Loss: ₹{pnl:,.2f} ({pnl_percent:.2f}%)")
                        break
                        
                await asyncio.sleep(3)  # Check every 3 seconds
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\nError monitoring: {e}")
                await asyncio.sleep(5)
                
        # Final summary
        if position.get('pnl'):
            self.pnl += position['pnl']
            self.current_capital += position['pnl']
            
            print("\n" + "="*60)
            print("PAPER TRADE SUMMARY")
            print("="*60)
            print(f"Trade P&L: ₹{position['pnl']:+,.2f}")
            print(f"Total P&L: ₹{self.pnl:+,.2f}")
            print(f"Current Capital: ₹{self.current_capital:,.2f}")
            print(f"Return: {(self.pnl/self.virtual_capital)*100:+.2f}%")
            print("="*60)

def main():
    """Main execution"""
    print("\n🚀 Starting Paper Trading with Zerodha Live Data...")
    print(f"   Current Time: {datetime.now().strftime('%H:%M:%S')}")
    
    trader = ZerodhaPaperTrading()
    
    try:
        trader.execute_paper_trade()
        
    except KeyboardInterrupt:
        print("\n\n👋 Paper trading stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()