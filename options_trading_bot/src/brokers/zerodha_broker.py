"""
Zerodha Kite Connect Broker Implementation
Real trading through Zerodha's API
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from kiteconnect import KiteConnect, KiteTicker

from .base_broker import BaseBroker, OrderType, TransactionType, ProductType, OrderStatus

logger = logging.getLogger(__name__)


class ZerodhaBroker(BaseBroker):
    """
    Zerodha broker implementation using Kite Connect API
    """
    
    def __init__(self, api_key: str, api_secret: str, access_token: Optional[str] = None):
        """
        Initialize Zerodha broker
        
        Args:
            api_key: Your Kite Connect API key
            api_secret: Your Kite Connect API secret
            access_token: Access token (if already generated)
        """
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.kite = KiteConnect(api_key=api_key)
        
        if access_token:
            self.kite.set_access_token(access_token)
            
        self.is_connected = False
        self.ticker = None
        
    async def connect(self) -> bool:
        """Connect to Zerodha"""
        try:
            if not self.access_token:
                logger.error("Access token not provided. Please complete login flow first.")
                return False
                
            # Set access token
            self.kite.set_access_token(self.access_token)
            
            # Verify connection by fetching profile
            profile = self.kite.profile()
            logger.info(f"Connected to Zerodha as {profile['user_name']} ({profile['user_id']})")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Zerodha: {e}")
            return False
            
    def get_login_url(self) -> str:
        """Get the login URL for user authentication"""
        return self.kite.login_url()
        
    def generate_session(self, request_token: str) -> str:
        """
        Generate access token from request token
        
        Args:
            request_token: Token received after login redirect
            
        Returns:
            Access token for API calls
        """
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            logger.info("Access token generated successfully")
            return self.access_token
        except Exception as e:
            logger.error(f"Failed to generate session: {e}")
            raise
            
    async def place_order(
        self,
        symbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        order_type: str = 'MARKET',
        product: str = 'MIS',
        price: float = 0,
        trigger_price: float = 0,
        validity: str = 'DAY',
        disclosed_quantity: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Place order on Zerodha"""
        try:
            # Map our parameters to Kite Connect format
            kite_params = {
                'tradingsymbol': symbol,
                'exchange': exchange,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'order_type': order_type,
                'product': product,
                'validity': validity,
                'disclosed_quantity': disclosed_quantity
            }
            
            # Add price for limit orders
            if order_type == 'LIMIT':
                kite_params['price'] = price
            elif order_type == 'SL' or order_type == 'SL-M':
                kite_params['trigger_price'] = trigger_price
                if order_type == 'SL':
                    kite_params['price'] = price
                    
            # Place order
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                **kite_params
            )
            
            logger.info(f"Order placed successfully: {order_id}")
            
            # Get order details
            order_details = self.get_order_details(order_id)
            
            return {
                'order_id': order_id,
                'status': order_details.get('status', 'PENDING'),
                'executed_price': order_details.get('average_price', 0),
                'quantity': quantity,
                'symbol': symbol,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return {
                'order_id': None,
                'status': 'REJECTED',
                'error': str(e)
            }
            
    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get details of a specific order"""
        try:
            orders = self.kite.orders()
            for order in orders:
                if order['order_id'] == order_id:
                    return order
            return {}
        except Exception as e:
            logger.error(f"Failed to get order details: {e}")
            return {}
            
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        try:
            positions = self.kite.positions()
            
            # Format positions
            formatted_positions = []
            for pos in positions['day']:
                if pos['quantity'] != 0:  # Only open positions
                    formatted_positions.append({
                        'symbol': pos['tradingsymbol'],
                        'exchange': pos['exchange'],
                        'quantity': pos['quantity'],
                        'average_price': pos['average_price'],
                        'last_price': pos['last_price'],
                        'pnl': pos['pnl'],
                        'product': pos['product']
                    })
                    
            return formatted_positions
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
            
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get all orders for today"""
        try:
            orders = self.kite.orders()
            return orders
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            return []
            
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self.kite.cancel_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id
            )
            logger.info(f"Order {order_id} cancelled successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
            
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        order_type: Optional[str] = None
    ) -> bool:
        """Modify an existing order"""
        try:
            params = {}
            if quantity is not None:
                params['quantity'] = quantity
            if price is not None:
                params['price'] = price
            if trigger_price is not None:
                params['trigger_price'] = trigger_price
            if order_type is not None:
                params['order_type'] = order_type
                
            self.kite.modify_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id,
                **params
            )
            logger.info(f"Order {order_id} modified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to modify order {order_id}: {e}")
            return False
            
    def get_funds(self) -> Dict[str, float]:
        """Get account funds/margins"""
        try:
            margins = self.kite.margins()
            
            # Combine equity and commodity margins
            available_cash = 0
            used_margin = 0
            
            if 'equity' in margins:
                available_cash += margins['equity'].get('available', {}).get('cash', 0)
                used_margin += margins['equity'].get('utilised', {}).get('debits', 0)
                
            return {
                'available_cash': available_cash,
                'used_margin': used_margin,
                'total_value': available_cash + used_margin
            }
            
        except Exception as e:
            logger.error(f"Failed to get funds: {e}")
            return {'available_cash': 0, 'used_margin': 0, 'total_value': 0}
            
    def get_pnl(self) -> Dict[str, float]:
        """Calculate total P&L"""
        try:
            positions = self.kite.positions()
            
            realised_pnl = sum(pos['realised'] for pos in positions['day'])
            unrealised_pnl = sum(pos['unrealised'] for pos in positions['day'])
            total_pnl = realised_pnl + unrealised_pnl
            
            return {
                'realised_pnl': realised_pnl,
                'unrealised_pnl': unrealised_pnl,
                'total_pnl': total_pnl,
                'pnl_percent': 0  # Calculate based on capital if needed
            }
            
        except Exception as e:
            logger.error(f"Failed to get P&L: {e}")
            return {
                'realised_pnl': 0,
                'unrealised_pnl': 0,
                'total_pnl': 0,
                'pnl_percent': 0
            }
            
    def get_quote(self, symbols: List[str], exchange: str = 'NSE') -> Dict[str, Any]:
        """Get real-time quotes for symbols"""
        try:
            # Format symbols for Kite Connect
            instruments = [f"{exchange}:{symbol}" for symbol in symbols]
            quotes = self.kite.quote(instruments)
            
            # Simplify the response
            simplified_quotes = {}
            for instrument, data in quotes.items():
                symbol = instrument.split(':')[1]
                simplified_quotes[symbol] = {
                    'ltp': data['last_price'],
                    'open': data['ohlc']['open'],
                    'high': data['ohlc']['high'],
                    'low': data['ohlc']['low'],
                    'close': data['ohlc']['close'],
                    'volume': data['volume'],
                    'bid': data['depth']['buy'][0]['price'] if data['depth']['buy'] else 0,
                    'ask': data['depth']['sell'][0]['price'] if data['depth']['sell'] else 0
                }
                
            return simplified_quotes
            
        except Exception as e:
            logger.error(f"Failed to get quotes: {e}")
            return {}
            
    def get_option_chain(self, symbol: str, expiry: str) -> Dict[str, Any]:
        """Get option chain for a symbol"""
        try:
            # Get instruments
            instruments = self.kite.instruments("NFO")
            
            # Filter for the symbol and expiry
            options = []
            for inst in instruments:
                if inst['name'] == symbol and str(inst['expiry']) == expiry:
                    options.append({
                        'symbol': inst['tradingsymbol'],
                        'strike': inst['strike'],
                        'instrument_type': inst['instrument_type'],  # CE or PE
                        'lot_size': inst['lot_size']
                    })
                    
            return {
                'symbol': symbol,
                'expiry': expiry,
                'options': options
            }
            
        except Exception as e:
            logger.error(f"Failed to get option chain: {e}")
            return {}
            
    async def place_bracket_order(
        self,
        symbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        price: float,
        target: float,
        stop_loss: float,
        trailing_stop_loss: Optional[float] = None
    ) -> Dict[str, Any]:
        """Place bracket order with target and stop loss"""
        try:
            params = {
                'tradingsymbol': symbol,
                'exchange': exchange,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'order_type': 'LIMIT',
                'product': 'MIS',
                'price': price,
                'squareoff': abs(target - price),
                'stoploss': abs(price - stop_loss)
            }
            
            if trailing_stop_loss:
                params['trailing_stoploss'] = trailing_stop_loss
                
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_BO,
                **params
            )
            
            logger.info(f"Bracket order placed: {order_id}")
            
            return {
                'order_id': order_id,
                'status': 'PENDING',
                'symbol': symbol,
                'quantity': quantity
            }
            
        except Exception as e:
            logger.error(f"Failed to place bracket order: {e}")
            return {'order_id': None, 'status': 'REJECTED', 'error': str(e)}
            
    async def disconnect(self):
        """Disconnect from Zerodha"""
        try:
            if self.ticker:
                self.ticker.close()
            self.is_connected = False
            logger.info("Disconnected from Zerodha")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            
    def start_websocket(self, tokens: List[int], on_ticks):
        """Start WebSocket for real-time data"""
        try:
            self.ticker = KiteTicker(self.api_key, self.access_token)
            
            self.ticker.on_ticks = on_ticks
            self.ticker.on_connect = lambda ws, response: logger.info("WebSocket connected")
            self.ticker.on_close = lambda ws, code, reason: logger.info(f"WebSocket closed: {reason}")
            
            self.ticker.connect(threaded=True)
            
            # Subscribe to tokens
            self.ticker.subscribe(tokens)
            self.ticker.set_mode(self.ticker.MODE_FULL, tokens)
            
            logger.info(f"WebSocket started for {len(tokens)} instruments")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket: {e}")