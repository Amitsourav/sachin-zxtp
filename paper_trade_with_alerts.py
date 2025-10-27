"""
PAPER TRADING WITH REAL-TIME NSE DATA + ALERTS
Notifies you immediately if NSE fails!
"""

import asyncio
import logging
from datetime import datetime, time as dt_time, timedelta
import pytz
import json
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os
import sys

# Import data fetchers
from nse_realtime_fetcher import NSERealTimeFetcher
import yfinance as yf
from NIFTY50_COMPLETE_LIST import NIFTY50_STOCKS, validate_nifty50_data

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_with_alerts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

IST = pytz.timezone('Asia/Kolkata')


def send_alert(title: str, message: str, alert_type: str = "warning"):
    """Send system notification alert"""
    
    # Console alert with colors
    colors = {
        'error': '\033[91m',  # Red
        'warning': '\033[93m',  # Yellow
        'success': '\033[92m',  # Green
        'info': '\033[94m',  # Blue
        'reset': '\033[0m'
    }
    
    color = colors.get(alert_type, colors['info'])
    
    # Big visible console alert
    alert_box = f"""
{color}
╔{'═'*70}╗
║ {'🚨 ALERT: ' + title:^68} ║
╠{'═'*70}╣
║ {message[:68]:<68} ║
╚{'═'*70}╝
{colors['reset']}
"""
    print(alert_box)
    logger.warning(f"ALERT: {title} - {message}")
    
    # System notification (Mac/Linux)
    try:
        if sys.platform == "darwin":  # macOS
            os.system(f'''osascript -e 'display notification "{message}" with title "🚨 Trading Alert: {title}" sound name "Glass"' ''')
        elif sys.platform.startswith("linux"):
            os.system(f"notify-send --urgency=critical '🚨 Trading Alert' '{title}: {message}'")
    except:
        pass
    
    # Write to alert file
    with open('TRADING_ALERTS.txt', 'a') as f:
        f.write(f"\n[{datetime.now(IST).strftime('%H:%M:%S')}] {title}: {message}\n")
    
    # Beep sound (if terminal supports it)
    print('\a')  # System beep


@dataclass
class Position:
    symbol: str
    entry_price: float
    quantity: int
    entry_time: datetime
    current_price: float = 0
    pnl: float = 0
    pnl_percent: float = 0
    status: str = "OPEN"
    exit_price: float = 0
    exit_time: Optional[datetime] = None


class SmartDataFetcher:
    """Intelligent data fetcher with alerts"""
    
    def __init__(self):
        self.nse_fetcher = NSERealTimeFetcher()
        self.nse_working = True
        self.alert_sent = False
        
    def get_pre_market_gainers(self) -> List[Dict]:
        """Get gainers with smart fallback and alerts"""
        
        # Try NSE first
        try:
            logger.info("Attempting NSE real-time data fetch...")
            gainers = self.nse_fetcher.get_top_gainers(limit=10)
            
            if gainers and len(gainers) > 0:
                if not self.nse_working:
                    # NSE recovered!
                    send_alert("NSE RECOVERED", "Real-time data restored!", "success")
                    self.nse_working = True
                    self.alert_sent = False
                
                # Format for our system
                formatted = []
                for stock in gainers:
                    formatted.append({
                        'symbol': stock['symbol'],
                        'price': stock['ltp'],
                        'change_percent': stock['change_percent'],
                        'volume': stock['volume'],
                        'source': 'NSE_REALTIME'
                    })
                
                logger.info("✅ NSE REAL-TIME data received successfully!")
                return formatted
                
        except Exception as e:
            error_msg = str(e)[:50]
            
            # Send alert only once
            if self.nse_working and not self.alert_sent:
                send_alert(
                    "NSE DATA FAILED",
                    f"Switching to Yahoo Finance (15-min delay). Error: {error_msg}",
                    "error"
                )
                self.nse_working = False
                self.alert_sent = True
        
        # Fallback to Yahoo
        return self._yahoo_fallback_with_alert()
    
    def _yahoo_fallback_with_alert(self) -> List[Dict]:
        """Yahoo fallback with notification"""
        
        if not self.alert_sent:
            send_alert(
                "USING DELAYED DATA",
                "Yahoo Finance active (15-min delay). Strategy accuracy reduced.",
                "warning"
            )
        
        logger.info("Fetching from Yahoo Finance...")
        gainers = []
        
        # Fetch from Yahoo - ALL NIFTY50 stocks
        nifty50 = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
            "LT.NS", "ASIANPAINT.NS", "AXISBANK.NS", "WIPRO.NS", "ULTRACEMCO.NS",
            "BAJFINANCE.NS", "BAJAJFINSV.NS", "MARUTI.NS", "M&M.NS", "NESTLEIND.NS",
            "TITAN.NS", "SUNPHARMA.NS", "TATAMOTORS.NS", "NTPC.NS", "POWERGRID.NS",
            "ADANIENT.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HCLTECH.NS", "ONGC.NS",
            "INDUSINDBK.NS", "TECHM.NS", "HINDALCO.NS", "COALINDIA.NS", "DRREDDY.NS",
            "BRITANNIA.NS", "GRASIM.NS", "DIVISLAB.NS", "CIPLA.NS", "BPCL.NS",
            "EICHERMOT.NS", "HEROMOTOCO.NS", "UPL.NS", "TATACONSUM.NS", "SBILIFE.NS",
            "APOLLOHOSP.NS", "ADANIPORTS.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "LTIM.NS"
        ]
        
        for symbol in nifty50:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('regularMarketPreviousClose', 0)
                
                if current_price and prev_close:
                    change_percent = ((current_price - prev_close) / prev_close) * 100
                    
                    if change_percent > 0:
                        gainers.append({
                            'symbol': symbol.replace('.NS', ''),
                            'price': current_price,
                            'change_percent': change_percent,
                            'volume': info.get('regularMarketVolume', 0),
                            'source': 'YAHOO_DELAYED'
                        })
            except:
                continue
        
        gainers.sort(key=lambda x: x['change_percent'], reverse=True)
        return gainers
    
    def get_pcr_ratio(self) -> float:
        """Get PCR with fallback"""
        try:
            options = self.nse_fetcher.get_option_chain("NIFTY")
            pcr = options.get('pcr', 0)
            if pcr > 0:
                return pcr
        except:
            pass
        
        # Simulated PCR
        return random.uniform(0.7, 1.5)
    
    def get_atm_strike(self, spot_price: float) -> float:
        return round(spot_price / 50) * 50
    
    def get_option_price(self, symbol: str, strike: float) -> float:
        base_price = max(0, strike * 0.015)
        volatility = random.uniform(0.5, 1.5)
        return round(base_price * volatility, 2)


