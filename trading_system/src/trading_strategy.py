"""
Core 9:15 Strategy Trading Logic
Implements the automated trading strategy with precise timing
"""

import logging
from datetime import datetime, time
import pytz
from typing import Dict, List, Optional, Tuple
import time as time_module
from dataclasses import dataclass

from .data_fetcher import NSEDataFetcher
from .broker_interface import BrokerInterface, BrokerFactory
from .notifications import NotificationManager

logger = logging.getLogger(__name__)

@dataclass
class TradeSignal:
    """Represents a trading signal"""
    symbol: str
    strike_price: float
    pcr_value: float
    entry_price: float
    target_price: float
    signal_time: datetime
    confidence: float

class TradingStrategy:
    """Main 9:15 Strategy Implementation"""
    
    def __init__(self, config: Dict, broker: BrokerInterface, notifier: 'NotificationManager'):
        self.config = config
        self.broker = broker
        self.notifier = notifier
        self.data_fetcher = NSEDataFetcher()
        
        # Trading parameters
        self.trading_config = config.get('trading', {})
        self.pcr_min = self.trading_config.get('pcr_min_range', 0.7)
        self.pcr_max = self.trading_config.get('pcr_max_range', 1.5)
        self.profit_target = self.trading_config.get('profit_target_percent', 8.0)
        self.timezone = pytz.timezone(self.trading_config.get('timezone', 'Asia/Kolkata'))
        
        # Execution times
        self.scan_time = time(9, 14, 0)  # 9:14 AM
        self.execution_time = time(9, 15, 0)  # 9:15 AM
        
        # State variables
        self.current_position = None
        self.selected_stock = None
        self.trade_executed_today = False
        
    def run_strategy(self):
        """Main strategy execution loop"""
        logger.info("Starting 9:15 Strategy...")
        
        # Check if it's a trading day
        if not self.data_fetcher.is_trading_day():
            logger.info("Today is not a trading day. Exiting.")
            self.notifier.send_message("📅 Today is not a trading day. Strategy will not execute.")
            return
        
        # Check market volatility
        if not self._check_market_conditions():
            logger.info("Market conditions not suitable for trading.")
            return
        
        # Wait for scan time (9:14 AM)
        self._wait_for_time(self.scan_time)
        
        # Execute pre-market scan
        signal = self._execute_premarket_scan()
        
        if not signal:
            logger.info("No suitable trading signal found.")
            self.notifier.send_message("❌ No suitable trading signal found for today.")
            return
        
        # Wait for execution time (9:15 AM)
        self._wait_for_time(self.execution_time)
        
        # Execute trade
        if self._execute_trade(signal):
            # Start monitoring position
            self._monitor_position()
        
    def _check_market_conditions(self) -> bool:
        """Check if market conditions are suitable for trading"""
        try:
            # Check VIX
            vix = self.data_fetcher.get_vix()
            if vix and vix > self.config.get('risk', {}).get('volatility_threshold', 25):
                logger.warning(f"High volatility detected (VIX: {vix}). Skipping trading.")
                self.notifier.send_message(f"⚠️ High volatility (VIX: {vix:.2f}). Trading skipped for safety.")
                return False
            
            # Check if already traded today
            if self.trade_executed_today:
                logger.info("Daily trade limit reached.")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking market conditions: {e}")
            return False
    
    def _wait_for_time(self, target_time: time):
        """Wait until the specified time"""
        while True:
            now = datetime.now(self.timezone).time()
            
            if now >= target_time:
                break
            
            # Calculate seconds to wait
            now_seconds = now.hour * 3600 + now.minute * 60 + now.second
            target_seconds = target_time.hour * 3600 + target_time.minute * 60 + target_time.second
            
            wait_seconds = target_seconds - now_seconds
            if wait_seconds > 0:
                logger.info(f"Waiting {wait_seconds} seconds until {target_time}")
                time_module.sleep(min(wait_seconds, 60))  # Sleep max 1 minute at a time
            else:
                break
    
    def _execute_premarket_scan(self) -> Optional[TradeSignal]:
        """Execute pre-market scan to find trading opportunity"""
        try:
            logger.info("Executing pre-market scan...")
            self.notifier.send_message("🔍 Starting pre-market scan for NIFTY50 gainers...")
            
            # Get pre-market gainers
            gainers = self.data_fetcher.get_nifty50_premarket_gainers()
            
            if not gainers:
                logger.error("No gainers found in pre-market scan")
                return None
            
            logger.info(f"Found {len(gainers)} gainers. Analyzing options...")
            
            # Analyze each gainer for suitable PCR
            for gainer in gainers:
                signal = self._analyze_stock_for_trade(gainer)
                if signal:
                    self.selected_stock = gainer
                    return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error in pre-market scan: {e}")
            return None
    
    def _analyze_stock_for_trade(self, stock_data: Dict) -> Optional[TradeSignal]:
        """Analyze a stock for trading opportunity"""
        try:
            symbol = stock_data['symbol']
            logger.info(f"Analyzing {symbol} (Change: {stock_data['change_percent']:.2f}%)")
            
            # Get option chain
            option_data = self.data_fetcher.get_option_chain(symbol)
            if not option_data:
                logger.warning(f"Could not fetch option chain for {symbol}")
                return None
            
            # Find ATM strike
            spot_price = stock_data['price']
            atm_strike = self.data_fetcher.find_atm_strike(symbol, spot_price)
            
            if not atm_strike:
                logger.warning(f"Could not find ATM strike for {symbol}")
                return None
            
            # Calculate PCR
            pcr = self.data_fetcher.calculate_pcr(option_data, atm_strike)
            
            if not pcr:
                logger.warning(f"Could not calculate PCR for {symbol} strike {atm_strike}")
                return None
            
            logger.info(f"{symbol}: ATM Strike {atm_strike}, PCR: {pcr}")
            
            # Check PCR range
            if self.pcr_min <= pcr <= self.pcr_max:
                # Create option symbol (format: SYMBOL24DDMMMCE)
                option_symbol = self._create_option_symbol(symbol, atm_strike, 'CE')
                
                signal = TradeSignal(
                    symbol=option_symbol,
                    strike_price=atm_strike,
                    pcr_value=pcr,
                    entry_price=0.0,  # Will be set during execution
                    target_price=0.0,  # Will be calculated during execution
                    signal_time=datetime.now(self.timezone),
                    confidence=self._calculate_confidence(stock_data, pcr)
                )
                
                logger.info(f"✅ Trade signal generated for {symbol}: Strike {atm_strike}, PCR {pcr}")
                self.notifier.send_message(
                    f"📈 Trade Signal Found!\n"
                    f"Stock: {symbol}\n"
                    f"Strike: {atm_strike}\n"
                    f"PCR: {pcr:.2f}\n"
                    f"Gain: {stock_data['change_percent']:.2f}%"
                )
                
                return signal
            else:
                logger.info(f"{symbol}: PCR {pcr} outside range [{self.pcr_min}, {self.pcr_max}]")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing {stock_data.get('symbol', 'Unknown')}: {e}")
            return None
    
    def _create_option_symbol(self, base_symbol: str, strike: float, option_type: str) -> str:
        """Create option symbol in NSE format"""
        # Get current month/year for expiry
        now = datetime.now(self.timezone)
        
        # For simplicity, using weekly expiry (Thursday)
        # Format: SYMBOL24DDMMMCE (e.g., RELIANCE2425JANC3000)
        expiry_str = f"{now.strftime('%d%b').upper()}"
        year_str = str(now.year)[2:]  # Last 2 digits of year
        
        # Format strike price (remove decimal if whole number)
        strike_str = str(int(strike)) if strike == int(strike) else str(strike)
        
        option_symbol = f"{base_symbol}{year_str}{expiry_str}{option_type}{strike_str}"
        return option_symbol
    
    def _calculate_confidence(self, stock_data: Dict, pcr: float) -> float:
        """Calculate confidence score for the trade signal"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for higher gains
        gain_factor = min(stock_data['change_percent'] / 5.0, 0.3)  # Max 0.3 boost
        confidence += gain_factor
        
        # Higher confidence for PCR closer to 1.0
        pcr_factor = 0.2 - abs(1.0 - pcr) * 0.2  # Max 0.2 boost
        confidence += pcr_factor
        
        # Volume factor
        if stock_data.get('volume', 0) > 100000:  # High volume
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _execute_trade(self, signal: TradeSignal) -> bool:
        """Execute the trade at 9:15 AM"""
        try:
            logger.info(f"Executing trade for {signal.symbol} at {signal.strike_price}")
            
            # Get current option price
            current_price = self.broker.get_ltp(signal.symbol)
            if current_price <= 0:
                logger.error(f"Could not get valid price for {signal.symbol}")
                return False
            
            # Calculate target price
            target_price = current_price * (1 + self.profit_target / 100)
            signal.entry_price = current_price
            signal.target_price = target_price
            
            # Calculate quantity (1 lot = lot size for the instrument)
            # For simplicity, using 1 lot = quantity of 1 for paper trading
            quantity = 1
            
            # Place market order
            order_result = self.broker.place_order(
                symbol=signal.symbol,
                quantity=quantity,
                order_type='MARKET'
            )
            
            if order_result['success']:
                self.current_position = {
                    'signal': signal,
                    'order_id': order_result['order_id'],
                    'quantity': quantity,
                    'entry_time': datetime.now(self.timezone)
                }
                
                self.trade_executed_today = True
                
                logger.info(f"Trade executed successfully: {signal.symbol} @ ₹{current_price}")
                self.notifier.send_message(
                    f"✅ Trade Executed!\n"
                    f"Symbol: {signal.symbol}\n"
                    f"Entry Price: ₹{current_price:.2f}\n"
                    f"Target: ₹{target_price:.2f} (+{self.profit_target}%)\n"
                    f"Order ID: {order_result['order_id']}"
                )
                
                return True
            else:
                logger.error(f"Trade execution failed: {order_result['message']}")
                self.notifier.send_message(f"❌ Trade execution failed: {order_result['message']}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            self.notifier.send_message(f"❌ Trade execution error: {str(e)}")
            return False
    
    def _monitor_position(self):
        """Monitor position for profit target"""
        if not self.current_position:
            return
        
        logger.info("Starting position monitoring...")
        signal = self.current_position['signal']
        
        while self.current_position:
            try:
                # Get current price
                current_price = self.broker.get_ltp(signal.symbol)
                
                if current_price <= 0:
                    logger.warning("Could not get current price, retrying...")
                    time_module.sleep(5)
                    continue
                
                # Calculate current PnL
                pnl_percent = ((current_price - signal.entry_price) / signal.entry_price) * 100
                
                logger.info(f"Current price: ₹{current_price:.2f}, PnL: {pnl_percent:.2f}%")
                
                # Check if target reached
                if pnl_percent >= self.profit_target:
                    self._exit_position(current_price, "Target reached")
                    break
                
                # Check if it's near market close (3:20 PM)
                now = datetime.now(self.timezone).time()
                if now >= time(15, 20):
                    self._exit_position(current_price, "Market close approaching")
                    break
                
                # Wait before next check
                time_module.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in position monitoring: {e}")
                time_module.sleep(30)  # Wait longer on error
    
    def _exit_position(self, exit_price: float, reason: str):
        """Exit the current position"""
        try:
            if not self.current_position:
                return
            
            signal = self.current_position['signal']
            
            # For paper trading, use the sell_position method
            if hasattr(self.broker, 'sell_position'):
                # Find position index
                positions = self.broker.get_positions()
                for i, pos in enumerate(positions):
                    if pos['symbol'] == signal.symbol:
                        result = self.broker.sell_position(i)
                        break
                else:
                    logger.error("Position not found for exit")
                    return
            else:
                # For real broker, place sell order
                result = self.broker.place_order(
                    symbol=signal.symbol,
                    quantity=self.current_position['quantity'],
                    order_type='MARKET'
                )
            
            if result['success']:
                # Calculate final PnL
                pnl_percent = ((exit_price - signal.entry_price) / signal.entry_price) * 100
                pnl_amount = (exit_price - signal.entry_price) * self.current_position['quantity']
                
                logger.info(f"Position exited: {reason}")
                logger.info(f"Final PnL: ₹{pnl_amount:.2f} ({pnl_percent:.2f}%)")
                
                self.notifier.send_message(
                    f"🎯 Position Closed!\n"
                    f"Reason: {reason}\n"
                    f"Exit Price: ₹{exit_price:.2f}\n"
                    f"PnL: ₹{pnl_amount:.2f} ({pnl_percent:.2f}%)\n"
                    f"Duration: {datetime.now(self.timezone) - self.current_position['entry_time']}"
                )
                
                # Clear current position
                self.current_position = None
                
            else:
                logger.error(f"Failed to exit position: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error exiting position: {e}")
    
    def get_status(self) -> Dict:
        """Get current strategy status"""
        status = {
            'trade_executed_today': self.trade_executed_today,
            'current_position': None,
            'selected_stock': self.selected_stock,
            'last_update': datetime.now(self.timezone).isoformat()
        }
        
        if self.current_position:
            signal = self.current_position['signal']
            current_price = self.broker.get_ltp(signal.symbol)
            pnl_percent = ((current_price - signal.entry_price) / signal.entry_price) * 100 if current_price > 0 else 0
            
            status['current_position'] = {
                'symbol': signal.symbol,
                'entry_price': signal.entry_price,
                'current_price': current_price,
                'target_price': signal.target_price,
                'pnl_percent': pnl_percent,
                'entry_time': self.current_position['entry_time'].isoformat()
            }
        
        return status