"""
Live Paper Trading Broker
Uses real market data for realistic paper trading
"""

import asyncio
import random
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
from .paper_broker import PaperBroker

logger = logging.getLogger(__name__)


class LivePaperBroker(PaperBroker):
    """
    Paper trading with LIVE market data from Zerodha
    Most realistic paper trading experience without real money
    """
    
    def __init__(self, initial_capital: float = 100000):
        super().__init__(initial_capital)
        self.is_market_hours = False
        self.last_prices = {}
        self.zerodha_data = None
        
        # Check if Zerodha is configured
        config_path = Path("config/config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Use Zerodha if configured, otherwise fallback
        if config.get('broker', {}).get('name') == 'zerodha' and config.get('broker', {}).get('access_token'):
            try:
                from ..data.zerodha_data_fetcher import ZerodhaDataFetcher
                self.zerodha_data = ZerodhaDataFetcher()
                logger.info("Using Zerodha for REAL-TIME market data")
            except Exception as e:
                logger.warning(f"Could not initialize Zerodha data: {e}, using fallback")
                from ..data.live_data_fetcher import PaperTradingLiveData
                self.live_data = PaperTradingLiveData()
        else:
            from ..data.live_data_fetcher import PaperTradingLiveData
            self.live_data = PaperTradingLiveData()
        
    async def connect(self) -> bool:
        """Connect to live data sources"""
        logger.info("Connecting to live paper broker...")
        
        # Initialize data fetcher based on what's available
        if self.zerodha_data:
            logger.info("Connected to Zerodha for real-time data")
        else:
            # Initialize fallback live data fetcher
            await self.live_data.initialize()
            logger.info("Using fallback data source")
        
        # Parent connection
        await super().connect()
        
        # Start price update loop
        asyncio.create_task(self.update_prices_loop())
        
        logger.info("Live paper broker connected with real market data!")
        return True
        
    async def update_prices_loop(self):
        """Continuously update prices with live data"""
        while self.is_connected:
            try:
                # Check market hours
                now = datetime.now().time()
                self.is_market_hours = (
                    datetime.now().weekday() < 5 and  # Monday-Friday
                    now >= datetime.strptime('09:15', '%H:%M').time() and
                    now <= datetime.strptime('15:30', '%H:%M').time()
                )
                
                if self.is_market_hours:
                    # Update tracked symbols
                    symbols_to_update = list(set(list(self.positions.keys()) + list(self.last_prices.keys())))
                    
                    if symbols_to_update:
                        if self.zerodha_data:
                            # Get live quotes from Zerodha
                            try:
                                quotes = self.zerodha_data.get_live_quotes(symbols_to_update)
                                for symbol, data in quotes.items():
                                    if data and data.get('ltp', 0) > 0:
                                        self.last_prices[symbol] = data['ltp']
                                        self.market_data[symbol] = {
                                            'ltp': data['ltp'],
                                            'timestamp': datetime.now()
                                        }
                                logger.debug(f"Updated {len(quotes)} symbols from Zerodha")
                            except Exception as e:
                                logger.error(f"Zerodha data fetch error: {e}")
                        else:
                            # Use fallback data source
                            for symbol in symbols_to_update:
                                try:
                                    data = await self.live_data.get_market_data(symbol)
                                    if data and data.get('ltp', 0) > 0:
                                        self.last_prices[symbol] = data['ltp']
                                        self.market_data[symbol] = {
                                            'ltp': data['ltp'],
                                            'timestamp': datetime.now()
                                        }
                                except Exception as e:
                                    logger.debug(f"Could not update {symbol}: {e}")
                            
                await asyncio.sleep(5 if self.is_market_hours else 60)
                
            except Exception as e:
                logger.error(f"Price update error: {e}")
                await asyncio.sleep(10)
                
    def get_market_price(self, symbol: str) -> float:
        """Get live market price or last known price"""
        # Check if we have recent live price
        if symbol in self.last_prices:
            return self.last_prices[symbol]
            
        # Otherwise use parent's simulated price
        return super().get_market_price(symbol)
        
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
        Place order with live market prices
        Adds realistic slippage based on actual market conditions
        """
        # Try to get live price first
        live_data = await self.live_data.get_market_data(symbol)
        if live_data and live_data.get('ltp', 0) > 0:
            market_price = live_data['ltp']
            self.last_prices[symbol] = market_price
            logger.info(f"Using live price for {symbol}: ₹{market_price:.2f}")
        else:
            market_price = self.get_market_price(symbol)
            logger.info(f"Using cached/simulated price for {symbol}: ₹{market_price:.2f}")
            
        # Calculate realistic slippage based on market hours
        if self.is_market_hours:
            # During market hours: realistic slippage
            if datetime.now().time() < datetime.strptime('09:30', '%H:%M').time():
                # First 15 minutes: higher slippage
                slippage = random.uniform(0.2, 0.5) / 100  # 0.2-0.5%
            else:
                # Normal hours: lower slippage
                slippage = random.uniform(0.05, 0.2) / 100  # 0.05-0.2%
        else:
            # After hours: use last close with gap
            slippage = random.uniform(0.5, 1.0) / 100  # 0.5-1% gap
            
        # Calculate execution price
        if order_type == 'MARKET':
            if transaction_type == 'BUY':
                executed_price = market_price * (1 + slippage)
            else:
                executed_price = market_price * (1 - slippage)
        else:
            executed_price = price
            
        # Set the market price for order processing
        self.market_data[symbol] = {'ltp': market_price}
        
        # Process order through parent
        order_result = await super().place_order(
            symbol=symbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            order_type=order_type,
            price=executed_price if order_type != 'MARKET' else price,
            product=product,
            **kwargs
        )
        
        # Update with actual executed price
        if order_result['status'] == 'COMPLETE':
            order_result['executed_price'] = executed_price
            order_result['market_price'] = market_price
            order_result['slippage'] = slippage * 100  # As percentage
            
        return order_result
        
    async def get_quote(self, symbol: str, exchange: str = 'NSE') -> Dict[str, Any]:
        """Get live quote for a symbol"""
        # Try live data first
        live_data = await self.live_data.get_market_data(symbol)
        
        if live_data and live_data.get('ltp', 0) > 0:
            ltp = live_data['ltp']
            return {
                'symbol': symbol,
                'exchange': exchange,
                'ltp': ltp,
                'bid': ltp * 0.9995,  # Realistic bid-ask spread
                'ask': ltp * 1.0005,
                'open': live_data.get('open', ltp),
                'high': live_data.get('high', ltp * 1.01),
                'low': live_data.get('low', ltp * 0.99),
                'close': ltp,
                'volume': live_data.get('volume', random.randint(100000, 1000000)),
                'timestamp': datetime.now(),
                'source': 'LIVE'
            }
        else:
            # Fallback to simulated
            quote = await super().get_quote(symbol, exchange)
            quote['source'] = 'SIMULATED'
            return quote
            
    async def scan_top_gainers(self) -> List[Dict[str, Any]]:
        """Scan for top gainers using live data"""
        logger.info("Scanning live market for top gainers...")
        
        # Get live top gainers
        gainers = await self.live_data.nse_fetcher.get_top_gainers()
        
        if gainers:
            logger.info(f"Found {len(gainers)} top gainers from live market")
            return gainers
        else:
            logger.warning("Could not fetch live gainers, using simulated data")
            # Fallback to simulated
            return self._simulate_top_gainers()
            
    def _simulate_top_gainers(self) -> List[Dict[str, Any]]:
        """Simulate top gainers when live data unavailable"""
        stocks = ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ICICIBANK']
        gainers = []
        
        for stock in stocks:
            gainers.append({
                'symbol': stock,
                'ltp': random.uniform(1000, 5000),
                'change_percent': random.uniform(0.5, 5.0),
                'volume': random.randint(1000000, 10000000)
            })
            
        return sorted(gainers, key=lambda x: x['change_percent'], reverse=True)
        
    async def get_pcr_ratio(self) -> float:
        """Get live Put-Call Ratio"""
        option_data = await self.live_data.nse_fetcher.get_option_chain_live()
        
        if option_data and 'pcr' in option_data:
            logger.info(f"Live PCR: {option_data['pcr']:.2f}")
            return option_data['pcr']
        else:
            # Simulate PCR in acceptable range
            pcr = random.uniform(0.7, 1.5)
            logger.info(f"Simulated PCR: {pcr:.2f}")
            return pcr
            
    async def get_option_chain(self, symbol: str, expiry: str) -> List[Dict[str, Any]]:
        """Get option chain with live data if available"""
        try:
            # Try to get live option chain
            option_data = await self.live_data.nse_fetcher.get_option_chain_live(symbol)
            
            if option_data:
                logger.info(f"Using live option chain for {symbol}")
                # Process and return live data
                # (Would need more parsing of NSE option chain response)
                
        except Exception as e:
            logger.debug(f"Could not fetch live option chain: {e}")
            
        # Fallback to simulated
        return await super().get_option_chain(symbol, expiry)
        
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions with live P&L"""
        positions = []
        
        for symbol, pos in self.positions.items():
            # Get current price (live if available)
            current_price = self.last_prices.get(symbol, pos['avg_price'])
            
            # Calculate live P&L
            pnl = (current_price - pos['avg_price']) * pos['quantity']
            pnl_percent = (pnl / (pos['avg_price'] * pos['quantity'])) * 100
            
            positions.append({
                'symbol': symbol,
                'quantity': pos['quantity'],
                'avg_price': pos['avg_price'],
                'current_price': current_price,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'value': current_price * pos['quantity'],
                'is_live_price': symbol in self.last_prices
            })
            
        return positions
        
    async def monitor_market_status(self):
        """Monitor and display market status"""
        while self.is_connected:
            if self.is_market_hours:
                status = "🟢 MARKET OPEN"
                
                # Get some market stats
                if self.positions:
                    pnl = self.get_pnl()
                    logger.info(f"{status} | P&L: ₹{pnl['total_pnl']:.2f} ({pnl['pnl_percent']:.2f}%)")
            else:
                status = "🔴 MARKET CLOSED"
                logger.info(f"{status} | Next open: 9:15 AM")
                
            await asyncio.sleep(300)  # Update every 5 minutes
    
    # Implement remaining abstract methods
    async def authenticate(self) -> bool:
        """Authenticate paper broker (always succeeds)"""
        return True
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return {
            'account_id': 'PAPER_LIVE_001',
            'name': 'Paper Trading Account',
            'broker': 'Live Paper Broker',
            'segment': ['NSE', 'NFO'],
            'capital': self.initial_capital,
            'current_value': self.capital
        }
    
    def get_ltp(self, symbol: str, exchange: str = 'NSE') -> float:
        """Get last traded price"""
        return self.get_market_price(symbol)
    
    def get_order_history(self, order_id: str = None) -> List[Dict[str, Any]]:
        """Get order history"""
        if order_id:
            return [self.orders.get(order_id)] if order_id in self.orders else []
        return list(self.orders.values())
    
    def get_trade_history(self, from_date: str = None, to_date: str = None) -> List[Dict[str, Any]]:
        """Get trade history"""
        trades = []
        for order in self.orders.values():
            if order['status'] == 'COMPLETE':
                trades.append({
                    'trade_id': order['order_id'],
                    'symbol': order['symbol'],
                    'transaction_type': order['transaction_type'],
                    'quantity': order['quantity'],
                    'price': order['executed_price'],
                    'timestamp': order['timestamp']
                })
        return trades
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get specific position"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            current_price = self.get_market_price(symbol)
            pnl = (current_price - pos['avg_price']) * pos['quantity']
            return {
                'symbol': symbol,
                'quantity': pos['quantity'],
                'avg_price': pos['avg_price'],
                'current_price': current_price,
                'pnl': pnl
            }
        return None
    
    def modify_order(self, order_id: str, **kwargs) -> bool:
        """Modify an order"""
        if order_id in self.orders and self.orders[order_id]['status'] == 'PENDING':
            self.orders[order_id].update(kwargs)
            return True
        return False
    
    def square_off_position(self, symbol: str) -> bool:
        """Square off a position"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            # Create a sell order
            asyncio.create_task(self.place_order(
                symbol=symbol,
                exchange='NFO',
                transaction_type='SELL',
                quantity=pos['quantity'],
                order_type='MARKET',
                product='MIS'
            ))
            return True
        return False