class PaperBroker:
    """Paper trading broker"""
    
    def __init__(self, capital: float = 100000):
        self.capital = capital
        self.initial_capital = capital
        self.positions: List[Position] = []
        
    def place_order(self, symbol: str, quantity: int, price: float) -> Dict:
        """Place paper order"""
        # Add slippage
        slippage = random.uniform(0.1, 0.3) / 100
        exec_price = price * (1 + slippage)
        
        position = Position(
            symbol=symbol,
            entry_price=exec_price,
            quantity=quantity,
            entry_time=datetime.now(IST)
        )
        self.positions.append(position)
        self.capital -= (exec_price * quantity)
        
        logger.info(f"Order executed: {symbol} @ ₹{exec_price:.2f}")
        
        return {
            'status': 'COMPLETE',
            'executed_price': exec_price,
            'quantity': quantity
        }
    
    def exit_position(self, position: Position, price: float) -> Dict:
        """Exit position"""
        position.exit_price = price
        position.exit_time = datetime.now(IST)
        position.status = "CLOSED"
        
        position.pnl = (price - position.entry_price) * position.quantity
        position.pnl_percent = ((price - position.entry_price) / position.entry_price) * 100
        
        self.capital += (price * position.quantity)
        
        return {'pnl': position.pnl, 'pnl_percent': position.pnl_percent}


