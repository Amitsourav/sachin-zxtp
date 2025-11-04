"""
Main application entry point for 9:15 Strategy Trading System
"""

import argparse
import sys
import os
from datetime import datetime
import signal
import time

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from logger import setup_logging, log_function_call
from trading_strategy import TradingStrategy
from broker_interface import BrokerFactory
from notifications import NotificationManager
from backtesting import BacktestEngine, run_quick_backtest
from data_fetcher import NSEDataFetcher

import logging

class TradingApplication:
    """Main trading application class"""
    
    def __init__(self, config_path: str = None):
        self.config_manager = ConfigManager(config_path or "config/config.yaml")
        self.config = self.config_manager.load_config()
        
        # Setup logging
        self.logger_setup = setup_logging(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.broker = None
        self.notifier = None
        self.strategy = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    @log_function_call()
    def initialize(self):
        """Initialize all application components"""
        try:
            self.logger.info("Initializing 9:15 Strategy Trading System...")
            
            # Initialize notification manager
            self.notifier = NotificationManager(self.config)
            
            # Test notifications if enabled
            if self.config.get('notifications', {}).get('telegram', {}).get('enabled') or \
               self.config.get('notifications', {}).get('email', {}).get('enabled'):
                test_results = self.notifier.test_notifications()
                self.logger.info(f"Notification test results: {test_results}")
            
            # Initialize broker
            broker_config = self.config_manager.get_broker_config()
            self.broker = BrokerFactory.create_broker(broker_config)
            
            if not self.broker.authenticate():
                raise Exception("Broker authentication failed")
            
            # Initialize trading strategy
            self.strategy = TradingStrategy(self.config, self.broker, self.notifier)
            
            self.logger.info("✅ Application initialized successfully")
            self.notifier.send_message("🤖 9:15 Strategy system initialized and ready for trading!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Application initialization failed: {e}")
            if self.notifier:
                self.notifier.send_error_alert(str(e), "Initialization Error")
            return False
    
    def run_strategy(self):
        """Run the main trading strategy"""
        try:
            if not self.strategy:
                raise Exception("Strategy not initialized")
            
            self.running = True
            self.logger.info("Starting trading strategy execution...")
            
            # Run the strategy
            self.strategy.run_strategy()
            
        except Exception as e:
            self.logger.error(f"Strategy execution failed: {e}")
            if self.notifier:
                self.notifier.send_error_alert(str(e), "Strategy Execution Error")
        finally:
            self.running = False
    
    def run_backtest(self, start_date: str = None, end_date: str = None, months: int = 6):
        """Run backtesting"""
        try:
            self.logger.info("Starting backtest...")
            
            if start_date and end_date:
                # Custom date range
                engine = BacktestEngine(self.config)
                results = engine.run_backtest(start_date, end_date)
            else:
                # Quick backtest
                results = run_quick_backtest(self.config, months)
            
            if 'error' in results:
                self.logger.error(f"Backtest failed: {results['error']}")
                return False
            
            # Display results
            performance = results.get('performance', {})
            self.logger.info("📊 Backtest Results:")
            self.logger.info(f"Total Trades: {performance.get('total_trades', 0)}")
            self.logger.info(f"Win Rate: {performance.get('win_rate', 0):.2f}%")
            self.logger.info(f"Total Return: {performance.get('total_return', 0):.2f}%")
            self.logger.info(f"Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
            self.logger.info(f"Max Drawdown: {performance.get('max_drawdown', 0):.2f}%")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"data/backtest_results_{timestamp}.json"
            
            if hasattr(engine, 'save_results'):
                engine.save_results(results_file)
                self.logger.info(f"Results saved to {results_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            return False
    
    def test_components(self):
        """Test all system components"""
        try:
            self.logger.info("Testing system components...")
            
            # Test data fetcher
            data_fetcher = NSEDataFetcher()
            self.logger.info("Testing market data fetching...")
            
            if data_fetcher.is_trading_day():
                self.logger.info("✅ Today is a trading day")
            else:
                self.logger.info("ℹ️ Today is not a trading day")
            
            # Test broker connection
            self.logger.info("Testing broker connection...")
            if self.broker and self.broker.authenticate():
                self.logger.info("✅ Broker connection successful")
            else:
                self.logger.warning("⚠️ Broker connection failed")
            
            # Test notifications
            self.logger.info("Testing notifications...")
            if self.notifier:
                test_results = self.notifier.test_notifications()
                for channel, result in test_results.items():
                    status = "✅" if result else "❌"
                    self.logger.info(f"{status} {channel.capitalize()} notification test")
            
            self.logger.info("Component testing completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Component testing failed: {e}")
            return False
    
    def get_status(self):
        """Get current system status"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'running': self.running,
                'broker_authenticated': bool(self.broker),
                'paper_trading': self.config_manager.is_paper_trading(),
                'environment': self.config.get('environment', 'development')
            }
            
            if self.strategy:
                strategy_status = self.strategy.get_status()
                status.update(strategy_status)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {'error': str(e)}
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
        if self.notifier:
            self.notifier.send_message("🛑 System shutdown initiated")
        
        sys.exit(0)
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down application...")
        self.running = False
        
        if self.notifier:
            self.notifier.send_message("👋 9:15 Strategy system shutdown complete")

def create_cli_parser():
    """Create command line interface parser"""
    parser = argparse.ArgumentParser(
        description="9:15 Strategy - Automated Options Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py run                    # Run the trading strategy
  python main.py backtest -m 3          # Run 3-month backtest
  python main.py backtest -s 2024-01-01 -e 2024-06-30  # Custom backtest period
  python main.py test                   # Test system components
  python main.py status                 # Get system status
        """
    )
    
    parser.add_argument(
        'command',
        choices=['run', 'backtest', 'test', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '-s', '--start-date',
        type=str,
        help='Start date for backtest (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '-e', '--end-date',
        type=str,
        help='End date for backtest (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '-m', '--months',
        type=int,
        default=6,
        help='Number of months for quick backtest (default: 6)'
    )
    
    parser.add_argument(
        '--paper',
        action='store_true',
        help='Force paper trading mode'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser

def main():
    """Main entry point"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    try:
        # Create application
        app = TradingApplication(args.config)
        
        # Override paper trading if specified
        if args.paper:
            app.config['broker']['paper_trading'] = True
        
        # Override log level if verbose
        if args.verbose:
            app.config['logging']['level'] = 'DEBUG'
            # Reinitialize logging with new level
            setup_logging(app.config)
        
        # Initialize application
        if not app.initialize():
            sys.exit(1)
        
        # Execute command
        if args.command == 'run':
            print("🚀 Starting 9:15 Strategy Trading System...")
            print("Press Ctrl+C to stop")
            app.run_strategy()
            
        elif args.command == 'backtest':
            print("📊 Running backtest...")
            success = app.run_backtest(
                args.start_date,
                args.end_date,
                args.months
            )
            if not success:
                sys.exit(1)
                
        elif args.command == 'test':
            print("🧪 Testing system components...")
            success = app.test_components()
            if not success:
                sys.exit(1)
                
        elif args.command == 'status':
            print("📋 System Status:")
            status = app.get_status()
            for key, value in status.items():
                print(f"  {key}: {value}")
        
        app.shutdown()
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()