#!/bin/bash

# ========================================================
#  REAL-TIME PAPER TRADING FOR TOMORROW'S MARKET
#  With NSE Direct Data (No Delays!)
# ========================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     9:15 STRATEGY - REAL-TIME NSE DATA TRADING              ║"
echo "║                                                              ║"
echo "║  Features:                                                   ║"
echo "║  ✅ REAL-TIME NSE data (when market is open)                ║"
echo "║  ✅ Automatic fallback to Yahoo if NSE fails                ║"
echo "║  ✅ Execute at exactly 9:15:00 AM                           ║"
echo "║  ✅ 30% stop loss protection                                ║"
echo "║  ✅ Web dashboard at localhost:8080                         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project
cd /Users/sumanprasad/Downloads/sachin\ zxtp/options_trading_bot

# Check dependencies
echo "📦 Checking dependencies..."
pip3 install -q pytz yfinance requests pandas 2>/dev/null

# Kill existing processes
echo "🔧 Cleaning up..."
lsof -ti:8080 | xargs kill -9 2>/dev/null

# Start dashboard
echo "🚀 Starting Web Dashboard..."
cd web_interface
python3 app.py &
DASHBOARD_PID=$!
cd ..

echo "✅ Dashboard: http://localhost:8080 (demo/demo123)"
sleep 2

# Choose trading mode
echo ""
echo "Select Trading Mode:"
echo "1) Real-time NSE data (Best for market hours)"
echo "2) Yahoo Finance data (Works anytime, 15-min delay)"
echo -n "Enter choice (1 or 2): "
read choice

if [ "$choice" == "1" ]; then
    echo "📡 Starting with REAL-TIME NSE data..."
    python3 paper_trade_live_realtime.py &
    TRADING_PID=$!
else
    echo "📡 Starting with Yahoo Finance data..."
    python3 paper_trade_live.py &
    TRADING_PID=$!
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  SYSTEM READY FOR TRADING!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Dashboard: http://localhost:8080"
echo "📝 Log: realtime_paper_trading.log"
echo "⏰ Trade Time: 9:15:00 AM"
echo ""
echo "Data Sources:"
echo "  Primary: NSE Direct (real-time during market hours)"
echo "  Fallback: Yahoo Finance (15-min delay)"
echo ""
echo "Press Ctrl+C to stop"

# Cleanup function
cleanup() {
    echo "Stopping..."
    kill $DASHBOARD_PID 2>/dev/null
    kill $TRADING_PID 2>/dev/null
    echo "✅ Stopped"
    exit 0
}

trap cleanup INT

while true; do
    sleep 1
done