"""
Paper Trading Broker Implementation
Simulates real trading without actual money for testing
"""

import asyncio
import random
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from .base_broker import BaseBroker, OrderStatus, OrderType, ProductType

logger = logging.getLogger(__name__)


class PaperBroker(BaseBroker):
    """
    Paper trading broker for testing strategies without real money
    Simulates real market conditions with realistic delays and slippage
    """
    
    def __init__(self, initial_capital: float = 100000, config=None):
        # Call parent constructor with empty config if none provided
        super().__init__(config or {})
        self.capital = initial_capital
        self.initial_capital = initial_capital
        # Note: positions and orders are already initialized in parent
        self.order_counter = 1000
        
        # Simulated market data
        self.market_data = {}
        self.initialize_market_data()
        
    def initialize_market_data(self):
        """Initialize with some sample market data"""
        self.market_data = {
            'RELIANCE': {'ltp': 2800, 'change': 2.5},
            'TCS': {'ltp': 3500, 'change': 1.8},
            'INFY': {'ltp': 1450, 'change': -0.5},
            'HDFC': {'ltp': 1650, 'change': 1.2},
            'RELIANCE2800CE': {'ltp': 45.50, 'bid': 45.00, 'ask': 46.00, 'lot_size': 250},
            'TCS3500CE': {'ltp': 35.00, 'bid': 34.50, 'ask': 35.50, 'lot_size': 150},
        }
        
    async def connect(self) -> bool:
        """Simulate broker connection"""
        logger.info("Connecting to paper broker...")
        await asyncio.sleep(0.5)  # Simulate connection delay
        self.is_connected = True
        logger.info("Paper broker connected successfully")
        return True
        
    async def disconnect(self) -> bool:
        """Disconnect from paper broker"""
        self.is_connected = False
        logger.info("Paper broker disconnected")
        return True
        
    def get_profile(self) -> Dict[str, Any]:
        """Get account profile"""
        return {
            'user_id': 'PAPER_USER',
            'user_name': 'Paper Trader',
            'email': 'paper@trading.com',
            'broker': 'Paper Broker',
            'exchanges': ['NSE', 'NFO']
        }
        
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        used_margin = sum(
            pos.get('margin', 0) for pos in self.positions.values()
        )
        return {
            'cash': self.capital,
            'opening_balance': self.initial_capital,
            'used_margin': used_margin,
            'available_margin': self.capital - used_margin,
            'total_value': self.capital
        }
        
    async def place_order(
        self,
        symbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        order_type: str = 'MARKET',
        price: float = 0,
        product: str = 'MIS',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Place a paper order with realistic simulation
        """
        # Generate order ID
        order_id = f"PAPER_{self.order_counter}"
        self.order_counter += 1
        
        # Get current price
        market_price = self.get_market_price(symbol)
        
        # Calculate execution price with slippage
        if order_type == 'MARKET':
            slippage = random.uniform(0.1, 0.3) / 100  # 0.1-0.3% slippage
            if transaction_type == 'BUY':
                executed_price = market_price * (1 + slippage)
            else:
                executed_price = market_price * (1 - slippage)
        else:
            executed_price = price
            
        # Calculate order value
        order_value = executed_price * quantity
        
        # Check if sufficient margin
        if transaction_type == 'BUY':
            required_margin = order_value * 0.2  # 20% margin for options
            if required_margin > self.get_balance()['available_margin']:
                return {
                    'order_id': order_id,
                    'status': 'REJECTED',
                    'message': 'Insufficient margin',
                    'timestamp': datetime.now()
                }
                
        # Simulate order processing delay
        await asyncio.sleep(random.uniform(0.05, 0.2))  # 50-200ms delay
        
        # Create order record
        order = {
            'order_id': order_id,
            'symbol': symbol,
            'exchange': exchange,
            'transaction_type': transaction_type,
            'quantity': quantity,
            'order_type': order_type,
            'price': price,
            'executed_price': executed_price,
            'product': product,
            'status': 'COMPLETE',
            'timestamp': datetime.now(),
            'order_value': order_value
        }
        
        self.orders[order_id] = order
        
        # Update positions
        if transaction_type == 'BUY':
            self.add_position(symbol, quantity, executed_price)
        else:
            self.reduce_position(symbol, quantity, executed_price)
            
        logger.info(f"Paper order executed: {order_id} - {transaction_type} {quantity} {symbol} @ {executed_price:.2f}")
        
        return order
        
    def cancel_order(self, order_id: str) -> bool:
        """Cancel a paper order"""
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'CANCELLED'
            logger.info(f"Paper order cancelled: {order_id}")
            return True
        return False
        
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Get paper order status"""
        if order_id in self.orders:
            status_map = {
                'PENDING': OrderStatus.PENDING,
                'COMPLETE': OrderStatus.EXECUTED,
                'REJECTED': OrderStatus.REJECTED,
                'CANCELLED': OrderStatus.CANCELLED
            }
            return status_map.get(self.orders[order_id]['status'])
        return None
        
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all paper positions"""
        positions = []
        for symbol, pos in self.positions.items():
            current_price = self.get_market_price(symbol)
            pnl = (current_price - pos['avg_price']) * pos['quantity']
            pnl_percent = (pnl / (pos['avg_price'] * pos['quantity'])) * 100
            
            positions.append({
                'symbol': symbol,
                'quantity': pos['quantity'],
                'avg_price': pos['avg_price'],
                'current_price': current_price,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'value': current_price * pos['quantity']
            })
            
        return positions
        
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get all paper orders"""
        return list(self.orders.values())
        
    def add_position(self, symbol: str, quantity: int, price: float):
        """Add to paper position"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_qty = pos['quantity'] + quantity
            total_value = (pos['quantity'] * pos['avg_price']) + (quantity * price)
            pos['avg_price'] = total_value / total_qty
            pos['quantity'] = total_qty
        else:
            self.positions[symbol] = {
                'quantity': quantity,
                'avg_price': price,
                'entry_time': datetime.now()
            }
            
        # Deduct from capital
        self.capital -= (quantity * price)
        
    def reduce_position(self, symbol: str, quantity: int, price: float):
        """Reduce paper position"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            
            # Calculate P&L
            pnl = (price - pos['avg_price']) * quantity
            
            # Update position
            pos['quantity'] -= quantity
            if pos['quantity'] <= 0:
                del self.positions[symbol]
                
            # Add to capital
            self.capital += (quantity * price)
            
            logger.info(f"Position closed: {symbol} - PnL: {pnl:.2f}")
            
    def get_market_price(self, symbol: str) -> float:
        """Get simulated market price with random walk"""
        if symbol not in self.market_data:
            # Generate random price for unknown symbols
            return random.uniform(10, 100)
            
        # Add small random movement to simulate market
        base_price = self.market_data[symbol]['ltp']
        movement = random.uniform(-0.5, 0.5) / 100  # ±0.5% movement
        return base_price * (1 + movement)
        
    def update_market_prices(self):
        """Update market prices to simulate market movement"""
        for symbol in self.market_data:
            movement = random.uniform(-1, 1) / 100  # ±1% movement
            self.market_data[symbol]['ltp'] *= (1 + movement)
            self.market_data[symbol]['change'] += movement * 100
            
    async def get_quote(self, symbol: str, exchange: str = 'NSE') -> Dict[str, Any]:
        """Get quote for a symbol"""
        price = self.get_market_price(symbol)
        return {
            'symbol': symbol,
            'exchange': exchange,
            'ltp': price,
            'bid': price * 0.999,
            'ask': price * 1.001,
            'open': price * 0.98,
            'high': price * 1.02,
            'low': price * 0.97,
            'close': price,
            'volume': random.randint(100000, 1000000),
            'timestamp': datetime.now()
        }
        
    async def get_option_chain(self, symbol: str, expiry: str) -> List[Dict[str, Any]]:
        """Get simulated option chain"""
        spot_price = self.get_market_price(symbol)
        strikes = []
        
        # Generate strikes around ATM
        atm_strike = round(spot_price / 100) * 100
        
        for i in range(-5, 6):
            strike = atm_strike + (i * 100)
            
            # Simulate option prices
            call_price = max(spot_price - strike + random.uniform(10, 30), 5)
            put_price = max(strike - spot_price + random.uniform(10, 30), 5)
            
            strikes.append({
                'strike': strike,
                'call_ltp': call_price if strike >= spot_price else call_price + (spot_price - strike),
                'put_ltp': put_price if strike <= spot_price else put_price + (strike - spot_price),
                'call_oi': random.randint(10000, 100000),
                'put_oi': random.randint(10000, 100000),
                'call_volume': random.randint(1000, 10000),
                'put_volume': random.randint(1000, 10000)
            })
            
        return strikes
        
    def get_pnl(self) -> Dict[str, float]:
        """Calculate total P&L"""
        realized_pnl = 0
        unrealized_pnl = 0
        
        # Calculate unrealized P&L from open positions
        for symbol, pos in self.positions.items():
            current_price = self.get_market_price(symbol)
            unrealized_pnl += (current_price - pos['avg_price']) * pos['quantity']
            
        # Calculate realized P&L
        realized_pnl = self.capital - self.initial_capital + unrealized_pnl
        
        return {
            'realized_pnl': realized_pnl - unrealized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': realized_pnl,
            'pnl_percent': (realized_pnl / self.initial_capital) * 100
        }
        
    def reset(self):
        """Reset paper trading account"""
        self.capital = self.initial_capital
        self.positions.clear()
        self.orders.clear()
        self.order_counter = 1000
        logger.info("Paper trading account reset")