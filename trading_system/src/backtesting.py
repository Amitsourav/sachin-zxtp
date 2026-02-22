"""
Backtesting module for 9:15 Strategy
Tests historical performance of the strategy
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import json
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

class BacktestEngine:
    """Backtesting engine for the 9:15 Strategy"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.backtest_config = config.get('backtesting', {})
        self.trading_config = config.get('trading', {})
        
        # Strategy parameters
        self.pcr_min = self.trading_config.get('pcr_min_range', 0.7)
        self.pcr_max = self.trading_config.get('pcr_max_range', 1.5)
        self.profit_target = self.trading_config.get('profit_target_percent', 8.0)
        self.initial_capital = self.backtest_config.get('initial_capital', 100000)
        
        # Results storage
        self.trades = []
        self.daily_returns = []
        self.equity_curve = []
        
    def run_backtest(self, start_date: str, end_date: str) -> Dict:
        """Run backtest for specified date range"""
        try:
            logger.info(f"Starting backtest from {start_date} to {end_date}")
            
            # Get historical data
            historical_data = self._get_historical_data(start_date, end_date)
            
            if not historical_data:
                return {'error': 'Failed to fetch historical data'}
            
            # Run strategy simulation
            self._simulate_strategy(historical_data)
            
            # Calculate performance metrics
            performance = self._calculate_performance()
            
            # Generate plots
            plots = self._generate_plots()
            
            results = {
                'performance': performance,
                'trades': self.trades,
                'equity_curve': self.equity_curve,
                'plots': plots,
                'summary': self._generate_summary()
            }
            
            logger.info("Backtest completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            return {'error': str(e)}
    
    def _get_historical_data(self, start_date: str, end_date: str) -> Optional[Dict]:
        """Fetch historical data for NIFTY50 stocks"""
        try:
            # NIFTY50 symbols for yfinance
            nifty50_symbols = [
                "ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS",
                "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
                "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS",
                "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS",
                "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS",
                "HINDUNILVR.NS", "HDFC.NS", "ICICIBANK.NS", "ITC.NS",
                "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS",
                "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS",
                "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS",
                "SHREECEM.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS",
                "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS",
                "TITAN.NS", "UPL.NS", "ULTRACEMCO.NS", "WIPRO.NS"
            ]
            
            data = {}
            
            # Fetch data for each stock
            for symbol in nifty50_symbols[:20]:  # Limit to first 20 for demo
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(start=start_date, end=end_date)
                    
                    if not hist.empty:
                        # Calculate daily returns and other metrics
                        hist['Daily_Return'] = hist['Close'].pct_change()
                        hist['Volume_MA'] = hist['Volume'].rolling(window=20).mean()
                        hist['High_Volume'] = hist['Volume'] > hist['Volume_MA']
                        
                        data[symbol.replace('.NS', '')] = hist
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch data for {symbol}: {e}")
                    continue
            
            logger.info(f"Fetched historical data for {len(data)} stocks")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    def _simulate_strategy(self, historical_data: Dict):
        """Simulate the 9:15 strategy on historical data"""
        try:
            # Get all trading dates
            all_dates = set()
            for stock_data in historical_data.values():
                all_dates.update(stock_data.index.date)
            
            trading_dates = sorted(list(all_dates))
            
            current_capital = self.initial_capital
            self.equity_curve = [current_capital]
            
            for date in trading_dates:
                # Skip weekends
                if date.weekday() >= 5:
                    continue
                
                # Simulate daily strategy
                trade_result = self._simulate_daily_trade(date, historical_data, current_capital)
                
                if trade_result:
                    self.trades.append(trade_result)
                    current_capital = trade_result['final_capital']
                
                self.equity_curve.append(current_capital)
                
                # Calculate daily return
                if len(self.equity_curve) > 1:
                    daily_return = (current_capital - self.equity_curve[-2]) / self.equity_curve[-2]
                    self.daily_returns.append(daily_return)
            
            logger.info(f"Simulated {len(self.trades)} trades over {len(trading_dates)} trading days")
            
        except Exception as e:
            logger.error(f"Error in strategy simulation: {e}")
    
    def _simulate_daily_trade(self, date: datetime.date, historical_data: Dict, capital: float) -> Optional[Dict]:
        """Simulate a single day's trade"""
        try:
            # Find gainers for the day
            gainers = []
            
            for symbol, data in historical_data.items():
                try:
                    # Get data for the specific date
                    if date not in data.index.date:
                        continue
                    
                    day_data = data[data.index.date == date].iloc[0]
                    
                    # Calculate gain (using open to high as proxy for pre-market gain)
                    if day_data['Open'] > 0:
                        gain_percent = ((day_data['High'] - day_data['Open']) / day_data['Open']) * 100
                        
                        if gain_percent > 0:
                            gainers.append({
                                'symbol': symbol,
                                'gain_percent': gain_percent,
                                'open': day_data['Open'],
                                'high': day_data['High'],
                                'close': day_data['Close'],
                                'volume': day_data['Volume']
                            })
                
                except Exception as e:
                    continue
            
            if not gainers:
                return None
            
            # Sort by gain percentage
            gainers.sort(key=lambda x: x['gain_percent'], reverse=True)
            
            # Select top gainer that meets criteria
            selected_stock = None
            for gainer in gainers[:5]:  # Check top 5 gainers
                # Simulate PCR check (using random values for demo)
                pcr = np.random.uniform(0.5, 2.0)  # Random PCR simulation
                
                if self.pcr_min <= pcr <= self.pcr_max:
                    selected_stock = gainer
                    selected_stock['pcr'] = pcr
                    break
            
            if not selected_stock:
                return None
            
            # Simulate trade execution
            return self._simulate_trade_execution(date, selected_stock, capital)
            
        except Exception as e:
            logger.error(f"Error simulating daily trade for {date}: {e}")
            return None
    
    def _simulate_trade_execution(self, date: datetime.date, stock: Dict, capital: float) -> Dict:
        """Simulate trade execution and monitoring"""
        try:
            # Simulate option price (using simplified model)
            base_price = 50.0  # Base option price
            volatility_factor = np.random.uniform(0.8, 1.2)
            entry_price = base_price * volatility_factor
            
            # Calculate position size (1 lot for now)
            quantity = 1
            trade_value = entry_price * quantity
            
            if trade_value > capital:
                return None  # Insufficient capital
            
            # Simulate price movement during the day
            # Using simplified random walk with bias toward profit target
            price_path = [entry_price]
            current_price = entry_price
            
            # Simulate intraday movement (375 minutes = 6.25 hours)
            for minute in range(375):
                # Add random movement with slight upward bias
                change = np.random.normal(0.001, 0.02)  # 0.1% mean, 2% std
                current_price *= (1 + change)
                price_path.append(current_price)
                
                # Check if profit target reached
                profit_percent = ((current_price - entry_price) / entry_price) * 100
                if profit_percent >= self.profit_target:
                    exit_price = current_price
                    exit_time = minute
                    break
            else:
                # If target not reached, exit at market close
                exit_price = current_price
                exit_time = 375
            
            # Calculate final PnL
            pnl = (exit_price - entry_price) * quantity
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100
            final_capital = capital + pnl
            
            trade_result = {
                'date': date.isoformat(),
                'symbol': stock['symbol'],
                'pre_market_gain': stock['gain_percent'],
                'pcr': stock['pcr'],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'quantity': quantity,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'exit_time_minutes': exit_time,
                'target_reached': pnl_percent >= self.profit_target,
                'initial_capital': capital,
                'final_capital': final_capital
            }
            
            return trade_result
            
        except Exception as e:
            logger.error(f"Error in trade execution simulation: {e}")
            return None
    
    def _calculate_performance(self) -> Dict:
        """Calculate performance metrics"""
        try:
            if not self.trades:
                return {'error': 'No trades to analyze'}
            
            # Basic metrics
            total_trades = len(self.trades)
            winning_trades = len([t for t in self.trades if t['pnl'] > 0])
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # PnL metrics
            total_pnl = sum(t['pnl'] for t in self.trades)
            avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
            best_trade = max(self.trades, key=lambda x: x['pnl'])['pnl']
            worst_trade = min(self.trades, key=lambda x: x['pnl'])['pnl']
            
            # Return metrics
            total_return = ((self.equity_curve[-1] - self.initial_capital) / self.initial_capital) * 100
            
            # Risk metrics
            if self.daily_returns:
                returns_array = np.array(self.daily_returns)
                volatility = np.std(returns_array) * np.sqrt(252) * 100  # Annualized
                sharpe_ratio = (np.mean(returns_array) * 252) / (np.std(returns_array) * np.sqrt(252)) if np.std(returns_array) > 0 else 0
                
                # Maximum drawdown
                equity_array = np.array(self.equity_curve)
                running_max = np.maximum.accumulate(equity_array)
                drawdown = (equity_array - running_max) / running_max
                max_drawdown = np.min(drawdown) * 100
            else:
                volatility = 0
                sharpe_ratio = 0
                max_drawdown = 0
            
            performance = {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(total_pnl, 2),
                'avg_pnl_per_trade': round(avg_pnl, 2),
                'best_trade': round(best_trade, 2),
                'worst_trade': round(worst_trade, 2),
                'total_return': round(total_return, 2),
                'initial_capital': self.initial_capital,
                'final_capital': round(self.equity_curve[-1], 2),
                'volatility': round(volatility, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown, 2)
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"Error calculating performance: {e}")
            return {'error': str(e)}
    
    def _generate_plots(self) -> Dict:
        """Generate performance visualization plots"""
        try:
            plots = {}
            
            # Equity curve plot
            fig_equity = go.Figure()
            fig_equity.add_trace(go.Scatter(
                y=self.equity_curve,
                mode='lines',
                name='Equity Curve',
                line=dict(color='blue', width=2)
            ))
            
            fig_equity.update_layout(
                title='Equity Curve - 9:15 Strategy Backtest',
                xaxis_title='Trading Days',
                yaxis_title='Portfolio Value (₹)',
                hovermode='x unified'
            )
            
            plots['equity_curve'] = fig_equity.to_html(include_plotlyjs='cdn')
            
            # PnL distribution
            if self.trades:
                pnl_values = [t['pnl'] for t in self.trades]
                
                fig_pnl = go.Figure(data=[go.Histogram(x=pnl_values, nbinsx=20)])
                fig_pnl.update_layout(
                    title='PnL Distribution',
                    xaxis_title='PnL (₹)',
                    yaxis_title='Frequency'
                )
                
                plots['pnl_distribution'] = fig_pnl.to_html(include_plotlyjs='cdn')
            
            # Monthly returns
            if self.trades:
                trades_df = pd.DataFrame(self.trades)
                trades_df['date'] = pd.to_datetime(trades_df['date'])
                trades_df['month'] = trades_df['date'].dt.to_period('M')
                
                monthly_pnl = trades_df.groupby('month')['pnl'].sum()
                
                fig_monthly = go.Figure(data=[
                    go.Bar(x=monthly_pnl.index.astype(str), y=monthly_pnl.values)
                ])
                fig_monthly.update_layout(
                    title='Monthly PnL',
                    xaxis_title='Month',
                    yaxis_title='PnL (₹)'
                )
                
                plots['monthly_returns'] = fig_monthly.to_html(include_plotlyjs='cdn')
            
            return plots
            
        except Exception as e:
            logger.error(f"Error generating plots: {e}")
            return {}
    
    def _generate_summary(self) -> str:
        """Generate backtest summary report"""
        try:
            if not self.trades:
                return "No trades executed during backtest period."
            
            performance = self._calculate_performance()
            
            summary = f"""
9:15 Strategy Backtest Summary
{'='*40}

Strategy Parameters:
- PCR Range: {self.pcr_min} - {self.pcr_max}
- Profit Target: {self.profit_target}%
- Initial Capital: ₹{self.initial_capital:,.2f}

Performance Results:
- Total Trades: {performance['total_trades']}
- Win Rate: {performance['win_rate']}%
- Total Return: {performance['total_return']}%
- Final Capital: ₹{performance['final_capital']:,.2f}
- Sharpe Ratio: {performance['sharpe_ratio']}
- Maximum Drawdown: {performance['max_drawdown']}%

Trade Analysis:
- Average PnL per Trade: ₹{performance['avg_pnl_per_trade']:,.2f}
- Best Trade: ₹{performance['best_trade']:,.2f}
- Worst Trade: ₹{performance['worst_trade']:,.2f}
- Total PnL: ₹{performance['total_pnl']:,.2f}

Risk Metrics:
- Annualized Volatility: {performance['volatility']}%
- Sharpe Ratio: {performance['sharpe_ratio']}
- Max Drawdown: {performance['max_drawdown']}%
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def save_results(self, filepath: str):
        """Save backtest results to file"""
        try:
            results = {
                'performance': self._calculate_performance(),
                'trades': self.trades,
                'equity_curve': self.equity_curve,
                'summary': self._generate_summary(),
                'config': self.config
            }
            
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Backtest results saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")

def run_quick_backtest(config: Dict, months: int = 6) -> Dict:
    """Run a quick backtest for the specified number of months"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        engine = BacktestEngine(config)
        results = engine.run_backtest(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Quick backtest failed: {e}")
        return {'error': str(e)}