#!/usr/bin/env python3
"""
Paper Trading with ZERODHA LIVE DATA
Uses real Zerodha API for market data but trades with virtual money
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from kiteconnect import KiteConnect, KiteTicker
import yaml
import pandas as pd
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config import ConfigManager
from src.risk.risk_manager import RiskManager

class ZerodhaPaperTrading:
    """Paper trading using Zerodha's real-time data"""
    
    def __init__(self):
        # Load configuration
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.api_key = self.config['broker']['api_key']
        self.api_secret = self.config['broker']['api_secret']
        self.access_token = self.config['broker']['access_token']
        
        # Initialize Zerodha connection
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        
        # Virtual trading account
        self.virtual_capital = self.config['trading']['capital']
        self.current_capital = self.virtual_capital
        self.positions = []
        self.pnl = 0
        
        print("=" * 80)
        print("PAPER TRADING WITH ZERODHA LIVE DATA")
        print("=" * 80)
        print(f"✅ Using REAL Zerodha market data")
        print(f"✅ Virtual Capital: ₹{self.virtual_capital:,.2f}")
        print(f"✅ No real money at risk")
        print("=" * 80)
        
    def connect_to_zerodha(self):
        """Test Zerodha connection and fetch live data"""
        try:
            # Test connection with profile
            profile = self.kite.profile()
            print(f"\n✅ Connected to Zerodha")
            print(f"User: {profile.get('user_name', 'Unknown')}")
            print(f"Email: {profile.get('email', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Zerodha connection failed: {e}")
            print("\nFalling back to paper mode with simulated data...")
            return False
            
    def get_live_quote(self, symbol: str) -> Dict[str, Any]:
        """Get live quote from Zerodha"""
        try:
            # Convert symbol to Zerodha format
            # Example: RELIANCE -> NSE:RELIANCE
            exchange_symbol = f"NSE:{symbol}"
            
            # Get quote from Zerodha
            quote = self.kite.quote([exchange_symbol])
            
            if quote and exchange_symbol in quote:
                data = quote[exchange_symbol]
                return {
                    'symbol': symbol,
                    'ltp': data['last_price'],
                    'open': data['ohlc']['open'],
                    'high': data['ohlc']['high'],
                    'low': data['ohlc']['low'],
                    'close': data['ohlc']['close'],
                    'volume': data['volume'],
                    'change': data['net_change'],
                    'change_percent': (data['net_change'] / data['ohlc']['close']) * 100,
                    'bid': data['depth']['buy'][0]['price'] if data['depth']['buy'] else data['last_price'],
                    'ask': data['depth']['sell'][0]['price'] if data['depth']['sell'] else data['last_price'],
                    'timestamp': datetime.now()
                }
            
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            
        return None
        
    def get_top_gainers(self):
        """Get top gainers from NIFTY 50 using Zerodha data"""
        print("\n📊 Fetching NIFTY 50 gainers from Zerodha...")
        
        # NIFTY 50 symbols
        nifty50 = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HDFC',
            'ICICIBANK', 'KOTAKBANK', 'SBIN', 'BHARTIARTL', 'ITC',
            'AXISBANK', 'LT', 'BAJFINANCE', 'WIPRO', 'MARUTI',
            'HCLTECH', 'ASIANPAINT', 'ULTRACEMCO', 'TITAN', 'SUNPHARMA',
            'TECHM', 'POWERGRID', 'NTPC', 'TATAMOTORS', 'INDUSINDBK'
        ]
        
        gainers = []
        
        # Fetch data for each stock
        for symbol in nifty50[:10]:  # Top 10 for speed
            quote = self.get_live_quote(symbol)
            if quote and quote['change_percent'] > 0:
                gainers.append({
                    'symbol': symbol,
                    'ltp': quote['ltp'],
                    'change_percent': quote['change_percent']
                })
                
        # Sort by gain percentage
        gainers.sort(key=lambda x: x['change_percent'], reverse=True)
        
        if gainers:
            print("\nTop Gainers (Zerodha Data):")
            print("-" * 40)
            for i, stock in enumerate(gainers[:5], 1):
                print(f"{i}. {stock['symbol']:12} | ₹{stock['ltp']:8.2f} | +{stock['change_percent']:.2f}%")
                
        return gainers[0] if gainers else None
        
    def get_option_chain(self, symbol: str):
        """Get option chain from Zerodha"""
        try:
            # Get instruments
            instruments = self.kite.instruments("NFO")
            
            # Filter for symbol options
            symbol_options = [
                inst for inst in instruments 
                if inst['name'] == symbol and inst['instrument_type'] == 'CE'
            ]
            
            if symbol_options:
                print(f"\n📈 Found {len(symbol_options)} call options for {symbol}")
                return symbol_options[:5]  # Return top 5 strikes
                
        except Exception as e:
            print(f"Error fetching option chain: {e}")
            
        return []
        
    def execute_paper_trade(self):
        """Execute a paper trade with Zerodha data"""
        print("\n" + "="*60)
        print("EXECUTING PAPER TRADE AT 9:15 STRATEGY")
        print("="*60)
        
        # Check connection
        if not self.connect_to_zerodha():
            print("⚠️  Running in offline mode")
            return
            
        # Get top gainer
        top_gainer = self.get_top_gainers()
        
        if not top_gainer:
            print("❌ No suitable stocks found")
            return
            
        print(f"\n🎯 Selected Stock: {top_gainer['symbol']}")
        print(f"   Current Price: ₹{top_gainer['ltp']:.2f}")
        print(f"   Change: +{top_gainer['change_percent']:.2f}%")
        
        # Calculate position size (2% risk)
        risk_amount = self.current_capital * 0.02
        stop_loss_percent = 30
        position_value = risk_amount / (stop_loss_percent / 100)
        quantity = int(position_value / top_gainer['ltp'])
        
        if quantity < 1:
            quantity = 1
            
        # Create virtual position
        position = {
            'symbol': top_gainer['symbol'],
            'type': 'CALL OPTION',
            'entry_price': top_gainer['ltp'],
            'quantity': quantity,
            'entry_time': datetime.now(),
            'target': top_gainer['ltp'] * 1.08,  # 8% target
            'stop_loss': top_gainer['ltp'] * 0.70,  # 30% stop
            'status': 'OPEN'
        }
        
        self.positions.append(position)
        
        print(f"\n✅ PAPER TRADE EXECUTED:")
        print(f"   Type: BUY CALL OPTION")
        print(f"   Quantity: {quantity}")
        print(f"   Entry: ₹{position['entry_price']:.2f}")
        print(f"   Target: ₹{position['target']:.2f} (+8%)")
        print(f"   Stop Loss: ₹{position['stop_loss']:.2f} (-30%)")
        print(f"   Virtual Investment: ₹{quantity * position['entry_price']:.2f}")
        
        # Monitor position
        asyncio.run(self.monitor_position(position))
        
    async def monitor_position(self, position):
        """Monitor paper position with live Zerodha data"""
        print("\n📊 Monitoring position with LIVE Zerodha data...")
        print("Press Ctrl+C to stop\n")
        
        while position['status'] == 'OPEN':
            try:
                # Get live price from Zerodha
                quote = self.get_live_quote(position['symbol'])
                
                if quote:
                    current_price = quote['ltp']
                    pnl = (current_price - position['entry_price']) * position['quantity']
                    pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    
                    # Display update
                    print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                          f"{position['symbol']} @ ₹{current_price:.2f} | "
                          f"P&L: ₹{pnl:+.2f} ({pnl_percent:+.2f}%) | "
                          f"Target: ₹{position['target']:.2f} | "
                          f"SL: ₹{position['stop_loss']:.2f}", end='')
                    
                    # Check exit conditions
                    if current_price >= position['target']:
                        position['status'] = 'TARGET_HIT'
                        position['exit_price'] = current_price
                        position['pnl'] = pnl
                        print(f"\n\n🎯 TARGET REACHED! Profit: ₹{pnl:.2f}")
                        break
                        
                    elif current_price <= position['stop_loss']:
                        position['status'] = 'STOP_LOSS_HIT'
                        position['exit_price'] = current_price
                        position['pnl'] = pnl
                        print(f"\n\n🛑 STOP LOSS HIT! Loss: ₹{pnl:.2f}")
                        break
                        
                await asyncio.sleep(5)  # Check every 5 seconds
                
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
            print(f"Trade P&L: ₹{position['pnl']:+.2f}")
            print(f"Total P&L: ₹{self.pnl:+.2f}")
            print(f"Current Capital: ₹{self.current_capital:,.2f}")
            print("="*60)

def main():
    """Main execution"""
    print("\n🚀 Starting Paper Trading with Zerodha Live Data...")
    
    trader = ZerodhaPaperTrading()
    
    try:
        # Check if market is open
        now = datetime.now()
        if now.weekday() in [5, 6]:
            print("\n⚠️  Market is closed (Weekend)")
            print("Running demo with last available data...")
            
        elif now.hour < 9 or now.hour >= 16:
            print("\n⚠️  Market is closed")
            print("Running demo with last available data...")
            
        trader.execute_paper_trade()
        
    except KeyboardInterrupt:
        print("\n\n👋 Paper trading stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()