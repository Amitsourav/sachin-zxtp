"""
Core configuration management with validation and type safety
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from pathlib import Path
from datetime import time
import json
import yaml

class TradingConfig(BaseModel):
    """Trading strategy configuration"""
    
    # Capital and mode
    mode: str = Field("paper", description="Trading mode: paper or live")
    capital: float = Field(100000, ge=10000, description="Trading capital")
    use_live_data: bool = Field(True, description="Use live market data for paper trading")
    
    # Strategy parameters
    pcr_min: float = Field(0.7, ge=0.1, le=5.0, description="Minimum PCR value")
    pcr_max: float = Field(1.5, ge=0.1, le=5.0, description="Maximum PCR value")
    profit_target_percent: float = Field(8.0, ge=1.0, le=50.0, description="Profit target percentage")
    stop_loss_percent: float = Field(30.0, ge=5.0, le=50.0, description="Stop loss percentage")
    strict_pcr_check: bool = Field(False, description="Strict PCR validation")
    
    # Timing configuration
    scan_time: str = Field("09:14:00", description="Pre-market scan time")
    entry_time: str = Field("09:17:00", description="Trade entry time (after market settles)")
    exit_time: str = Field("15:20:00", description="Force exit time")
    
    # Position sizing
    max_position_size_percent: float = Field(5.0, ge=1.0, le=20.0, description="Max position size as % of capital")
    max_lots_per_trade: int = Field(2, ge=1, le=10, description="Maximum lots per trade")
    
    @validator('pcr_max')
    def validate_pcr_range(cls, v, values):
        if 'pcr_min' in values and v <= values['pcr_min']:
            raise ValueError('pcr_max must be greater than pcr_min')
        return v


class RiskConfig(BaseModel):
    """Risk management configuration"""
    
    max_risk_per_trade: float = Field(2.0, ge=0.5, le=10.0, description="Max risk per trade as % of capital")
    max_daily_loss: float = Field(5000, ge=1000, description="Max daily loss in rupees")
    max_positions: int = Field(1, ge=1, le=5, description="Max concurrent positions")
    stop_loss_enabled: bool = Field(True, description="Enable stop loss")
    trailing_stop_enabled: bool = Field(False, description="Enable trailing stop loss")
    circuit_breaker_enabled: bool = Field(True, description="Enable circuit breaker")
    circuit_breaker_threshold: int = Field(3, ge=1, le=10, description="Stop after N consecutive losses")
    
    # Legacy fields for compatibility
    max_daily_loss_percent: float = Field(2.0, ge=0.5, le=10.0, description="Max daily loss as % of capital")
    max_daily_trades: int = Field(2, ge=1, le=10, description="Maximum trades per day")
    max_open_positions: int = Field(1, ge=1, le=5, description="Max concurrent positions")
    
    # Market conditions
    min_market_cap_cr: float = Field(10000, ge=1000, description="Minimum market cap in crores")
    min_volume: int = Field(100000, ge=1000, description="Minimum daily volume")
    max_vix_threshold: float = Field(22.0, ge=10.0, le=50.0, description="Maximum VIX for trading")
    
    # Liquidity checks
    min_open_interest: int = Field(500, ge=100, description="Minimum open interest in contracts")
    max_bid_ask_spread_percent: float = Field(2.0, ge=0.1, le=5.0, description="Maximum bid-ask spread")
    
    # Circuit breakers
    consecutive_loss_limit: int = Field(3, ge=1, le=10, description="Stop after N consecutive losses")
    daily_error_limit: int = Field(5, ge=1, le=20, description="Max technical errors per day")


class BrokerConfig(BaseModel):
    """Broker configuration"""
    
    name: str = Field("zerodha", description="Broker name")
    api_key: Optional[str] = Field(None, description="API key")
    api_secret: Optional[str] = Field(None, description="API secret")
    access_token: Optional[str] = Field(None, description="Access token")
    
    # Execution settings
    order_type: str = Field("LIMIT", description="Order type: MARKET or LIMIT")
    product_type: str = Field("MIS", description="Product type: MIS, CNC, NRML")
    
    # Paper trading
    paper_trading: bool = Field(True, description="Enable paper trading mode")
    paper_trading_capital: float = Field(100000, ge=10000, description="Paper trading capital")


class DataConfig(BaseModel):
    """Data source configuration"""
    
    primary_source: str = Field("yfinance", description="Primary data source")
    backup_sources: List[str] = Field(["nsepy", "alpha_vantage"], description="Backup data sources")
    
    # Data validation
    max_data_age_seconds: int = Field(60, ge=10, le=300, description="Maximum age of data in seconds")
    retry_count: int = Field(3, ge=1, le=10, description="Number of retries for failed requests")
    retry_delay_seconds: int = Field(2, ge=1, le=30, description="Delay between retries")
    
    # Caching
    enable_cache: bool = Field(True, description="Enable data caching")
    cache_ttl_seconds: int = Field(300, ge=60, le=3600, description="Cache time-to-live")


class NotificationConfig(BaseModel):
    """Notification configuration"""
    
    telegram_enabled: bool = Field(False, description="Enable Telegram notifications")
    telegram_bot_token: Optional[str] = Field(None, description="Telegram bot token")
    telegram_chat_id: Optional[str] = Field(None, description="Telegram chat ID")
    
    email_enabled: bool = Field(False, description="Enable email notifications")
    email_smtp_host: Optional[str] = Field("smtp.gmail.com", description="SMTP server host")
    email_smtp_port: int = Field(587, description="SMTP server port")
    email_username: Optional[str] = Field(None, description="Email username")
    email_password: Optional[str] = Field(None, description="Email password")
    email_recipient: Optional[str] = Field(None, description="Email recipient")
    
    # Notification levels
    notify_on_trade: bool = Field(True, description="Notify on trade execution")
    notify_on_pnl: bool = Field(True, description="Notify on P&L updates")
    notify_on_error: bool = Field(True, description="Notify on errors")
    notify_on_daily_summary: bool = Field(True, description="Send daily summary")


class LoggingConfig(BaseModel):
    """Logging configuration"""
    
    level: str = Field("INFO", description="Logging level")
    format: str = Field(
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
        description="Log format"
    )
    
    # File logging
    file_enabled: bool = Field(True, description="Enable file logging")
    file_path: Path = Field(Path("logs/trading.log"), description="Log file path")
    file_rotation: str = Field("1 day", description="Log rotation period")
    file_retention: str = Field("30 days", description="Log retention period")
    
    # Console logging
    console_enabled: bool = Field(True, description="Enable console logging")
    console_colorize: bool = Field(True, description="Colorize console output")


class Settings(BaseSettings):
    """Main application settings"""
    
    # Environment
    environment: str = Field("development", description="Environment: development, staging, production")
    debug: bool = Field(False, description="Debug mode")
    
    # Component configurations
    trading: TradingConfig = Field(default_factory=TradingConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    broker: BrokerConfig = Field(default_factory=BrokerConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Database
    database_url: str = Field("sqlite:///./data/trading.db", description="Database URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "Settings":
        """Load settings from YAML file"""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_path: Path) -> "Settings":
        """Load settings from JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def save_yaml(self, yaml_path: Path):
        """Save settings to YAML file"""
        with open(yaml_path, 'w') as f:
            yaml.dump(self.dict(), f, default_flow_style=False)
    
    def save_json(self, json_path: Path):
        """Save settings to JSON file"""
        with open(json_path, 'w') as f:
            json.dump(self.dict(), f, indent=2)
    
    def validate_for_production(self) -> List[str]:
        """Validate settings for production use"""
        errors = []
        
        if self.broker.paper_trading and self.environment == "production":
            errors.append("Paper trading should be disabled in production")
        
        if not self.broker.api_key and not self.broker.paper_trading:
            errors.append("Broker API key is required for live trading")
        
        if self.risk.stop_loss_percent > 50:
            errors.append("Stop loss percentage is too high (>50%)")
        
        if self.trading.profit_target_percent < self.risk.stop_loss_percent / 3:
            errors.append("Risk-reward ratio is unfavorable")
        
        if self.notifications.notify_on_error and not (
            self.notifications.telegram_enabled or self.notifications.email_enabled
        ):
            errors.append("Error notifications enabled but no notification channel configured")
        
        return errors


