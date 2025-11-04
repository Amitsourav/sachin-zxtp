"""
Broker interface for handling different broker APIs
Supports Zerodha Kite Connect, Upstox, and paper trading
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BrokerInterface(ABC):
    """Abstract base class for broker interfaces"""
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with broker API"""
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, quantity: int, order_type: str, price: float = None) -> Dict:
        """Place an order"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        pass
    
    @abstractmethod
    def get_ltp(self, symbol: str) -> float:
        """Get Last Traded Price"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        pass

class ZerodhaBroker(BrokerInterface):
    """Zerodha Kite Connect implementation"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.kite = None
        
    def authenticate(self) -> bool:
        """Authenticate with Zerodha Kite"""
        try:
            from kiteconnect import KiteConnect
            
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            
            # Test authentication
            profile = self.kite.profile()
            logger.info(f"Authenticated with Zerodha as {profile.get('user_name')}")
            return True
            
        except Exception as e:
            logger.error(f"Zerodha authentication failed: {e}")
            return False
    
    def place_order(self, symbol: str, quantity: int, order_type: str, price: float = None) -> Dict:
        """Place order on Zerodha"""
        try:
            if not self.kite:
                raise Exception("Not authenticated")
            
            order_params = {
                'tradingsymbol': symbol,
                'exchange': 'NFO',  # Options exchange
                'transaction_type': 'BUY',
                'quantity': quantity,
                'order_type': order_type.upper(),
                'product': 'MIS',  # Intraday
                'validity': 'DAY'
            }
            
            if price and order_type.upper() == 'LIMIT':
                order_params['price'] = price
            
            order_id = self.kite.place_order(**order_params)
            
            return {
                'success': True,
                'order_id': order_id,
                'message': f"Order placed successfully: {order_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return {
                'success': False,
                'order_id': None,
                'message': str(e)
            }
    
    def get_positions(self) -> List[Dict]:
        """Get current positions from Zerodha"""
        try:
            if not self.kite:
                return []
            
            positions = self.kite.positions()
            return positions.get('day', [])
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    def get_ltp(self, symbol: str) -> float:
        """Get Last Traded Price from Zerodha"""
        try:
            if not self.kite:
                return 0.0
            
            instruments = [f"NFO:{symbol}"]
            ltp_data = self.kite.ltp(instruments)
            
            if f"NFO:{symbol}" in ltp_data:
                return float(ltp_data[f"NFO:{symbol}"]['last_price'])
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to get LTP for {symbol}: {e}")
            return 0.0
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel order on Zerodha"""
        try:
            if not self.kite:
                return False
            
            self.kite.cancel_order(variety='regular', order_id=order_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status from Zerodha"""
        try:
            if not self.kite:
                return {}
            
            orders = self.kite.orders()
            for order in orders:
                if order['order_id'] == order_id:
                    return order
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            return {}

class UpstoxBroker(BrokerInterface):
    """Upstox API implementation"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.upstox = None
        
    def authenticate(self) -> bool:
        """Authenticate with Upstox"""
        try:
            # Note: Upstox SDK implementation would go here
            # This is a placeholder for the actual implementation
            logger.info("Upstox authentication - placeholder implementation")
            return True
            
        except Exception as e:
            logger.error(f"Upstox authentication failed: {e}")
            return False
    
    def place_order(self, symbol: str, quantity: int, order_type: str, price: float = None) -> Dict:
        """Place order on Upstox - placeholder"""
        logger.info(f"Upstox place order - placeholder: {symbol}, {quantity}")
        return {'success': False, 'message': 'Upstox implementation pending'}
    
    def get_positions(self) -> List[Dict]:
        """Get positions from Upstox - placeholder"""
        return []
    
    def get_ltp(self, symbol: str) -> float:
        """Get LTP from Upstox - placeholder"""
        return 0.0
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel order on Upstox - placeholder"""
        return False
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status from Upstox - placeholder"""
        return {}

class PaperTradingBroker(BrokerInterface):
    """Paper trading implementation for testing"""
    
    def __init__(self, initial_balance: float = 100000):
        self.balance = initial_balance
        self.positions = []
        self.orders = {}
        self.order_counter = 1000
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate paper trading"""
        self.authenticated = True
        logger.info(f"Paper trading authenticated with balance: ₹{self.balance:,.2f}")
        return True
    
    def place_order(self, symbol: str, quantity: int, order_type: str, price: float = None) -> Dict:
        """Place paper trading order"""
        try:
            if not self.authenticated:
                return {'success': False, 'message': 'Not authenticated'}
            
            order_id = f"PAPER_{self.order_counter}"
            self.order_counter += 1
            
            # Simulate order execution
            execution_price = price if price else self._get_simulated_price(symbol)
            order_value = quantity * execution_price
            
            if order_value > self.balance:
                return {
                    'success': False,
                    'message': f'Insufficient balance. Required: ₹{order_value:,.2f}, Available: ₹{self.balance:,.2f}'
                }
            
            # Execute order
            self.balance -= order_value
            
            position = {
                'symbol': symbol,
                'quantity': quantity,
                'buy_price': execution_price,
                'current_price': execution_price,
                'pnl': 0.0,
                'order_id': order_id,
                'timestamp': datetime.now()
            }
            
            self.positions.append(position)
            
            self.orders[order_id] = {
                'order_id': order_id,
                'symbol': symbol,
                'quantity': quantity,
                'price': execution_price,
                'status': 'COMPLETE',
                'timestamp': datetime.now()
            }
            
            logger.info(f"Paper trade executed: {symbol} @ ₹{execution_price:,.2f}")
            
            return {
                'success': True,
                'order_id': order_id,
                'message': f"Paper order executed: {symbol} @ ₹{execution_price:,.2f}"
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Get paper trading positions"""
        # Update current prices and PnL
        for position in self.positions:
            current_price = self._get_simulated_price(position['symbol'])
            position['current_price'] = current_price
            position['pnl'] = (current_price - position['buy_price']) * position['quantity']
            position['pnl_percent'] = ((current_price - position['buy_price']) / position['buy_price']) * 100
        
        return self.positions
    
    def get_ltp(self, symbol: str) -> float:
        """Get simulated LTP"""
        return self._get_simulated_price(symbol)
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel paper order"""
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'CANCELLED'
            return True
        return False
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get paper order status"""
        return self.orders.get(order_id, {})
    
    def _get_simulated_price(self, symbol: str) -> float:
        """Generate simulated price for paper trading"""
        import random
        
        # Base prices for common option strikes
        base_prices = {
            'RELIANCE': 100.0,
            'TCS': 80.0,
            'INFY': 75.0,
            'HDFCBANK': 90.0,
            'ICICIBANK': 85.0
        }
        
        # Extract base symbol from option symbol
        base_symbol = symbol.split('24')[0] if '24' in symbol else symbol
        base_price = base_prices.get(base_symbol, 50.0)
        
        # Add random variation (±5%)
        variation = random.uniform(-0.05, 0.05)
        return base_price * (1 + variation)
    
    def sell_position(self, position_index: int) -> Dict:
        """Sell a position (for exit strategy)"""
        try:
            if position_index >= len(self.positions):
                return {'success': False, 'message': 'Position not found'}
            
            position = self.positions[position_index]
            sell_price = self._get_simulated_price(position['symbol'])
            sell_value = position['quantity'] * sell_price
            
            # Update balance
            self.balance += sell_value
            
            # Calculate final PnL
            final_pnl = (sell_price - position['buy_price']) * position['quantity']
            final_pnl_percent = ((sell_price - position['buy_price']) / position['buy_price']) * 100
            
            # Remove position
            sold_position = self.positions.pop(position_index)
            
            logger.info(f"Paper position sold: {sold_position['symbol']} @ ₹{sell_price:,.2f}, PnL: ₹{final_pnl:,.2f} ({final_pnl_percent:.2f}%)")
            
            return {
                'success': True,
                'sell_price': sell_price,
                'pnl': final_pnl,
                'pnl_percent': final_pnl_percent,
                'message': f"Position sold successfully. PnL: ₹{final_pnl:,.2f}"
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}

class BrokerFactory:
    """Factory class to create broker instances"""
    
    @staticmethod
    def create_broker(broker_config: Dict) -> BrokerInterface:
        """Create broker instance based on configuration"""
        broker_name = broker_config.get('name', '').lower()
        
        if broker_config.get('paper_trading', True):
            return PaperTradingBroker()
        
        elif broker_name == 'zerodha':
            return ZerodhaBroker(
                api_key=broker_config.get('api_key'),
                api_secret=broker_config.get('api_secret'),
                access_token=broker_config.get('access_token')
            )
        
        elif broker_name == 'upstox':
            return UpstoxBroker(
                api_key=broker_config.get('api_key'),
                api_secret=broker_config.get('api_secret'),
                access_token=broker_config.get('access_token')
            )
        
        else:
            raise ValueError(f"Unsupported broker: {broker_name}")