"""
Advanced risk management system with multiple safety checks
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import deque

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    BLOCKED = "BLOCKED"


@dataclass
class Position:
    """Position information"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    entry_time: datetime
    position_type: str  # 'CALL' or 'PUT'
    strike_price: float
    expiry_date: datetime
    
    @property
    def pnl(self) -> float:
        """Calculate current P&L"""
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def pnl_percent(self) -> float:
        """Calculate P&L percentage"""
        if self.entry_price == 0:
            return 0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100
    
    @property
    def position_value(self) -> float:
        """Current position value"""
        return self.current_price * self.quantity
    
    @property
    def holding_duration(self) -> timedelta:
        """Time held"""
        return datetime.now() - self.entry_time


@dataclass
class TradeRecord:
    """Historical trade record"""
    symbol: str
    entry_price: float
    exit_price: float
    quantity: int
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_percent: float
    exit_reason: str


@dataclass
class RiskMetrics:
    """Current risk metrics"""
    current_risk_level: RiskLevel
    total_exposure: float
    daily_pnl: float
    daily_pnl_percent: float
    open_positions_count: int
    consecutive_losses: int
    daily_trades_count: int
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    avg_win: float
    avg_loss: float
    risk_reward_ratio: float
    correlation_risk: float
    vix_level: float
    market_risk_score: float
    can_trade: bool
    blocked_reasons: List[str] = field(default_factory=list)