# Singleton instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get or create settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def load_settings(config_path: Optional[Path] = None) -> Settings:
    """Load settings from file or environment"""
    global _settings
    
    if config_path:
        if config_path.suffix == '.yaml':
            _settings = Settings.from_yaml(config_path)
        elif config_path.suffix == '.json':
            _settings = Settings.from_json(config_path)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    else:
        _settings = Settings()
    
    # Validate for production if needed
    if _settings.environment == "production":
        errors = _settings.validate_for_production()
        if errors:
            raise ValueError(f"Production validation failed: {'; '.join(errors)}")
    
    return _settings


class ConfigManager:
    """Simple config manager wrapper for backward compatibility"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        self.config_path = Path(config_path)
        if self.config_path.exists():
            self.settings = load_settings(self.config_path)
        else:
            # Create default config if it doesn't exist
            self.settings = Settings()
            # Create config directory
            self.config_path.parent.mkdir(exist_ok=True)
            # Save default config
            self.settings.save_yaml(self.config_path)
    
    @property
    def trading(self):
        return self.settings.trading
    
    @property
    def risk(self):
        return self.settings.risk
    
    @property
    def broker(self):
        return self.settings.broker
    
    @property
    def data(self):
        return self.settings.data
    
    @property
    def notifications(self):
        return self.settings.notifications
    
    @property
    def logging(self):
        return self.settings.logging
    
    def get(self, key, default=None):
        """Get value from settings with default"""
        try:
            parts = key.split('.')
            value = self.settings
            for part in parts:
                value = getattr(value, part)
            return value
        except (AttributeError, KeyError):
            return default