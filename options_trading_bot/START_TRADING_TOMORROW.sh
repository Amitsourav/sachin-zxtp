#!/bin/bash

# =====================================================
#  START PAPER TRADING FOR TOMORROW'S LIVE MARKET
#  Safe paper trading with real market data
# =====================================================

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       9:15 STRATEGY - LIVE PAPER TRADING SYSTEM         ║"
echo "║                                                          ║"
echo "║  This will:                                              ║"
echo "║  1. Start the web dashboard on localhost:8080           ║"
echo "║  2. Run paper trading with live market data             ║"
echo "║  3. Execute at exactly 9:15:00 AM                       ║"
echo "║  4. Include 30% stop loss protection                    ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project directory
cd /Users/sumanprasad/Downloads/sachin\ zxtp/options_trading_bot

# Install required packages if needed
echo "📦 Checking dependencies..."
pip3 install -q yfinance requests pytz flask flask-socketio flask-login 2>/dev/null

# Kill any existing processes on port 8080
echo "🔧 Cleaning up old processes..."
lsof -ti:8080 | xargs kill -9 2>/dev/null

# Start the dashboard
echo "🚀 Starting Web Dashboard..."
cd web_interface
python3 app.py &
DASHBOARD_PID=$!

echo "✅ Dashboard started at: http://localhost:8080"
echo "   Login: demo / demo123"
echo ""

# Wait for dashboard to initialize
sleep 3

# Start the paper trading engine
echo "📈 Starting Paper Trading Engine..."
cd ..
python3 paper_trade_live.py &
TRADING_PID=$!

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  SYSTEM READY FOR TOMORROW'S TRADING!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📊 Dashboard: http://localhost:8080"
echo "📝 Logs: paper_trading.log"
echo "⏰ Trade Time: 9:15:00 AM IST"
echo ""
echo "Press Ctrl+C to stop all processes"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping trading system..."
    kill $DASHBOARD_PID 2>/dev/null
    kill $TRADING_PID 2>/dev/null
    echo "✅ All processes stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT

# Keep script running
while true; do
    sleep 1
done