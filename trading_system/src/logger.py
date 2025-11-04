"""
Comprehensive logging system for the trading application
"""

import logging
import logging.handlers
import os
from datetime import datetime
import sys
import colorlog
from typing import Optional, Dict
import json

class TradingLogger:
    """Custom logger for the trading system"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.log_config = config.get('logging', {})
        self.setup_logging()
    
    def setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.log_config.get('file_path', 'logs/trading.log'))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Get log level
        log_level = getattr(logging, self.log_config.get('level', 'INFO').upper())
        
        # Create root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Setup console handler with colors
        self._setup_console_handler(root_logger, log_level)
        
        # Setup file handler
        self._setup_file_handler(root_logger, log_level)
        
        # Setup trade log handler (separate file for trade records)
        self._setup_trade_log_handler(root_logger)
        
        # Setup error log handler
        self._setup_error_log_handler(root_logger)
        
        # Log startup message
        logging.info("Logging system initialized successfully")
        logging.info(f"Log level: {self.log_config.get('level', 'INFO')}")
        logging.info(f"Log file: {self.log_config.get('file_path', 'logs/trading.log')}")
    
    def _setup_console_handler(self, logger: logging.Logger, level: int):
        """Setup colored console logging"""
        try:
            console_handler = colorlog.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            # Color formatter
            color_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                reset=True,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
                secondary_log_colors={},
                style='%'
            )
            
            console_handler.setFormatter(color_formatter)
            logger.addHandler(console_handler)
            
        except Exception as e:
            # Fallback to basic console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    
    def _setup_file_handler(self, logger: logging.Logger, level: int):
        """Setup file logging with rotation"""
        try:
            log_file = self.log_config.get('file_path', 'logs/trading.log')
            max_bytes = self._parse_size(self.log_config.get('max_file_size', '10MB'))
            backup_count = self.log_config.get('backup_count', 5)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            
            # File formatter (more detailed)
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logging.error(f"Failed to setup file handler: {e}")
    
    def _setup_trade_log_handler(self, logger: logging.Logger):
        """Setup separate handler for trade records"""
        try:
            trade_log_file = 'logs/trades.log'
            
            trade_handler = logging.handlers.RotatingFileHandler(
                trade_log_file,
                maxBytes=self._parse_size('50MB'),
                backupCount=10,
                encoding='utf-8'
            )
            trade_handler.setLevel(logging.INFO)
            
            # Trade formatter (JSON format for easy parsing)
            trade_formatter = logging.Formatter(
                '%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            trade_handler.setFormatter(trade_formatter)
            
            # Create trade logger
            trade_logger = logging.getLogger('trade_logger')
            trade_logger.addHandler(trade_handler)
            trade_logger.setLevel(logging.INFO)
            trade_logger.propagate = False  # Don't propagate to root logger
            
        except Exception as e:
            logging.error(f"Failed to setup trade log handler: {e}")
    
    def _setup_error_log_handler(self, logger: logging.Logger):
        """Setup separate handler for errors"""
        try:
            error_log_file = 'logs/errors.log'
            
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self._parse_size('20MB'),
                backupCount=5,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            
            # Error formatter (detailed)
            error_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s()\n'
                'Error: %(message)s\n'
                '%(pathname)s:%(lineno)d\n'
                '%(exc_info)s\n' + '-' * 80,
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            error_handler.setFormatter(error_formatter)
            logger.addHandler(error_handler)
            
        except Exception as e:
            logging.error(f"Failed to setup error log handler: {e}")
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        size_str = size_str.upper()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)  # Assume bytes
    
    @staticmethod
    def log_trade(trade_data: Dict):
        """Log trade information to separate trade log"""
        try:
            trade_logger = logging.getLogger('trade_logger')
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'type': 'TRADE',
                'data': trade_data
            }
            trade_logger.info(json.dumps(trade_record))
            
        except Exception as e:
            logging.error(f"Failed to log trade data: {e}")
    
    @staticmethod
    def log_signal(signal_data: Dict):
        """Log trading signal information"""
        try:
            trade_logger = logging.getLogger('trade_logger')
            signal_record = {
                'timestamp': datetime.now().isoformat(),
                'type': 'SIGNAL',
                'data': signal_data
            }
            trade_logger.info(json.dumps(signal_record))
            
        except Exception as e:
            logging.error(f"Failed to log signal data: {e}")
    
    @staticmethod
    def log_market_data(market_data: Dict):
        """Log market data for analysis"""
        try:
            trade_logger = logging.getLogger('trade_logger')
            market_record = {
                'timestamp': datetime.now().isoformat(),
                'type': 'MARKET_DATA',
                'data': market_data
            }
            trade_logger.info(json.dumps(market_record))
            
        except Exception as e:
            logging.error(f"Failed to log market data: {e}")
    
    @staticmethod
    def log_performance(performance_data: Dict):
        """Log performance metrics"""
        try:
            trade_logger = logging.getLogger('trade_logger')
            performance_record = {
                'timestamp': datetime.now().isoformat(),
                'type': 'PERFORMANCE',
                'data': performance_data
            }
            trade_logger.info(json.dumps(performance_record))
            
        except Exception as e:
            logging.error(f"Failed to log performance data: {e}")

class ContextLogger:
    """Context manager for logging function execution"""
    
    def __init__(self, logger: logging.Logger, function_name: str, level: int = logging.INFO):
        self.logger = logger
        self.function_name = function_name
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"Starting {self.function_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = datetime.now() - self.start_time
        
        if exc_type is None:
            self.logger.log(self.level, f"Completed {self.function_name} in {execution_time}")
        else:
            self.logger.error(f"Failed {self.function_name} after {execution_time}: {exc_val}")
        
        return False  # Don't suppress exceptions

def log_function_call(logger: Optional[logging.Logger] = None, level: int = logging.INFO):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = logger or logging.getLogger(func.__module__)
            
            with ContextLogger(func_logger, func.__name__, level):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

def setup_logging(config: Dict):
    """Setup logging system with given configuration"""
    trading_logger = TradingLogger(config)
    return trading_logger

# Convenience functions for structured logging
def log_trade_execution(symbol: str, entry_price: float, quantity: int, order_id: str):
    """Log trade execution"""
    TradingLogger.log_trade({
        'action': 'ENTRY',
        'symbol': symbol,
        'price': entry_price,
        'quantity': quantity,
        'order_id': order_id
    })

def log_trade_exit(symbol: str, exit_price: float, pnl: float, pnl_percent: float):
    """Log trade exit"""
    TradingLogger.log_trade({
        'action': 'EXIT',
        'symbol': symbol,
        'price': exit_price,
        'pnl': pnl,
        'pnl_percent': pnl_percent
    })

def log_strategy_signal(symbol: str, pcr: float, strike_price: float, confidence: float):
    """Log strategy signal generation"""
    TradingLogger.log_signal({
        'symbol': symbol,
        'pcr': pcr,
        'strike_price': strike_price,
        'confidence': confidence
    })

def log_market_scan(gainers_count: int, top_gainer: str, vix: Optional[float] = None):
    """Log market scan results"""
    TradingLogger.log_market_data({
        'scan_type': 'PRE_MARKET',
        'gainers_count': gainers_count,
        'top_gainer': top_gainer,
        'vix': vix
    })