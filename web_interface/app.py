"""
Simple Flask web dashboard for options trading bot
Designed for non-technical users
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os
from datetime import datetime
import json
from typing import Dict, Any

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simulated bot state (in production, this connects to actual bot)
bot_state = {
    'status': 'stopped',  # stopped, running, paused
    'capital': 100000,
    'current_capital': 100000,
    'daily_pnl': 0,
    'daily_pnl_percent': 0,
    'positions': [],
    'trades_today': 0,
    'last_trade': None,
    'risk_level': 'medium',  # low, medium, high
    'paper_trading': True,
    'notifications': {
        'telegram': False,
        'email': False
    }
}

# Simple user class (in production, use proper authentication)
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html', state=bot_state)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login page"""
    if request.method == 'POST':
        # In production, verify credentials properly
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:  # Basic check
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/status')
@login_required
def get_status():
    """Get current bot status"""
    return jsonify(bot_state)

@app.route('/api/start', methods=['POST'])
@login_required
def start_bot():
    """Start the trading bot"""
    if bot_state['status'] == 'stopped':
        bot_state['status'] = 'running'
        bot_state['last_trade'] = datetime.now().isoformat()
        
        # Emit status update to all connected clients
        socketio.emit('status_update', {'status': 'running'})
        
        return jsonify({'success': True, 'message': 'Bot started successfully'})
    
    return jsonify({'success': False, 'message': 'Bot is already running'})

@app.route('/api/stop', methods=['POST'])
@login_required
def stop_bot():
    """Stop the trading bot"""
    if bot_state['status'] in ['running', 'paused']:
        bot_state['status'] = 'stopped'
        
        socketio.emit('status_update', {'status': 'stopped'})
        
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
    
    return jsonify({'success': False, 'message': 'Bot is not running'})

@app.route('/api/pause', methods=['POST'])
@login_required
def pause_bot():
    """Pause the trading bot"""
    if bot_state['status'] == 'running':
        bot_state['status'] = 'paused'
        
        socketio.emit('status_update', {'status': 'paused'})
        
        return jsonify({'success': True, 'message': 'Bot paused successfully'})
    
    return jsonify({'success': False, 'message': 'Bot is not running'})

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Get or update settings"""
    if request.method == 'POST':
        data = request.json
        
        # Update settings
        if 'risk_level' in data:
            bot_state['risk_level'] = data['risk_level']
        
        if 'paper_trading' in data:
            bot_state['paper_trading'] = data['paper_trading']
        
        if 'notifications' in data:
            bot_state['notifications'].update(data['notifications'])
        
        return jsonify({'success': True, 'message': 'Settings updated'})
    
    # GET request - return current settings
    return jsonify({
        'risk_level': bot_state['risk_level'],
        'paper_trading': bot_state['paper_trading'],
        'notifications': bot_state['notifications']
    })

@app.route('/api/positions')
@login_required
def get_positions():
    """Get current positions"""
    # In production, fetch from actual broker
    sample_positions = [
        {
            'symbol': 'RELIANCE24JAN2800CE',
            'quantity': 250,
            'entry_price': 45.50,
            'current_price': 48.75,
            'pnl': 812.50,
            'pnl_percent': 7.14
        }
    ]
    return jsonify(sample_positions if bot_state['status'] == 'running' else [])

@app.route('/api/trades')
@login_required
def get_trades():
    """Get today's trades"""
    # In production, fetch from database
    sample_trades = [
        {
            'time': '09:15:00',
            'symbol': 'RELIANCE24JAN2800CE',
            'action': 'BUY',
            'quantity': 250,
            'price': 45.50,
            'status': 'completed'
        }
    ]
    return jsonify(sample_trades if bot_state['trades_today'] > 0 else [])

@app.route('/api/performance')
@login_required
def get_performance():
    """Get performance metrics"""
    # In production, calculate from actual trades
    return jsonify({
        'daily': [
            {'date': '2024-01-15', 'pnl': 2500, 'pnl_percent': 2.5},
            {'date': '2024-01-16', 'pnl': -1200, 'pnl_percent': -1.2},
            {'date': '2024-01-17', 'pnl': 1800, 'pnl_percent': 1.8},
            {'date': '2024-01-18', 'pnl': 3200, 'pnl_percent': 3.2},
            {'date': '2024-01-19', 'pnl': 1500, 'pnl_percent': 1.5},
        ],
        'summary': {
            'total_trades': 45,
            'winning_trades': 28,
            'losing_trades': 17,
            'win_rate': 62.22,
            'avg_profit': 2150,
            'avg_loss': -850,
            'best_trade': 4500,
            'worst_trade': -2100,
            'sharpe_ratio': 1.45
        }
    })

@app.route('/api/logs')
@login_required
def get_logs():
    """Get recent log entries"""
    # In production, read from actual log files
    sample_logs = [
        {'timestamp': '2024-01-19 09:14:00', 'level': 'INFO', 'message': 'Starting pre-market scan'},
        {'timestamp': '2024-01-19 09:14:30', 'level': 'INFO', 'message': 'Found top gainer: RELIANCE (+2.3%)'},
        {'timestamp': '2024-01-19 09:14:45', 'level': 'INFO', 'message': 'PCR calculated: 1.12'},
        {'timestamp': '2024-01-19 09:15:00', 'level': 'SUCCESS', 'message': 'Trade executed: RELIANCE 2800 CE'},
    ]
    return jsonify(sample_logs)

# WebSocket events for real-time updates
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'data': 'Connected to trading bot'})

@socketio.on('request_update')
def handle_update_request():
    """Send current state to client"""
    emit('state_update', bot_state)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080, allow_unsafe_werkzeug=True)