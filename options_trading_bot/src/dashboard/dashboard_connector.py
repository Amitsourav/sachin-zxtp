"""
Dashboard Connector - Bridges Trading Engine with Web Dashboard
Provides real-time updates via WebSocket
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask_socketio import SocketIO, emit

logger = logging.getLogger(__name__)


class DashboardConnector:
    """
    Connects trading engine to web dashboard
    Sends real-time updates via WebSocket
    """
    
    def __init__(self, socketio: Optional[SocketIO] = None):
        self.socketio = socketio
        self.connected_clients = set()
        self.latest_data = {
            'status': 'STOPPED',
            'positions': [],
            'pnl': {'realized': 0, 'unrealized': 0, 'total': 0},
            'trades': [],
            'risk_metrics': {},
            'market_data': {}
        }
        
    def set_socketio(self, socketio: SocketIO):
        """Set SocketIO instance"""
        self.socketio = socketio
        
    async def emit_update(self, event: str, data: Any):
        """Emit update to all connected clients"""
        if self.socketio:
            try:
                self.socketio.emit(event, data, broadcast=True)
                logger.debug(f"Emitted {event}: {data}")
            except Exception as e:
                logger.error(f"Failed to emit {event}: {e}")
                
    async def send_status_update(self, status: str, details: Dict[str, Any] = None):
        """Send bot status update"""
        update = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.latest_data['status'] = status
        await self.emit_update('status_update', update)
        
    async def send_position_update(self, positions: list):
        """Send position updates"""
        self.latest_data['positions'] = positions
        await self.emit_update('position_update', {
            'positions': positions,
            'timestamp': datetime.now().isoformat()
        })
        
    async def send_pnl_update(self, pnl: Dict[str, float]):
        """Send P&L update"""
        self.latest_data['pnl'] = pnl
        await self.emit_update('pnl_update', {
            'pnl': pnl,
            'timestamp': datetime.now().isoformat()
        })
        
    async def send_trade_alert(self, trade: Dict[str, Any]):
        """Send trade execution alert"""
        self.latest_data['trades'].append(trade)
        
        # Keep only last 50 trades
        if len(self.latest_data['trades']) > 50:
            self.latest_data['trades'] = self.latest_data['trades'][-50:]
            
        await self.emit_update('trade_alert', {
            'trade': trade,
            'timestamp': datetime.now().isoformat()
        })
        
    async def send_risk_update(self, risk_metrics: Dict[str, Any]):
        """Send risk metrics update"""
        self.latest_data['risk_metrics'] = risk_metrics
        await self.emit_update('risk_update', {
            'metrics': risk_metrics,
            'timestamp': datetime.now().isoformat()
        })
        
    async def send_market_data(self, market_data: Dict[str, Any]):
        """Send market data update"""
        self.latest_data['market_data'] = market_data
        await self.emit_update('market_data', {
            'data': market_data,
            'timestamp': datetime.now().isoformat()
        })
        
    async def send_error_alert(self, error: str, severity: str = 'warning'):
        """Send error alert to dashboard"""
        await self.emit_update('error_alert', {
            'error': error,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        })
        
    async def send_log_message(self, message: str, level: str = 'info'):
        """Send log message to dashboard"""
        await self.emit_update('log_message', {
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        })
        
    def get_current_state(self) -> Dict[str, Any]:
        """Get current state for new connections"""
        return {
            'data': self.latest_data,
            'timestamp': datetime.now().isoformat()
        }
        
    async def handle_command(self, command: str, params: Dict[str, Any] = None):
        """Handle commands from dashboard"""
        logger.info(f"Received command: {command} with params: {params}")
        
        # Commands will be processed by the orchestrator
        # This is just the interface
        
        responses = {
            'start': "Starting trading bot...",
            'stop': "Stopping trading bot...",
            'pause': "Pausing trading...",
            'resume': "Resuming trading...",
            'emergency_stop': "Emergency stop initiated!",
            'get_status': self.get_current_state()
        }
        
        response = responses.get(command, "Unknown command")
        
        await self.emit_update('command_response', {
            'command': command,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return response


class TradingEngineInterface:
    """
    Interface for trading engine to send updates to dashboard
    """
    
    def __init__(self, connector: DashboardConnector):
        self.connector = connector
        
    async def on_bot_start(self):
        """Called when bot starts"""
        await self.connector.send_status_update('RUNNING', {
            'message': 'Trading bot started successfully'
        })
        await self.connector.send_log_message('Trading bot initialized', 'info')
        
    async def on_bot_stop(self):
        """Called when bot stops"""
        await self.connector.send_status_update('STOPPED', {
            'message': 'Trading bot stopped'
        })
        
    async def on_trade_executed(self, trade: Dict[str, Any]):
        """Called when trade is executed"""
        await self.connector.send_trade_alert(trade)
        await self.connector.send_log_message(
            f"Trade executed: {trade['symbol']} - {trade['transaction_type']} {trade['quantity']} @ {trade['price']:.2f}",
            'success'
        )
        
    async def on_position_update(self, positions: list):
        """Called when positions change"""
        await self.connector.send_position_update(positions)
        
    async def on_pnl_update(self, pnl: Dict[str, float]):
        """Called when P&L changes"""
        await self.connector.send_pnl_update(pnl)
        
    async def on_risk_alert(self, alert: str):
        """Called on risk alerts"""
        await self.connector.send_error_alert(alert, 'warning')
        await self.connector.send_log_message(f"Risk Alert: {alert}", 'warning')
        
    async def on_error(self, error: str):
        """Called on errors"""
        await self.connector.send_error_alert(error, 'error')
        await self.connector.send_log_message(f"Error: {error}", 'error')
        
    async def on_market_scan(self, scan_result: Dict[str, Any]):
        """Called after market scan"""
        await self.connector.send_market_data(scan_result)
        await self.connector.send_log_message(
            f"Market scan complete: Found {scan_result.get('top_gainer', 'N/A')}",
            'info'
        )
        
    async def periodic_update(self, broker, risk_manager):
        """Send periodic updates to dashboard"""
        # Get current positions
        positions = broker.get_positions()
        await self.on_position_update(positions)
        
        # Get P&L
        pnl = broker.get_pnl()
        await self.on_pnl_update(pnl)
        
        # Get risk metrics
        risk_metrics = {
            'daily_loss': risk_manager.daily_loss,
            'max_daily_loss': risk_manager.max_daily_loss,
            'open_positions': risk_manager.open_positions_count,
            'max_positions': risk_manager.max_positions,
            'current_risk': risk_manager.get_current_risk(),
            'risk_level': 'LOW' if risk_manager.get_current_risk() < 0.5 else 'MEDIUM' if risk_manager.get_current_risk() < 0.8 else 'HIGH'
        }
        await self.connector.send_risk_update(risk_metrics)