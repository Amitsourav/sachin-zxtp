#!/bin/bash

# 🌅 Morning Trading Bot Startup Script
# Run this at 8:30 AM for 9:15 AM paper trading test

echo "🤖 Starting Paper Trading Bot with Live Data..."
echo "📅 Date: $(date)"
echo ""

# Navigate to project directory
cd "/Users/sumanprasad/Downloads/sachin zxtp/options_trading_bot"

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes (cleanup)
echo "🧹 Cleaning up any existing processes..."
pkill -f "python3 main.py" 2>/dev/null || true
pkill -f "python3 app.py" 2>/dev/null || true

# Wait a moment
sleep 2

echo ""
echo "🚀 Starting Trading Bot..."
python3 main.py &
TRADING_PID=$!

echo "📊 Starting Web Dashboard..."
cd web_interface
python3 app.py &
WEB_PID=$!

echo ""
echo "✅ Both services started successfully!"
echo ""
echo "🔗 Web Dashboard: http://localhost:8080"
echo "📱 Trading Bot PID: $TRADING_PID"
echo "🌐 Web Server PID: $WEB_PID"
echo ""
echo "📋 What to expect:"
echo "  • Bot will wait until 9:15 AM to execute"
echo "  • Use web dashboard to monitor status"
echo "  • Check logs/trading_bot.log for details"
echo "  • Bot uses PAPER TRADING (no real money)"
echo ""
echo "⏰ Market opens at 9:15 AM - Bot will execute automatically"
echo "🛑 To stop: Press Ctrl+C or run: pkill -f 'python3 main.py'"
echo ""

# Keep script running to show status
echo "💬 Live status updates:"
tail -f logs/trading_bot.log 2>/dev/null || echo "Log file will appear when bot starts..."