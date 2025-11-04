"""
Configuration management system
Handles loading and validation of configuration files
"""

import yaml
import os
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: str = "config/config.yaml", env_path: str = ".env"):
        self.config_path = config_path
        self.env_path = env_path
        self.config = {}
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file and environment variables"""
        try:
            # Load environment variables
            if os.path.exists(self.env_path):
                load_dotenv(self.env_path)
                logger.info(f"Loaded environment variables from {self.env_path}")
            
            # Load YAML configuration
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    self.config = yaml.safe_load(file)
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                self.config = self._get_default_config()
            
            # Override with environment variables
            self._override_with_env_vars()
            
            # Validate configuration
            self._validate_config()
            
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _override_with_env_vars(self):
        """Override configuration with environment variables"""
        try:
            # Broker configuration
            if 'broker' not in self.config:
                self.config['broker'] = {}
            
            # Zerodha credentials
            if os.getenv('ZERODHA_API_KEY'):
                self.config['broker']['api_key'] = os.getenv('ZERODHA_API_KEY')
            if os.getenv('ZERODHA_API_SECRET'):
                self.config['broker']['api_secret'] = os.getenv('ZERODHA_API_SECRET')
            if os.getenv('ZERODHA_ACCESS_TOKEN'):
                self.config['broker']['access_token'] = os.getenv('ZERODHA_ACCESS_TOKEN')
            
            # Upstox credentials
            if os.getenv('UPSTOX_API_KEY'):
                self.config['broker']['api_key'] = os.getenv('UPSTOX_API_KEY')
            if os.getenv('UPSTOX_API_SECRET'):
                self.config['broker']['api_secret'] = os.getenv('UPSTOX_API_SECRET')
            if os.getenv('UPSTOX_ACCESS_TOKEN'):
                self.config['broker']['access_token'] = os.getenv('UPSTOX_ACCESS_TOKEN')
            
            # Telegram configuration
            if 'notifications' not in self.config:
                self.config['notifications'] = {'telegram': {}, 'email': {}}
            
            if os.getenv('TELEGRAM_BOT_TOKEN'):
                self.config['notifications']['telegram']['bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN')
            if os.getenv('TELEGRAM_CHAT_ID'):
                self.config['notifications']['telegram']['chat_id'] = os.getenv('TELEGRAM_CHAT_ID')
            
            # Email configuration
            if os.getenv('EMAIL_ADDRESS'):
                self.config['notifications']['email']['email'] = os.getenv('EMAIL_ADDRESS')
            if os.getenv('EMAIL_PASSWORD'):
                self.config['notifications']['email']['password'] = os.getenv('EMAIL_PASSWORD')
            if os.getenv('EMAIL_RECIPIENT'):
                self.config['notifications']['email']['recipient'] = os.getenv('EMAIL_RECIPIENT')
            
            # Environment setting
            if os.getenv('ENVIRONMENT'):
                self.config['environment'] = os.getenv('ENVIRONMENT')
            
            # Log level
            if os.getenv('LOG_LEVEL'):
                if 'logging' not in self.config:
                    self.config['logging'] = {}
                self.config['logging']['level'] = os.getenv('LOG_LEVEL')
            
        except Exception as e:
            logger.error(f"Error overriding with environment variables: {e}")
    
    def _validate_config(self):
        """Validate configuration parameters"""
        try:
            # Validate trading parameters
            trading_config = self.config.get('trading', {})
            
            pcr_min = trading_config.get('pcr_min_range', 0.7)
            pcr_max = trading_config.get('pcr_max_range', 1.5)
            
            if pcr_min >= pcr_max:
                raise ValueError("pcr_min_range must be less than pcr_max_range")
            
            if pcr_min < 0 or pcr_max < 0:
                raise ValueError("PCR range values must be positive")
            
            profit_target = trading_config.get('profit_target_percent', 8.0)
            if profit_target <= 0:
                raise ValueError("profit_target_percent must be positive")
            
            # Validate broker configuration
            broker_config = self.config.get('broker', {})
            if not broker_config.get('paper_trading', True):
                # Real trading requires credentials
                required_fields = ['api_key', 'api_secret']
                for field in required_fields:
                    if not broker_config.get(field):
                        logger.warning(f"Missing broker credential: {field}")
            
            # Validate notification configuration
            notifications = self.config.get('notifications', {})
            
            # Telegram validation
            telegram_config = notifications.get('telegram', {})
            if telegram_config.get('enabled', False):
                if not telegram_config.get('bot_token') or not telegram_config.get('chat_id'):
                    logger.warning("Telegram enabled but missing bot_token or chat_id")
                    self.config['notifications']['telegram']['enabled'] = False
            
            # Email validation
            email_config = notifications.get('email', {})
            if email_config.get('enabled', False):
                required_email_fields = ['email', 'password', 'recipient']
                for field in required_email_fields:
                    if not email_config.get(field):
                        logger.warning(f"Email enabled but missing field: {field}")
                        self.config['notifications']['email']['enabled'] = False
                        break
            
            logger.info("Configuration validation completed successfully")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file doesn't exist"""
        return {
            'trading': {
                'max_amount_per_trade': 1,
                'pcr_min_range': 0.7,
                'pcr_max_range': 1.5,
                'profit_target_percent': 8.0,
                'execution_time': '09:15:00',
                'pre_market_scan_time': '09:14:00',
                'timezone': 'Asia/Kolkata'
            },
            'broker': {
                'name': 'zerodha',
                'paper_trading': True
            },
            'data': {
                'use_free_apis': True
            },
            'risk': {
                'max_daily_trades': 1,
                'trading_holidays_check': True,
                'market_volatility_filter': True,
                'volatility_threshold': 25.0
            },
            'notifications': {
                'telegram': {'enabled': False},
                'email': {'enabled': False}
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'logs/trading.log'
            },
            'backtesting': {
                'enabled': True,
                'initial_capital': 100000
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)"""
        try:
            keys = key.split('.')
            config_ref = self.config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config_ref:
                    config_ref[k] = {}
                config_ref = config_ref[k]
            
            # Set the value
            config_ref[keys[-1]] = value
            
        except Exception as e:
            logger.error(f"Failed to set config key {key}: {e}")
    
    def save_config(self, path: Optional[str] = None):
        """Save current configuration to file"""
        try:
            save_path = path or self.config_path
            
            with open(save_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading-specific configuration"""
        return self.config.get('trading', {})
    
    def get_broker_config(self) -> Dict[str, Any]:
        """Get broker-specific configuration"""
        return self.config.get('broker', {})
    
    def get_notification_config(self) -> Dict[str, Any]:
        """Get notification-specific configuration"""
        return self.config.get('notifications', {})
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration"""
        return self.config.get('risk', {})
    
    def is_paper_trading(self) -> bool:
        """Check if paper trading is enabled"""
        return self.config.get('broker', {}).get('paper_trading', True)
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.config.get('environment', 'development') == 'production'