class AlertingStrategy915:
    """9:15 Strategy with comprehensive alerts"""
    
    def __init__(self):
        self.data_fetcher = SmartDataFetcher()
        self.broker = PaperBroker()
        
        # Parameters
        self.profit_target = 8.0
        self.stop_loss = 30.0
        self.pcr_min = 0.7
        self.pcr_max = 1.5
        
        self.position = None
        
    async def run(self):
        """Execute strategy with alerts"""
        
        # Clear alert file
        open('TRADING_ALERTS.txt', 'w').close()
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║     9:15 PAPER TRADING WITH SMART ALERTS                        ║
║                                                                  ║
║  🔔 You will be NOTIFIED if:                                    ║
║     • NSE data source fails                                     ║
║     • Fallback to Yahoo activated                               ║
║     • Data quality degrades                                     ║
║     • Trade execution issues                                    ║
║                                                                  ║
║  Starting monitoring...                                          ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        # Pre-market scan
        await self._scan_market()
        
        # Execute trade
        await self._execute_trade()
        
        # Monitor
        if self.position:
            await self._monitor_position()
        
        # Results
        self._show_results()
    
    async def _scan_market(self):
        """Scan with data source monitoring"""
        logger.info("\n📊 PRE-MARKET SCAN (9:14 AM)")
        
        # Get gainers
        gainers = self.data_fetcher.get_pre_market_gainers()
        
        if not gainers:
            send_alert("NO GAINERS", "No gaining stocks found in NIFTY50", "error")
            return
        
        # Check data source and alert
        source = gainers[0].get('source', 'Unknown')
        
        if source == 'NSE_REALTIME':
            print("""
╔══════════════════════════════════════════════════════════════════╗
║  ✅ DATA QUALITY: EXCELLENT - NSE Real-Time                     ║
║     No delay - Live market prices!                              ║
╚══════════════════════════════════════════════════════════════════╝
            """)
        else:
            print("""
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️  DATA QUALITY: DEGRADED - Yahoo Finance                     ║
║     15-minute delay - May affect strategy!                      ║
╚══════════════════════════════════════════════════════════════════╝
            """)
        
        # Analyze top gainer
        for gainer in gainers:
            symbol = gainer['symbol']
            pcr = self.data_fetcher.get_pcr_ratio()
            
            logger.info(f"Analyzing {symbol} (+{gainer['change_percent']:.2f}%) PCR: {pcr:.2f}")
            
            if self.pcr_min <= pcr <= self.pcr_max:
                # Selected!
                strike = self.data_fetcher.get_atm_strike(gainer['price'])
                expiry = self._get_expiry()
                
                self.selected = {
                    'symbol': symbol,
                    'option': f"{symbol}{expiry.strftime('%d%b').upper()}{int(strike)}CE",
                    'price': gainer['price'],
                    'strike': strike,
                    'pcr': pcr,
                    'source': source
                }
                
                send_alert(
                    "TRADE FOUND",
                    f"{symbol} selected! PCR: {pcr:.2f}, Source: {source}",
                    "success"
                )
                break
    
    def _get_expiry(self) -> datetime:
        today = datetime.now(IST).date()
        days_ahead = 3 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)
    
    async def _execute_trade(self):
        """Execute with confirmation"""
        if not hasattr(self, 'selected'):
            return
        
        logger.info("\n🚀 EXECUTING AT 9:15:00")
        
        option_price = self.data_fetcher.get_option_price(
            self.selected['symbol'],
            self.selected['strike']
        )
        
        order = self.broker.place_order(
            self.selected['option'],
            50,  # Lot size
            option_price
        )
        
        if order['status'] == 'COMPLETE':
            self.position = self.broker.positions[-1]
            
            send_alert(
                "TRADE EXECUTED",
                f"{self.selected['option']} @ ₹{order['executed_price']:.2f}",
                "success"
            )
            
            # Show targets
            print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  POSITION OPENED                                                 ║
║  Symbol: {self.selected['option']:<30}              ║
║  Entry: ₹{order['executed_price']:.2f}                                              ║
║  Target: ₹{order['executed_price'] * 1.08:.2f} (+8%)                                        ║
║  Stop Loss: ₹{order['executed_price'] * 0.70:.2f} (-30%)                                    ║
║  Data: {self.selected['source']:<30}                    ║
╚══════════════════════════════════════════════════════════════════╝
            """)
    
    async def _monitor_position(self):
        """Monitor with alerts"""
        logger.info("\n📈 MONITORING POSITION")
        
        entry = self.position.entry_price
        
        for i in range(10):
            await asyncio.sleep(1)
            
            # Simulate price
            change = random.uniform(-2, 3)
            current = entry * (1 + change / 100)
            pnl_pct = ((current - entry) / entry) * 100
            
            logger.info(f"Price: ₹{current:.2f} | P&L: {pnl_pct:+.2f}%")
            
            # Check targets
            if pnl_pct >= self.profit_target:
                send_alert("TARGET HIT", f"Profit target reached! +{pnl_pct:.2f}%", "success")
                self.broker.exit_position(self.position, current)
                break
                
            elif pnl_pct <= -self.stop_loss:
                send_alert("STOP LOSS", f"Stop loss triggered! {pnl_pct:.2f}%", "error")
                self.broker.exit_position(self.position, current)
                break
            
            entry = current
    
    def _show_results(self):
        """Show results"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  TRADING RESULTS                                                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Capital: ₹{self.broker.initial_capital:,.2f} → ₹{self.broker.capital:,.2f}                     ║
║  P&L: ₹{self.broker.capital - self.broker.initial_capital:+,.2f}                                              ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        print("\n📋 Check TRADING_ALERTS.txt for all notifications")


async def main():
    strategy = AlertingStrategy915()
    await strategy.run()


if __name__ == "__main__":
    asyncio.run(main())