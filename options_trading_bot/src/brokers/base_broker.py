"""
Abstract base broker interface and factory pattern
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import asyncio
from decimal import Decimal

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order types"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"


class OrderStatus(Enum):
    """Order status"""
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class PositionType(Enum):
    """Position types"""
    LONG = "LONG"
    SHORT = "SHORT"


class ProductType(Enum):
    """Product types for Indian markets"""
    MIS = "MIS"  # Intraday
    CNC = "CNC"  # Delivery
    NRML = "NRML"  # Normal (F&O)


@dataclass
class Order:
    """Order details"""
    order_id: str
    symbol: str
    quantity: int
    order_type: OrderType
    side: str  # BUY or SELL
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    product_type: ProductType = ProductType.MIS
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    average_price: float = 0.0
    placed_time: Optional[datetime] = None
    filled_time: Optional[datetime] = None
    exchange_order_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        return self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]
    
    @property
    def is_active(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]
    
    @property
    def fill_percentage(self) -> float:
        if self.quantity == 0:
            return 0
        return (self.filled_quantity / self.quantity) * 100


@dataclass
class Position:
    """Position details"""
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    product_type: ProductType
    exchange: str
    
    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        return self.quantity * self.average_price


@dataclass
class BrokerAccount:
    """Broker account details"""
    account_id: str
    broker_name: str
    total_capital: float
    available_margin: float
    used_margin: float
    positions_value: float
    pnl_today: float
    pnl_total: float
    
    @property
    def margin_utilization(self) -> float:
        if self.total_capital == 0:
            return 0
        return (self.used_margin / self.total_capital) * 100


class BaseBroker(ABC):
    """Abstract base class for all brokers"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.is_connected = False
        self.account: Optional[BrokerAccount] = None
        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to broker API"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from broker API"""
        pass
    
    @abstractmethod
    async def authenticate(self, credentials: Dict) -> bool:
        """Authenticate with broker"""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> BrokerAccount:
        """Get account information"""
        pass
    
    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        quantity: int,
        order_type: OrderType,
        side: str,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        product_type: ProductType = ProductType.MIS
    ) -> Order:
        """Place an order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None
    ) -> Order:
        """Modify an existing order"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Order:
        """Get order status"""
        pass
    
    @abstractmethod
    async def get_orders(self) -> List[Order]:
        """Get all orders for the day"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get all open positions"""
        pass
    
    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get specific position"""
        pass
    
    @abstractmethod
    async def square_off_position(self, symbol: str) -> Order:
        """Square off a position"""
        pass
    
    @abstractmethod
    async def get_ltp(self, symbol: str) -> float:
        """Get last traded price"""
        pass
    
    @abstractmethod
    async def get_quote(self, symbol: str) -> Dict:
        """Get full quote for symbol"""
        pass
    
    @abstractmethod
    async def get_order_history(self, order_id: str) -> List[Dict]:
        """Get order history/audit trail"""
        pass
    
    @abstractmethod
    async def get_trade_history(self, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Get trade history"""
        pass
    
    # Common utility methods
    
    async def wait_for_order_completion(
        self,
        order_id: str,
        timeout: int = 30,
        check_interval: float = 0.5
    ) -> Order:
        """Wait for order to complete with timeout"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            order = await self.get_order_status(order_id)
            
            if order.is_complete:
                return order
            
            await asyncio.sleep(check_interval)
        
        # Timeout reached
        logger.warning(f"Order {order_id} did not complete within {timeout} seconds")
        return await self.get_order_status(order_id)
    
    async def place_bracket_order(
        self,
        symbol: str,
        quantity: int,
        entry_price: float,
        stop_loss: float,
        target: float,
        product_type: ProductType = ProductType.MIS
    ) -> Tuple[Order, Order, Order]:
        """Place bracket order (entry + stop loss + target)"""
        # Place entry order
        entry_order = await self.place_order(
            symbol=symbol,
            quantity=quantity,
            order_type=OrderType.LIMIT,
            side="BUY",
            price=entry_price,
            product_type=product_type
        )
        
        # Wait for entry to fill
        entry_order = await self.wait_for_order_completion(entry_order.order_id)
        
        if entry_order.status != OrderStatus.FILLED:
            logger.error(f"Entry order not filled: {entry_order.status}")
            return entry_order, None, None
        
        # Place stop loss order
        sl_order = await self.place_order(
            symbol=symbol,
            quantity=quantity,
            order_type=OrderType.STOP_LOSS,
            side="SELL",
            trigger_price=stop_loss,
            product_type=product_type
        )
        
        # Place target order
        target_order = await self.place_order(
            symbol=symbol,
            quantity=quantity,
            order_type=OrderType.LIMIT,
            side="SELL",
            price=target,
            product_type=product_type
        )
        
        return entry_order, sl_order, target_order
    
    async def place_cover_order(
        self,
        symbol: str,
        quantity: int,
        order_type: OrderType,
        side: str,
        stop_loss: float,
        price: Optional[float] = None
    ) -> Tuple[Order, Order]:
        """Place cover order (entry + stop loss)"""
        # Place entry order
        entry_order = await self.place_order(
            symbol=symbol,
            quantity=quantity,
            order_type=order_type,
            side=side,
            price=price,
            product_type=ProductType.MIS
        )
        
        # Wait for entry to fill
        entry_order = await self.wait_for_order_completion(entry_order.order_id)
        
        if entry_order.status != OrderStatus.FILLED:
            return entry_order, None
        
        # Place stop loss order
        sl_side = "SELL" if side == "BUY" else "BUY"
        sl_order = await self.place_order(
            symbol=symbol,
            quantity=quantity,
            order_type=OrderType.STOP_LOSS,
            side=sl_side,
            trigger_price=stop_loss,
            product_type=ProductType.MIS
        )
        
        return entry_order, sl_order
    
    def calculate_brokerage(
        self,
        order_value: float,
        order_type: str = "equity"
    ) -> float:
        """Calculate brokerage charges"""
        # This is broker-specific, override in implementation
        if order_type == "equity":
            return min(order_value * 0.0003, 20)  # 0.03% or Rs 20, whichever is lower
        elif order_type == "options":
            return 20  # Flat Rs 20 per order
        return 0
    
    def calculate_total_charges(
        self,
        order_value: float,
        order_type: str = "equity"
    ) -> float:
        """Calculate total charges including taxes"""
        brokerage = self.calculate_brokerage(order_value, order_type)
        
        # Add taxes (simplified)
        stt = order_value * 0.001  # 0.1% STT
        transaction_charges = order_value * 0.0000325  # NSE charges
        gst = brokerage * 0.18  # 18% GST on brokerage
        sebi_charges = order_value * 0.000001  # SEBI charges
        stamp_duty = order_value * 0.00003  # Stamp duty
        
        total = brokerage + stt + transaction_charges + gst + sebi_charges + stamp_duty
        
        return round(total, 2)
    
    def validate_order(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate order before placing"""
        # Basic validation
        if quantity <= 0:
            return False, "Quantity must be positive"
        
        if price is not None and price <= 0:
            return False, "Price must be positive"
        
        # Check margin (simplified)
        if self.account:
            required_margin = (price or 100) * quantity * 0.2  # 20% margin
            if required_margin > self.account.available_margin:
                return False, f"Insufficient margin. Required: {required_margin}, Available: {self.account.available_margin}"
        
        return True, None
    
    async def get_option_greeks(self, symbol: str) -> Dict:
        """Get option Greeks"""
        # This would be implemented by specific brokers
        return {
            'delta': 0,
            'gamma': 0,
            'theta': 0,
            'vega': 0,
            'rho': 0
        }
    
    async def get_market_depth(self, symbol: str) -> Dict:
        """Get market depth (order book)"""
        # This would be implemented by specific brokers
        return {
            'bids': [],
            'asks': [],
            'total_buy_quantity': 0,
            'total_sell_quantity': 0
        }


class BrokerFactory:
    """Factory pattern for creating broker instances"""
    
    _brokers = {}
    
    @classmethod
    def register_broker(cls, name: str, broker_class: type):
        """Register a broker implementation"""
        cls._brokers[name.lower()] = broker_class
    
    @classmethod
    def create_broker(cls, name: str, config: Dict) -> BaseBroker:
        """Create a broker instance"""
        broker_class = cls._brokers.get(name.lower())
        
        if not broker_class:
            raise ValueError(f"Unknown broker: {name}. Available: {list(cls._brokers.keys())}")
        
        return broker_class(config)
    
    @classmethod
    def list_brokers(cls) -> List[str]:
        """List available brokers"""
        return list(cls._brokers.keys())