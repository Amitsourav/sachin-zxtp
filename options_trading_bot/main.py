#!/usr/bin/env python3
"""
Main Trading Bot Orchestrator
Coordinates all components: Strategy, Dashboard, Telegram, and Broker
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, time as dt_time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config import ConfigManager
from src.data.data_manager import DataManager
from src.risk.risk_manager import RiskManager
from src.strategies.strategy_915 import Strategy915
from src.brokers.paper_broker import PaperBroker
from src.notifications.telegram_bot import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingBotOrchestrator:
    """
    Main orchestrator that coordinates all trading components
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        self.config = ConfigManager(config_path)
        self.is_running = False
        self.components = {}
        
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
    async def initialize_components(self):
        """Initialize all trading components"""
        logger.info("Initializing trading bot components...")
        
        try:
            # 1. Initialize Data Manager
            logger.info("Setting up data manager...")
            self.data_manager = DataManager(self.config)
            self.components['data_manager'] = self.data_manager
            
            # 2. Initialize Risk Manager
            logger.info("Setting up risk manager...")
            self.risk_manager = RiskManager(
                config=self.config.risk.__dict__,
                initial_capital=self.config.trading.capital
            )
            self.components['risk_manager'] = self.risk_manager
            
            # 3. Initialize Broker
            logger.info("Setting up broker connection...")
            if self.config.trading.mode == 'paper':
                # Check if user wants live data for paper trading
                use_live_data = getattr(self.config.trading, 'use_live_data', True)
                
                if use_live_data:
                    from src.brokers.live_paper_broker import LivePaperBroker
                    self.broker = LivePaperBroker(
                        initial_capital=self.config.trading.capital
                    )
                    logger.info("Using PAPER TRADING with LIVE MARKET DATA")
                else:
                    self.broker = PaperBroker(
                        initial_capital=self.config.trading.capital
                    )
                    logger.info("Using PAPER TRADING with simulated data")
            elif self.config.trading.mode == 'live':
                broker_name = self.config.broker.name.lower()
                
                if broker_name == 'zerodha':
                    from src.brokers.zerodha_broker import ZerodhaBroker
                    self.broker = ZerodhaBroker(
                        api_key=self.config.broker.api_key,
                        api_secret=self.config.broker.api_secret,
                        access_token=self.config.broker.access_token
                    )
                    logger.info("Using ZERODHA for LIVE TRADING")
                else:
                    raise NotImplementedError(f"Broker {broker_name} not implemented")
            else:
                raise ValueError(f"Invalid trading mode: {self.config.trading.mode}")
                
            await self.broker.connect()
            self.components['broker'] = self.broker
            
            # 4. Initialize Telegram Bot (if configured)
            self.telegram = None
            if self.config.notifications.telegram_enabled:
                try:
                    logger.info("Setting up Telegram notifications...")
                    self.telegram = TelegramNotifier(self.config)
                    await self.telegram.initialize()
                    self.components['telegram'] = self.telegram
                except Exception as e:
                    logger.warning(f"Telegram setup failed: {e}. Continuing without notifications.")
                    
            # 5. Initialize Strategy
            logger.info("Setting up 9:15 strategy...")
            self.strategy = Strategy915(
                config=self.config,
                data_manager=self.data_manager,
                risk_manager=self.risk_manager,
                broker=self.broker,
                notifier=self.telegram
            )
            await self.strategy.initialize()
            self.components['strategy'] = self.strategy
            
            logger.info("✅ All components initialized successfully")
            
            # Display configuration
            self.display_configuration()
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
            
    def display_configuration(self):
        """Display current configuration"""
        print("\n" + "="*60)
        print("TRADING BOT CONFIGURATION")
        print("="*60)
        print(f"Mode:           {self.config.trading.mode.upper()}")
        print(f"Capital:        ₹{self.config.trading.capital:,.2f}")
        print(f"Risk per trade: {self.config.risk.max_risk_per_trade}%")
        print(f"Target:         {self.config.trading.profit_target_percent}%")
        print(f"Stop Loss:      {self.config.trading.stop_loss_percent}%")
        print(f"PCR Range:      {self.config.trading.pcr_min} - {self.config.trading.pcr_max}")
        print(f"Max daily loss: ₹{self.config.risk.max_daily_loss:,.2f}")
        print(f"Telegram:       {'Enabled' if self.telegram else 'Disabled'}")
        print("="*60 + "\n")
        
    async def run_strategy(self):
        """Run the trading strategy"""
        try:
            self.is_running = True
            
            # Check if market is open
            if not self.is_market_open():
                logger.info("Market is closed. Bot will wait for market hours.")
                
                if self.telegram:
                    await self.telegram.send_message(
                        "🤖 Trading bot started. Waiting for market hours (9:15 AM)..."
                    )
                    
            # Wait for market hours if needed
            await self.wait_for_market_hours()
            
            # Run strategy
            logger.info("Starting strategy execution...")
            await self.strategy.run_strategy()
            
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            
            if self.telegram:
                await self.telegram.send_error_alert(f"Strategy failed: {e}")
                
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        
        # Check if weekend
        if now.weekday() in [5, 6]:  # Saturday, Sunday
            return False
            
        # Check market hours (9:15 AM - 3:30 PM)
        current_time = now.time()
        market_open = dt_time(9, 15)
        market_close = dt_time(15, 30)
        
        return market_open <= current_time <= market_close
        
    async def wait_for_market_hours(self):
        """Wait until market opens"""
        while self.is_running:
            now = datetime.now()
            
            # Skip weekends
            if now.weekday() in [5, 6]:
                logger.info("Weekend - waiting for Monday...")
                await asyncio.sleep(3600)  # Check every hour
                continue
                
            # Check if before market hours
            current_time = now.time()
            market_open = dt_time(9, 14)  # Start 1 minute before
            
            if current_time < market_open:
                # Calculate wait time
                target = datetime.combine(now.date(), market_open)
                wait_seconds = (target - now).total_seconds()
                
                logger.info(f"Waiting {wait_seconds/60:.1f} minutes for market open...")
                
                # Wait, but check periodically in case of shutdown
                while wait_seconds > 0 and self.is_running:
                    sleep_time = min(wait_seconds, 60)
                    await asyncio.sleep(sleep_time)
                    wait_seconds -= sleep_time
                    
                break
            elif current_time > dt_time(15, 30):
                # Market closed for today
                logger.info("Market closed for today. Will resume tomorrow.")
                
                if self.telegram:
                    await self.telegram.send_message(
                        "📊 Market closed. Bot will resume tomorrow at 9:14 AM."
                    )
                    
                # Wait until tomorrow
                await asyncio.sleep(3600)  # Check every hour
            else:
                # Market is open
                break
                
    async def health_check_loop(self):
        """Periodic health checks"""
        while self.is_running:
            try:
                # Check component health
                health_status = {
                    'broker_connected': self.broker.is_connected if hasattr(self.broker, 'is_connected') else True,
                    'risk_ok': not getattr(self.risk_manager, 'is_blocked', False),
                    'strategy_running': self.strategy.is_running if hasattr(self.strategy, 'is_running') else True
                }
                
                if not all(health_status.values()):
                    logger.warning(f"Health check failed: {health_status}")
                    
                    if self.telegram:
                        await self.telegram.send_alert(
                            f"⚠️ Health check issue: {health_status}"
                        )
                        
                # Update dashboard status (when connected)
                # TODO: Send status to dashboard via WebSocket
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)
                
    async def shutdown(self):
        """Gracefully shutdown all components"""
        logger.info("Shutting down trading bot...")
        self.is_running = False
        
        try:
            # Stop strategy
            if hasattr(self.strategy, 'emergency_stop'):
                await self.strategy.emergency_stop()
                
            # Close all positions if any
            positions = self.broker.get_positions()
            if positions:
                logger.warning(f"Closing {len(positions)} open positions...")
                for pos in positions:
                    await self.broker.place_order(
                        symbol=pos['symbol'],
                        exchange='NFO',
                        transaction_type='SELL',
                        quantity=pos['quantity'],
                        order_type='MARKET',
                        product='MIS'
                    )
                    
            # Send final summary
            if self.telegram:
                pnl = self.broker.get_pnl()
                await self.telegram.send_message(
                    f"🛑 Bot stopped\n"
                    f"Final P&L: ₹{pnl['total_pnl']:.2f} ({pnl['pnl_percent']:.2f}%)"
                )
                
            # Disconnect broker
            if hasattr(self.broker, 'disconnect'):
                await self.broker.disconnect()
                
            logger.info("✅ Shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            
    async def main(self):
        """Main execution loop"""
        try:
            # Initialize components
            await self.initialize_components()
            
            # Create tasks
            tasks = [
                asyncio.create_task(self.run_strategy()),
                asyncio.create_task(self.health_check_loop())
            ]
            
            # Run until interrupted
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            await self.shutdown()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    raise KeyboardInterrupt


async def run_bot():
    """Entry point for running the bot"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run orchestrator
    orchestrator = TradingBotOrchestrator()
    await orchestrator.main()


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#" + " "*18 + "9:15 TRADING BOT v2.0" + " "*19 + "#")
    print("#" + " "*58 + "#")
    print("#"*60 + "\n")
    
    print("Starting trading bot...")
    print("Press Ctrl+C to stop\n")
    
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
    except Exception as e:
        print(f"\n\nBot stopped due to error: {e}")
        sys.exit(1)