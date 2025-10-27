#!/usr/bin/env python3
"""
Python script to start the trading bot for morning session
Run this at 8:30 AM for 9:15 AM execution
"""

import asyncio
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("\n" + "="*60)
    print("🌅 MORNING TRADING BOT STARTER")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    print("🎯 Mode: Paper Trading with Live Data")
    print("💰 Capital: ₹1,00,000 (Virtual)")
    print("="*60 + "\n")

def check_dependencies():
    """Check if required modules are available"""
    print("🔍 Checking dependencies...")
    
    try:
        import pandas
        import yfinance
        import pydantic
        print("✅ Core dependencies: OK")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    
    return True

def start_web_dashboard():
    """Start the web dashboard in background"""
    print("📊 Starting web dashboard...")
    
    web_dir = Path(__file__).parent / "web_interface"
    if not web_dir.exists():
        print("❌ Web interface directory not found")
        return None
    
    try:
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=web_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ Web dashboard started (PID: {process.pid})")
        print("🔗 Dashboard URL: http://localhost:8080")
        return process
    except Exception as e:
        print(f"❌ Failed to start web dashboard: {e}")
        return None

async def start_trading_bot():
    """Start the main trading bot"""
    print("🤖 Starting trading bot...")
    
    # Import here to avoid issues if modules not ready
    try:
        from main import TradingBotOrchestrator
        
        # Create and run orchestrator
        orchestrator = TradingBotOrchestrator()
        await orchestrator.main()
        
    except Exception as e:
        print(f"❌ Trading bot failed: {e}")
        raise

def monitor_market_hours():
    """Check if it's appropriate time to start"""
    now = datetime.now()
    current_time = now.time()
    
    # Check if weekend
    if now.weekday() in [5, 6]:  # Saturday, Sunday
        print("⚠️  Weekend detected - markets are closed")
        print("💡 Bot will still start for testing purposes")
        return True
    
    # Check if too early (before 8:00 AM)
    if current_time.hour < 8:
        print("⚠️  Very early start - market opens at 9:15 AM")
        print("💡 Recommended start time: 8:30 AM")
    
    # Check if too late (after 4:00 PM)
    elif current_time.hour > 16:
        print("⚠️  Markets closed for today")
        print("💡 Next trading session: Tomorrow 9:15 AM")
    
    return True

def cleanup_existing_processes():
    """Clean up any existing bot processes"""
    print("🧹 Cleaning up existing processes...")
    
    try:
        # Kill existing Python processes that might be running the bot
        subprocess.run(["pkill", "-f", "main.py"], capture_output=True)
        subprocess.run(["pkill", "-f", "app.py"], capture_output=True)
        time.sleep(2)
        print("✅ Cleanup completed")
    except Exception:
        print("⚠️  Cleanup skipped (processes may not exist)")

async def main():
    """Main startup function"""
    print_banner()
    
    # Pre-flight checks
    if not check_dependencies():
        print("❌ Dependencies check failed")
        return
    
    if not monitor_market_hours():
        print("❌ Market hours check failed")
        return
    
    # Cleanup
    cleanup_existing_processes()
    
    # Start web dashboard first
    web_process = start_web_dashboard()
    
    if web_process:
        # Give web server time to start
        print("⏳ Waiting for web server to initialize...")
        time.sleep(3)
    
    try:
        # Start trading bot
        print("\n🚀 Launching trading bot...")
        print("📋 What happens next:")
        print("  • Bot waits for 9:15 AM")
        print("  • Scans NIFTY50 at 9:14 AM")
        print("  • Executes trade at 9:15 AM")
        print("  • Monitors position until exit")
        print("\n💻 Monitor via:")
        print("  • Web Dashboard: http://localhost:8080")
        print("  • Console: Live updates below")
        print("  • Logs: logs/trading_bot.log")
        print("\n" + "="*60)
        
        await start_trading_bot()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot stopped by user")
    except Exception as e:
        print(f"\n\n❌ Bot stopped due to error: {e}")
    finally:
        # Cleanup
        if web_process:
            print("🧹 Stopping web dashboard...")
            web_process.terminate()
        print("✅ Shutdown complete")

if __name__ == "__main__":
    # Check if running from correct directory
    if not Path("main.py").exists():
        print("❌ Please run from the trading bot directory")
        print("💡 Use: cd '/Users/sumanprasad/Downloads/sachin zxtp/options_trading_bot'")
        sys.exit(1)
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)