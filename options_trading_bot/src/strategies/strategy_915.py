"""
9:15 Strategy Implementation with High-Precision Execution
Executes trades at exactly 9:15:00 with minimal delay
"""

import asyncio
import logging
from datetime import datetime, time as dt_time
from typing import Dict, Any, Optional, List
from enum import Enum

from ..core.precision_timer import Strategy915Timer, ExecutionOptimizer
from ..core.config import ConfigManager
from ..data.data_manager import DataManager
from ..risk.risk_manager import RiskManager
from ..brokers.base_broker import BaseBroker
from ..notifications.telegram_bot import TelegramNotifier

logger = logging.getLogger(__name__)


class StrategyState(Enum):
    """Strategy execution states"""
    IDLE = "idle"
    SCANNING = "scanning"
    PREPARING = "preparing"
    READY = "ready"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    CLOSED = "closed"
    ERROR = "error"


class Strategy915:
    """
    High-precision 9:15 AM Options Trading Strategy
    
    Strategy Rules:
    1. Scan NIFTY50 for top gainers at 9:14:00
    2. Check PCR (Put-Call Ratio) between 0.7-1.5
    3. Prepare order at 9:14:50
    4. Execute at EXACTLY 9:15:00
    5. Monitor with 8% target and 30% stop loss
    """
    
    def __init__(
        self,
        config: ConfigManager,
        data_manager: DataManager,
        risk_manager: RiskManager,
        broker: BaseBroker,
        notifier: Optional[TelegramNotifier] = None
    ):
        self.config = config
        self.data_manager = data_manager
        self.risk_manager = risk_manager
        self.broker = broker
        self.notifier = notifier
        
        # Strategy components
        self.timer = Strategy915Timer()
        self.optimizer = ExecutionOptimizer()
        
        # State management
        self.state = StrategyState.IDLE
        self.current_position = None
        self.today_trades = []
        self.is_running = False
        
        # Pre-calculated data
        self.scan_data = {}
        self.order_params = {}
        
    async def initialize(self):
        """Initialize strategy and sync time"""
        logger.info("Initializing 9:15 Strategy...")
        
        # Initialize timer with NTP sync
        await self.timer.initialize()
        
        # Pre-warm broker connection for faster execution
        if hasattr(self.broker, 'connect'):
            self.optimizer.pre_warm_connection(self.broker)
            
        # Load configuration
        self.profit_target = self.config.trading.profit_target_percent
        self.stop_loss = self.config.trading.stop_loss_percent
        self.pcr_min = self.config.trading.pcr_min
        self.pcr_max = self.config.trading.pcr_max
        
        self.state = StrategyState.IDLE
        logger.info("Strategy initialized successfully")
        
    async def scan_pre_market(self) -> Dict[str, Any]:
        """
        Scan market at 9:14:00 to find best opportunity
        All heavy calculations done here, 1 minute before execution
        """
        self.state = StrategyState.SCANNING
        logger.info("Starting pre-market scan...")
        
        try:
            # Fetch NIFTY50 stocks data
            nifty50_stocks = self.data_manager.get_nifty50_stocks()
            
            # Get pre-market gainers in parallel for speed
            market_data = await self.optimizer.parallel_data_fetch(
                nifty50_stocks[:10],  # Top 10 for speed
                self.data_manager.get_stock_data
            )
            
            # Find top gainer
            top_gainer = None
            max_change = 0
            
            for symbol, data in market_data.items():
                if data and data.get('change_percent', 0) > max_change:
                    max_change = data['change_percent']
                    top_gainer = symbol
                    
            if not top_gainer:
                raise ValueError("No suitable gainer found")
                
            # Get PCR for validation
            pcr = self.data_manager.get_pcr_ratio()
            
            # Validate PCR range
            if not (self.pcr_min <= pcr <= self.pcr_max):
                logger.warning(f"PCR {pcr:.2f} outside range [{self.pcr_min}-{self.pcr_max}]")
                if self.config.trading.strict_pcr_check:
                    raise ValueError(f"PCR {pcr:.2f} outside acceptable range")
                    
            # Get option chain and select strike
            spot_price = market_data[top_gainer]['ltp']
            strike_price = self.calculate_atm_strike(spot_price)
            option_symbol = f"{top_gainer}{strike_price}CE"
            
            # Store scan results
            self.scan_data = {
                'timestamp': datetime.now(),
                'top_gainer': top_gainer,
                'change_percent': max_change,
                'pcr': pcr,
                'spot_price': spot_price,
                'strike_price': strike_price,
                'option_symbol': option_symbol,
                'market_data': market_data
            }
            
            # Send notification
            if self.notifier:
                await self.notifier.send_scan_alert(self.scan_data)
                
            logger.info(f"Scan complete: {top_gainer} (+{max_change:.2f}%), PCR: {pcr:.2f}")
            return self.scan_data
            
        except Exception as e:
            logger.error(f"Pre-market scan failed: {e}")
            self.state = StrategyState.ERROR
            raise
            
    async def prepare_order(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare order at 9:14:50 with all parameters ready
        No calculations here, just organizing for instant execution
        """
        self.state = StrategyState.PREPARING
        logger.info("Preparing order for execution...")
        
        try:
            # Get option details
            option_symbol = scan_data['option_symbol']
            option_data = self.data_manager.get_option_data(option_symbol)
            
            if not option_data:
                raise ValueError(f"No data for option {option_symbol}")
                
            # Calculate position size using risk management
            position_size = self.risk_manager.calculate_position_size(
                option_data['ltp'],
                self.stop_loss
            )
            
            # Determine lot size
            lot_size = option_data.get('lot_size', 50)  # NIFTY lot size
            num_lots = position_size // lot_size
            
            if num_lots == 0:
                logger.warning("Position size too small for even 1 lot")
                num_lots = 1  # Minimum 1 lot
                
            quantity = num_lots * lot_size
            
            # Pre-calculate all order parameters
            self.order_params = {
                'symbol': option_symbol,
                'exchange': 'NFO',
                'transaction_type': 'BUY',
                'quantity': quantity,
                'order_type': 'MARKET',
                'product': 'MIS',  # Intraday
                'validity': 'DAY',
                'disclosed_quantity': 0,
                'trigger_price': 0,
                'price': 0,  # Market order
                # Pre-calculated values
                'expected_entry': option_data['ltp'],
                'target_price': option_data['ltp'] * (1 + self.profit_target / 100),
                'stop_loss_price': option_data['ltp'] * (1 - self.stop_loss / 100),
                'risk_amount': quantity * option_data['ltp'] * (self.stop_loss / 100),
                'prepared_at': datetime.now()
            }
            
            self.state = StrategyState.READY
            logger.info(f"Order ready: {quantity} qty of {option_symbol}")
            return self.order_params
            
        except Exception as e:
            logger.error(f"Order preparation failed: {e}")
            self.state = StrategyState.ERROR
            raise
            
    async def execute_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute order at EXACTLY 9:15:00
        This should be instant - all decisions already made
        """
        self.state = StrategyState.EXECUTING
        
        try:
            # Final risk check (quick)
            if not self.risk_manager.can_take_position(order_params['risk_amount']):
                raise ValueError("Risk limit exceeded")
                
            # EXECUTE NOW! No delays!
            order_response = await self.broker.place_order(**order_params)
            
            if not order_response or order_response.get('status') == 'REJECTED':
                raise ValueError(f"Order rejected: {order_response}")
                
            # Create position record
            self.current_position = {
                'order_id': order_response['order_id'],
                'symbol': order_params['symbol'],
                'quantity': order_params['quantity'],
                'entry_price': order_response.get('executed_price', order_params['expected_entry']),
                'entry_time': datetime.now(),
                'target': order_params['target_price'],
                'stop_loss': order_params['stop_loss_price'],
                'status': 'OPEN'
            }
            
            # Add to risk manager
            self.risk_manager.add_position(
                self.current_position['symbol'],
                self.current_position['quantity'],
                self.current_position['entry_price']
            )
            
            # Send notification
            if self.notifier:
                await self.notifier.send_trade_alert(self.current_position)
                
            self.state = StrategyState.MONITORING
            logger.info(f"Order executed: {order_response['order_id']}")
            
            return {
                'success': True,
                'order_id': order_response['order_id'],
                'position': self.current_position,
                'response': order_response
            }
            
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            self.state = StrategyState.ERROR
            
            if self.notifier:
                await self.notifier.send_error_alert(f"Execution failed: {e}")
                
            raise
            
    async def monitor_position(self):
        """
        Monitor position for target/stop loss after execution
        """
        if not self.current_position or self.current_position['status'] != 'OPEN':
            return
            
        logger.info("Monitoring position for exit conditions...")
        
        while self.current_position and self.current_position['status'] == 'OPEN':
            try:
                # Get current price
                current_data = self.data_manager.get_option_data(
                    self.current_position['symbol']
                )
                
                if not current_data:
                    await asyncio.sleep(5)
                    continue
                    
                current_price = current_data['ltp']
                entry_price = self.current_position['entry_price']
                
                # Calculate P&L
                pnl = (current_price - entry_price) * self.current_position['quantity']
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                # Check target
                if current_price >= self.current_position['target']:
                    logger.info(f"Target reached! PnL: {pnl_percent:.2f}%")
                    await self.exit_position('TARGET', current_price)
                    break
                    
                # Check stop loss
                elif current_price <= self.current_position['stop_loss']:
                    logger.warning(f"Stop loss hit! PnL: {pnl_percent:.2f}%")
                    await self.exit_position('STOPLOSS', current_price)
                    break
                    
                # Check risk manager signals
                elif self.risk_manager.check_stop_loss(self.current_position['symbol']):
                    logger.warning("Risk manager triggered stop loss")
                    await self.exit_position('RISK_STOP', current_price)
                    break
                    
                # Check time-based exit (3:15 PM)
                elif datetime.now().time() >= dt_time(15, 15):
                    logger.info("Market closing - exiting position")
                    await self.exit_position('TIME_EXIT', current_price)
                    break
                    
                # Update dashboard/notifications periodically
                if int(datetime.now().second) % 30 == 0:  # Every 30 seconds
                    if self.notifier:
                        await self.notifier.send_position_update(
                            self.current_position,
                            current_price,
                            pnl,
                            pnl_percent
                        )
                        
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error monitoring position: {e}")
                await asyncio.sleep(5)
                
    async def exit_position(self, reason: str, exit_price: float):
        """Exit current position"""
        if not self.current_position:
            return
            
        try:
            # Place exit order
            exit_order = await self.broker.place_order(
                symbol=self.current_position['symbol'],
                exchange='NFO',
                transaction_type='SELL',
                quantity=self.current_position['quantity'],
                order_type='MARKET',
                product='MIS'
            )
            
            # Calculate final P&L
            entry_price = self.current_position['entry_price']
            quantity = self.current_position['quantity']
            pnl = (exit_price - entry_price) * quantity
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100
            
            # Update position
            self.current_position.update({
                'status': 'CLOSED',
                'exit_price': exit_price,
                'exit_time': datetime.now(),
                'exit_reason': reason,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'exit_order_id': exit_order.get('order_id')
            })
            
            # Update risk manager
            self.risk_manager.remove_position(self.current_position['symbol'])
            self.risk_manager.update_daily_pnl(pnl)
            
            # Add to today's trades
            self.today_trades.append(self.current_position)
            
            # Send notification
            if self.notifier:
                await self.notifier.send_exit_alert(self.current_position)
                
            logger.info(f"Position closed: {reason}, PnL: ₹{pnl:.2f} ({pnl_percent:.2f}%)")
            
            # Clear current position
            self.current_position = None
            self.state = StrategyState.CLOSED
            
        except Exception as e:
            logger.error(f"Failed to exit position: {e}")
            raise
            
    async def run_strategy(self):
        """
        Main strategy execution loop
        Runs the complete sequence with precise timing
        """
        try:
            # Initialize
            await self.initialize()
            self.is_running = True
            
            logger.info("Starting 9:15 Strategy execution...")
            
            # Run the precision-timed sequence
            result = await self.timer.run_complete_sequence(
                scan_callback=self.scan_pre_market,
                prepare_callback=self.prepare_order,
                execute_callback=self.execute_order
            )
            
            # Log execution metrics
            if result and result.get('execution_metrics'):
                metrics = result['execution_metrics']
                logger.info(f"Execution metrics: Total delay: {metrics['total_delay_ms']:.1f}ms")
                
            # Monitor position until exit
            if self.current_position:
                await self.monitor_position()
                
            # Send daily summary
            if self.notifier:
                await self.send_daily_summary()
                
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            self.state = StrategyState.ERROR
            
            if self.notifier:
                await self.notifier.send_error_alert(f"Strategy failed: {e}")
                
        finally:
            self.is_running = False
            logger.info("Strategy execution completed")
            
    async def send_daily_summary(self):
        """Send end-of-day summary"""
        total_pnl = sum(trade.get('pnl', 0) for trade in self.today_trades)
        win_count = sum(1 for trade in self.today_trades if trade.get('pnl', 0) > 0)
        total_trades = len(self.today_trades)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        summary = {
            'date': datetime.now().date(),
            'total_trades': total_trades,
            'winning_trades': win_count,
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'trades': self.today_trades
        }
        
        if self.notifier:
            await self.notifier.send_daily_summary(summary)
            
        logger.info(f"Daily Summary: Trades: {total_trades}, PnL: ₹{total_pnl:.2f}, Win Rate: {win_rate:.1f}%")
        
    def calculate_atm_strike(self, spot_price: float) -> int:
        """Calculate At-The-Money strike price"""
        # Round to nearest 50 for NIFTY, 100 for stocks
        if spot_price < 1000:
            return round(spot_price / 50) * 50
        else:
            return round(spot_price / 100) * 100
            
    async def emergency_stop(self):
        """Emergency stop - close all positions immediately"""
        logger.warning("EMERGENCY STOP TRIGGERED!")
        
        self.is_running = False
        
        if self.current_position and self.current_position['status'] == 'OPEN':
            try:
                current_price = self.data_manager.get_option_data(
                    self.current_position['symbol']
                )['ltp']
                await self.exit_position('EMERGENCY', current_price)
            except Exception as e:
                logger.error(f"Emergency exit failed: {e}")
                
        self.state = StrategyState.CLOSED
        
        if self.notifier:
            await self.notifier.send_alert("🛑 EMERGENCY STOP - All positions closed")