class RiskManager:
    """Advanced risk management system"""
    
    def __init__(self, config: Dict, initial_capital: float):
        self.config = config
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Risk parameters
        self.max_daily_loss_percent = config.get('max_daily_loss_percent', 2.0)
        self.max_position_size_percent = config.get('max_position_size_percent', 5.0)
        self.max_daily_trades = config.get('max_daily_trades', 3)
        self.max_open_positions = config.get('max_open_positions', 2)
        self.consecutive_loss_limit = config.get('consecutive_loss_limit', 3)
        self.stop_loss_percent = config.get('stop_loss_percent', 30.0)
        self.max_vix_threshold = config.get('max_vix_threshold', 25.0)
        self.min_liquidity_score = config.get('min_liquidity_score', 0.7)
        
        # State tracking
        self.positions: Dict[str, Position] = {}
        self.today_trades: List[TradeRecord] = []
        self.historical_trades: deque = deque(maxlen=1000)
        self.consecutive_losses = 0
        self.daily_pnl = 0.0
        self.errors_today = 0
        self.last_trade_time = None
        self.trading_day_start = None
        
        # Risk tracking
        self.risk_events: List[Dict] = []
        self.blocked_until = None
        self.emergency_stop = False
    
    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        volatility: float,
        lot_size: int
    ) -> Tuple[int, float]:
        """
        Calculate optimal position size using Kelly Criterion and risk limits
        
        Returns:
            Tuple of (quantity, position_value)
        """
        # Maximum risk per trade
        max_risk_amount = self.current_capital * (self.max_position_size_percent / 100)
        
        # Kelly Criterion (simplified)
        win_rate = self._calculate_win_rate()
        avg_win_loss_ratio = self._calculate_avg_win_loss_ratio()
        
        if win_rate > 0 and avg_win_loss_ratio > 0:
            kelly_fraction = (win_rate * avg_win_loss_ratio - (1 - win_rate)) / avg_win_loss_ratio
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        else:
            kelly_fraction = 0.02  # Default 2% for new system
        
        # Volatility adjustment
        volatility_multiplier = max(0.5, min(1.5, 20 / volatility)) if volatility > 0 else 1.0
        
        # Calculate position size
        position_value = self.current_capital * kelly_fraction * volatility_multiplier
        position_value = min(position_value, max_risk_amount)
        
        # Convert to lots
        quantity = int(position_value / (entry_price * lot_size)) * lot_size
        quantity = max(lot_size, min(quantity, self.config.get('max_lots_per_trade', 2) * lot_size))
        
        actual_position_value = quantity * entry_price
        
        logger.info(f"Position size calculated: {quantity} units, Value: {actual_position_value:.2f}")
        
        return quantity, actual_position_value
    
    def check_pre_trade_risk(
        self,
        symbol: str,
        position_value: float,
        current_vix: float,
        liquidity_score: float
    ) -> Tuple[bool, List[str]]:
        """
        Comprehensive pre-trade risk check
        
        Returns:
            Tuple of (can_trade, reasons_if_blocked)
        """
        blocked_reasons = []
        
        # Emergency stop check
        if self.emergency_stop:
            blocked_reasons.append("Emergency stop activated")
        
        # Time-based block check
        if self.blocked_until and datetime.now() < self.blocked_until:
            blocked_reasons.append(f"Trading blocked until {self.blocked_until}")
        
        # Daily loss limit
        daily_loss_percent = abs(self.daily_pnl / self.initial_capital * 100)
        if daily_loss_percent >= self.max_daily_loss_percent:
            blocked_reasons.append(f"Daily loss limit reached ({daily_loss_percent:.1f}%)")
        
        # Consecutive losses
        if self.consecutive_losses >= self.consecutive_loss_limit:
            blocked_reasons.append(f"Consecutive loss limit reached ({self.consecutive_losses})")
        
        # Daily trade limit
        if len(self.today_trades) >= self.max_daily_trades:
            blocked_reasons.append(f"Daily trade limit reached ({len(self.today_trades)})")
        
        # Open positions limit
        if len(self.positions) >= self.max_open_positions:
            blocked_reasons.append(f"Open position limit reached ({len(self.positions)})")
        
        # Position size check
        max_position = self.current_capital * (self.max_position_size_percent / 100)
        if position_value > max_position:
            blocked_reasons.append(f"Position too large ({position_value:.0f} > {max_position:.0f})")
        
        # Market volatility check
        if current_vix > self.max_vix_threshold:
            blocked_reasons.append(f"VIX too high ({current_vix:.1f} > {self.max_vix_threshold})")
        
        # Liquidity check
        if liquidity_score < self.min_liquidity_score:
            blocked_reasons.append(f"Insufficient liquidity (score: {liquidity_score:.2f})")
        
        # Capital preservation check
        if self.current_capital < self.initial_capital * 0.8:
            blocked_reasons.append("Capital preservation mode (80% threshold)")
        
        # Time spacing check (avoid rapid trades)
        if self.last_trade_time:
            time_since_last = (datetime.now() - self.last_trade_time).seconds
            if time_since_last < 60:  # Minimum 1 minute between trades
                blocked_reasons.append(f"Too soon after last trade ({time_since_last}s)")
        
        can_trade = len(blocked_reasons) == 0
        
        if not can_trade:
            logger.warning(f"Trade blocked for {symbol}: {', '.join(blocked_reasons)}")
        
        return can_trade, blocked_reasons
    
    def add_position(self, position: Position) -> bool:
        """Add new position with risk checks"""
        if position.symbol in self.positions:
            logger.error(f"Position already exists for {position.symbol}")
            return False
        
        self.positions[position.symbol] = position
        self.last_trade_time = datetime.now()
        
        logger.info(f"Position added: {position.symbol} @ {position.entry_price}")
        return True
    
    def update_position_price(self, symbol: str, current_price: float):
        """Update position with current price"""
        if symbol in self.positions:
            self.positions[symbol].current_price = current_price
    
    def check_stop_loss(self, symbol: str) -> bool:
        """Check if position hit stop loss"""
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        loss_percent = abs(position.pnl_percent)
        
        return loss_percent >= self.stop_loss_percent
    
    def check_trailing_stop(self, symbol: str, highest_price: float) -> bool:
        """Check trailing stop loss"""
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        
        # Trailing stop activates after 5% profit
        if position.pnl_percent > 5:
            drawdown_from_high = ((highest_price - position.current_price) / highest_price) * 100
            return drawdown_from_high > 3  # 3% trailing stop
        
        return False
    
    def close_position(
        self,
        symbol: str,
        exit_price: float,
        exit_reason: str
    ) -> Optional[TradeRecord]:
        """Close position and record trade"""
        if symbol not in self.positions:
            logger.error(f"No position found for {symbol}")
            return None
        
        position = self.positions[symbol]
        pnl = (exit_price - position.entry_price) * position.quantity
        pnl_percent = ((exit_price - position.entry_price) / position.entry_price) * 100
        
        # Create trade record
        trade = TradeRecord(
            symbol=symbol,
            entry_price=position.entry_price,
            exit_price=exit_price,
            quantity=position.quantity,
            entry_time=position.entry_time,
            exit_time=datetime.now(),
            pnl=pnl,
            pnl_percent=pnl_percent,
            exit_reason=exit_reason
        )
        
        # Update tracking
        self.today_trades.append(trade)
        self.historical_trades.append(trade)
        self.daily_pnl += pnl
        self.current_capital += pnl
        
        # Update consecutive losses
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Remove position
        del self.positions[symbol]
        
        logger.info(
            f"Position closed: {symbol} @ {exit_price:.2f}, "
            f"PnL: {pnl:.2f} ({pnl_percent:.2f}%), Reason: {exit_reason}"
        )
        
        # Check for circuit breakers
        self._check_circuit_breakers()
        
        return trade
    
    def get_risk_metrics(self, current_vix: float = 0) -> RiskMetrics:
        """Calculate current risk metrics"""
        total_exposure = sum(p.position_value for p in self.positions.values())
        daily_pnl_percent = (self.daily_pnl / self.initial_capital) * 100
        
        # Calculate statistics
        win_rate = self._calculate_win_rate()
        avg_win, avg_loss = self._calculate_avg_win_loss()
        risk_reward_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Determine risk level
        risk_level = self._calculate_risk_level(daily_pnl_percent, current_vix)
        
        # Check if trading allowed
        can_trade, blocked_reasons = self._can_trade_now()
        
        return RiskMetrics(
            current_risk_level=risk_level,
            total_exposure=total_exposure,
            daily_pnl=self.daily_pnl,
            daily_pnl_percent=daily_pnl_percent,
            open_positions_count=len(self.positions),
            consecutive_losses=self.consecutive_losses,
            daily_trades_count=len(self.today_trades),
            max_drawdown=self._calculate_max_drawdown(),
            sharpe_ratio=self._calculate_sharpe_ratio(),
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            risk_reward_ratio=risk_reward_ratio,
            correlation_risk=self._calculate_correlation_risk(),
            vix_level=current_vix,
            market_risk_score=self._calculate_market_risk_score(current_vix),
            can_trade=can_trade,
            blocked_reasons=blocked_reasons
        )
    
    def reset_daily_metrics(self):
        """Reset daily metrics at start of trading day"""
        self.today_trades.clear()
        self.daily_pnl = 0.0
        self.errors_today = 0
        self.trading_day_start = datetime.now()
        logger.info("Daily risk metrics reset")
    
    def emergency_stop_trading(self, reason: str):
        """Activate emergency stop"""
        self.emergency_stop = True
        self.blocked_until = datetime.now() + timedelta(hours=24)
        
        logger.critical(f"EMERGENCY STOP ACTIVATED: {reason}")
        
        # Record risk event
        self.risk_events.append({
            'timestamp': datetime.now(),
            'type': 'EMERGENCY_STOP',
            'reason': reason
        })
    
    def _calculate_win_rate(self) -> float:
        """Calculate win rate from historical trades"""
        if not self.historical_trades:
            return 0.5  # Default 50%
        
        wins = sum(1 for trade in self.historical_trades if trade.pnl > 0)
        return wins / len(self.historical_trades)
    
    def _calculate_avg_win_loss(self) -> Tuple[float, float]:
        """Calculate average win and loss amounts"""
        if not self.historical_trades:
            return 0.0, 0.0
        
        wins = [t.pnl for t in self.historical_trades if t.pnl > 0]
        losses = [t.pnl for t in self.historical_trades if t.pnl < 0]
        
        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        
        return avg_win, avg_loss
    
    def _calculate_avg_win_loss_ratio(self) -> float:
        """Calculate average win/loss ratio"""
        avg_win, avg_loss = self._calculate_avg_win_loss()
        
        if avg_loss == 0:
            return 1.0
        
        return abs(avg_win / avg_loss)
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.historical_trades:
            return 0.0
        
        cumulative_pnl = []
        running_pnl = 0
        
        for trade in self.historical_trades:
            running_pnl += trade.pnl
            cumulative_pnl.append(running_pnl)
        
        if not cumulative_pnl:
            return 0.0
        
        peak = cumulative_pnl[0]
        max_dd = 0
        
        for pnl in cumulative_pnl:
            if pnl > peak:
                peak = pnl
            drawdown = (peak - pnl) / self.initial_capital * 100 if peak > 0 else 0
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio"""
        if len(self.historical_trades) < 10:
            return 0.0
        
        returns = [t.pnl_percent for t in self.historical_trades]
        
        if not returns:
            return 0.0
        
        avg_return = sum(returns) / len(returns)
        
        if len(returns) > 1:
            variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
            std_dev = variance ** 0.5
            
            if std_dev > 0:
                return (avg_return / std_dev) * (252 ** 0.5)  # Annualized
        
        return 0.0
    
    def _calculate_correlation_risk(self) -> float:
        """Calculate portfolio correlation risk"""
        if len(self.positions) < 2:
            return 0.0
        
        # Simplified correlation risk based on similar symbols
        # In production, use actual price correlation
        return min(len(self.positions) * 0.2, 1.0)
    
    def _calculate_market_risk_score(self, vix: float) -> float:
        """Calculate overall market risk score (0-100)"""
        vix_score = min(vix / 50 * 100, 100) if vix > 0 else 50
        
        # Add other market indicators here
        return vix_score
    
    def _calculate_risk_level(self, daily_pnl_percent: float, vix: float) -> RiskLevel:
        """Determine current risk level"""
        if self.emergency_stop:
            return RiskLevel.BLOCKED
        
        if abs(daily_pnl_percent) > self.max_daily_loss_percent * 0.8:
            return RiskLevel.CRITICAL
        
        if vix > self.max_vix_threshold * 0.9:
            return RiskLevel.HIGH
        
        if self.consecutive_losses >= 2:
            return RiskLevel.HIGH
        
        if len(self.positions) >= self.max_open_positions * 0.8:
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _can_trade_now(self) -> Tuple[bool, List[str]]:
        """Check if trading is currently allowed"""
        blocked_reasons = []
        
        if self.emergency_stop:
            blocked_reasons.append("Emergency stop active")
        
        if self.blocked_until and datetime.now() < self.blocked_until:
            blocked_reasons.append(f"Blocked until {self.blocked_until}")
        
        if abs(self.daily_pnl / self.initial_capital * 100) >= self.max_daily_loss_percent:
            blocked_reasons.append("Daily loss limit reached")
        
        if self.consecutive_losses >= self.consecutive_loss_limit:
            blocked_reasons.append("Consecutive loss limit reached")
        
        return len(blocked_reasons) == 0, blocked_reasons
    
    def _check_circuit_breakers(self):
        """Check and activate circuit breakers if needed"""
        # Daily loss circuit breaker
        if abs(self.daily_pnl / self.initial_capital * 100) >= self.max_daily_loss_percent:
            self.blocked_until = datetime.now().replace(
                hour=23, minute=59, second=59
            )
            logger.warning("Daily loss circuit breaker activated")
        
        # Consecutive loss circuit breaker
        if self.consecutive_losses >= self.consecutive_loss_limit:
            self.blocked_until = datetime.now() + timedelta(hours=2)
            logger.warning("Consecutive loss circuit breaker activated")
        
        # Capital preservation circuit breaker
        if self.current_capital < self.initial_capital * 0.7:
            self.emergency_stop_trading("Capital preservation threshold breached (70%)")