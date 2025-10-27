#!/usr/bin/env python3
"""
Quick Start Script for Paper Trading with Live Market Data
Run this to start paper trading immediately!
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     📊 PAPER TRADING WITH LIVE MARKET DATA                  ║
║                                                              ║
║     Practice Trading with Real Prices - Zero Risk!          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

def check_market_hours():
    """Check if market is open"""
    now = datetime.now()
    
    # Check weekend
    if now.weekday() in [5, 6]:
        return False, "Weekend - Market Closed"
    
    # Check time
    current_time = now.time()
    market_open = datetime.strptime("09:15", "%H:%M").time()
    market_close = datetime.strptime("15:30", "%H:%M").time()
    
    if current_time < market_open:
        hours_until = (datetime.combine(now.date(), market_open) - now).seconds // 3600
        mins_until = ((datetime.combine(now.date(), market_open) - now).seconds % 3600) // 60
        return False, f"Market opens at 9:15 AM ({hours_until}h {mins_until}m remaining)"
    elif current_time > market_close:
        return False, "Market closed for today (3:30 PM)"
    else:
        return True, "Market is OPEN!"

# Check market status
is_open, status_msg = check_market_hours()

print(f"📅 Current Time: {datetime.now().strftime('%I:%M %p, %d %b %Y')}")
print(f"📈 Market Status: {status_msg}")
print()

if is_open:
    print("✅ Perfect timing! Market is open for trading.")
else:
    print("⏰ Market is closed, but you can still:")
    print("   • Test the system with simulated data")
    print("   • Review settings and configuration")
    print("   • Practice with historical patterns")

print("\n" + "="*60)
print("CHOOSE YOUR ACTION:")
print("="*60)
print()
print("1. Start Full Trading Bot (Automated)")
print("2. Test Live Data Connection")
print("3. Run Quick Paper Trade Demo")
print("4. Setup Telegram Notifications")
print("5. View Configuration")
print("6. Exit")
print()

choice = input("Enter your choice (1-6): ").strip()

async def start_full_bot():
    """Start the full trading bot"""
    print("\n🚀 Starting Trading Bot...")
    print("   Mode: Paper Trading with Live Data")
    print("   Capital: ₹100,000 (Virtual)")
    print("\n⚠️  The bot will:")
    print("   • Scan market at 9:14 AM")
    print("   • Execute at exactly 9:15:00")
    print("   • Monitor positions throughout the day")
    print("   • Exit at target (8%) or stop loss (30%)")
    
    confirm = input("\nStart bot? (y/n): ").lower()
    if confirm == 'y':
        os.system("python3 main.py")
    else:
        print("Cancelled.")

async def test_live_data():
    """Test live data connection"""
    print("\n🔍 Testing Live Data Connection...")
    os.system("python3 src/data/live_data_fetcher.py")

async def run_demo():
    """Run a quick demo"""
    print("\n📊 Running Quick Demo...")
    
    from src.brokers.live_paper_broker import LivePaperBroker
    
    broker = LivePaperBroker(100000)
    await broker.connect()
    
    print("\n✅ Paper Broker Connected")
    print(f"   Virtual Capital: ₹1,00,000")
    
    # Get some live data
    print("\n📈 Fetching Live Market Data...")
    gainers = await broker.scan_top_gainers()
    
    if gainers:
        print("\nTop Gainers Right Now:")
        for i, g in enumerate(gainers[:3], 1):
            print(f"   {i}. {g['symbol']}: +{g['change_percent']:.2f}%")
    
    pcr = await broker.get_pcr_ratio()
    print(f"\nPut-Call Ratio: {pcr:.2f}")
    
    if 0.7 <= pcr <= 1.5:
        print("Signal: BUY (PCR in range) ✅")
    else:
        print("Signal: WAIT (PCR out of range) ⏸️")
    
    print("\n✅ Demo Complete! System is working perfectly.")
    
    await broker.live_data.nse_fetcher.close()

def setup_telegram():
    """Setup Telegram bot"""
    print("\n📱 Setting up Telegram...")
    os.system("python3 test_telegram.py")

def view_config():
    """View current configuration"""
    print("\n⚙️  Current Configuration:")
    print("-" * 40)
    
    try:
        with open("config/config.yaml", "r") as f:
            print(f.read())
    except FileNotFoundError:
        print("Config file not found. Creating default...")
        os.system("python3 test_telegram.py")

# Execute choice
if choice == "1":
    asyncio.run(start_full_bot())
elif choice == "2":
    asyncio.run(test_live_data())
elif choice == "3":
    asyncio.run(run_demo())
elif choice == "4":
    setup_telegram()
elif choice == "5":
    view_config()
elif choice == "6":
    print("\nGoodbye! Happy Trading! 📈")
else:
    print("\nInvalid choice. Please run again.")

print("\n" + "="*60)
print("Need help? Check these files:")
print("  • PAPER_TRADING_LIVE_DATA_GUIDE.md")
print("  • COMPLETE_SYSTEM_STATUS.md")
print("  • TELEGRAM_SETUP_GUIDE.md")
print("="*60)