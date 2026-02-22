"""
Data fetching module for NSE market data and NIFTY50 gainers
"""

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
import json
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class NSEDataFetcher:
    """Fetches NSE market data using free APIs"""
    
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        # NIFTY50 constituent symbols
        self.nifty50_symbols = [
            "ADANIPORTS", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE",
            "BAJAJFINSV", "BPCL", "BHARTIARTL", "BRITANNIA", "CIPLA",
            "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT", "GRASIM",
            "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO",
            "HINDUNILVR", "HDFC", "ICICIBANK", "ITC", "INDUSINDBK",
            "INFY", "JSWSTEEL", "KOTAKBANK", "LT", "M&M",
            "MARUTI", "NTPC", "NESTLEIND", "ONGC", "POWERGRID",
            "RELIANCE", "SBILIFE", "SHREECEM", "SBIN", "SUNPHARMA",
            "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM",
            "TITAN", "UPL", "ULTRACEMCO", "WIPRO", "ADANIGREEN"
        ]
    
    def _get_nse_cookies(self) -> bool:
        """Get NSE cookies for API access"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to get NSE cookies: {e}")
            return False
    
    def get_nifty50_premarket_gainers(self) -> List[Dict]:
        """
        Fetch pre-market gainers from NIFTY50
        Returns list of stocks sorted by percentage gain
        """
        try:
            # Get cookies first
            if not self._get_nse_cookies():
                logger.error("Failed to get NSE cookies")
                return self._fallback_premarket_data()
            
            # Try to fetch pre-market data
            url = f"{self.base_url}/api/market-data-pre-open?key=NIFTY%2050"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                gainers = []
                
                if 'data' in data:
                    for item in data['data']:
                        if item.get('symbol') in self.nifty50_symbols:
                            change_percent = item.get('perChange', 0)
                            if change_percent > 0:  # Only gainers
                                gainers.append({
                                    'symbol': item.get('symbol'),
                                    'change_percent': change_percent,
                                    'price': item.get('lastPrice', 0),
                                    'change': item.get('change', 0),
                                    'volume': item.get('totalTradedVolume', 0)
                                })
                
                # Sort by percentage gain (descending)
                gainers.sort(key=lambda x: x['change_percent'], reverse=True)
                logger.info(f"Found {len(gainers)} pre-market gainers from NIFTY50")
                return gainers
            
            else:
                logger.warning(f"NSE API returned status {response.status_code}")
                return self._fallback_premarket_data()
                
        except Exception as e:
            logger.error(f"Error fetching pre-market gainers: {e}")
            return self._fallback_premarket_data()
    
    def _fallback_premarket_data(self) -> List[Dict]:
        """Fallback method using yfinance for market data"""
        try:
            logger.info("Using fallback method with yfinance")
            gainers = []
            
            # Get data for NIFTY50 stocks
            for symbol in self.nifty50_symbols[:10]:  # Limit to avoid rate limiting
                try:
                    ticker = yf.Ticker(f"{symbol}.NS")
                    info = ticker.info
                    
                    if 'regularMarketChangePercent' in info:
                        change_percent = info['regularMarketChangePercent'] * 100
                        if change_percent > 0:
                            gainers.append({
                                'symbol': symbol,
                                'change_percent': change_percent,
                                'price': info.get('regularMarketPrice', 0),
                                'change': info.get('regularMarketChange', 0),
                                'volume': info.get('regularMarketVolume', 0)
                            })
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Failed to get data for {symbol}: {e}")
                    continue
            
            gainers.sort(key=lambda x: x['change_percent'], reverse=True)
            return gainers
            
        except Exception as e:
            logger.error(f"Fallback method also failed: {e}")
            return []
    
    def get_option_chain(self, symbol: str) -> Optional[Dict]:
        """
        Fetch option chain data for a given symbol
        """
        try:
            if not self._get_nse_cookies():
                return None
            
            url = f"{self.base_url}/api/option-chain-indices?symbol={symbol}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch option chain for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching option chain for {symbol}: {e}")
            return None
    
    def calculate_pcr(self, option_data: Dict, strike_price: float) -> Optional[float]:
        """
        Calculate Put/Call Ratio for a specific strike price
        """
        try:
            if 'records' not in option_data or 'data' not in option_data['records']:
                return None
            
            put_oi = 0
            call_oi = 0
            
            for record in option_data['records']['data']:
                if record.get('strikePrice') == strike_price:
                    if 'CE' in record:
                        call_oi = record['CE'].get('openInterest', 0)
                    if 'PE' in record:
                        put_oi = record['PE'].get('openInterest', 0)
                    break
            
            if call_oi > 0:
                pcr = put_oi / call_oi
                return round(pcr, 2)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating PCR: {e}")
            return None
    
    def find_atm_strike(self, symbol: str, spot_price: float) -> Optional[float]:
        """
        Find the At-The-Money (ATM) strike price closest to spot price
        """
        try:
            option_data = self.get_option_chain(symbol)
            if not option_data:
                return None
            
            strikes = []
            if 'records' in option_data and 'data' in option_data['records']:
                for record in option_data['records']['data']:
                    strike = record.get('strikePrice')
                    if strike:
                        strikes.append(strike)
            
            if not strikes:
                return None
            
            # Find closest strike to spot price
            atm_strike = min(strikes, key=lambda x: abs(x - spot_price))
            return atm_strike
            
        except Exception as e:
            logger.error(f"Error finding ATM strike: {e}")
            return None
    
    def get_market_holidays(self) -> List[str]:
        """
        Get list of market holidays
        """
        try:
            url = f"{self.base_url}/api/holiday-master?type=trading"
            response = self.session.get(url, timeout=10)
            
            holidays = []
            if response.status_code == 200:
                data = response.json()
                if 'CM' in data:
                    for holiday in data['CM']:
                        holidays.append(holiday.get('tradingDate'))
            
            return holidays
            
        except Exception as e:
            logger.error(f"Error fetching market holidays: {e}")
            # Fallback - common holidays
            return [
                "26-Jan-2024", "14-Mar-2024", "25-Mar-2024", "29-Mar-2024",
                "11-Apr-2024", "17-Apr-2024", "01-May-2024", "15-Aug-2024",
                "02-Oct-2024", "31-Oct-2024", "01-Nov-2024", "15-Nov-2024"
            ]
    
    def is_trading_day(self) -> bool:
        """
        Check if today is a trading day
        """
        today = datetime.now()
        
        # Check if weekend
        if today.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check if holiday
        holidays = self.get_market_holidays()
        today_str = today.strftime("%d-%b-%Y")
        
        if today_str in holidays:
            return False
        
        return True
    
    def get_vix(self) -> Optional[float]:
        """
        Get current VIX (Volatility Index) value
        """
        try:
            url = f"{self.base_url}/api/market-data-pre-open?key=INDIA%20VIX"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    vix_value = data['data'][0].get('lastPrice', 0)
                    return float(vix_value)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching VIX: {e}")
            return None