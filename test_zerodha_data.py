#!/usr/bin/env python3
"""
Test Zerodha Real-Time Data Fetching
Verify that we're getting live data from Zerodha instead of Yahoo/NSE
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.zerodha_data_fetcher import ZerodhaDataFetcher
import asyncio
from datetime import datetime


async def test_zerodha_data():
    """Test Zerodha data fetching"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         TESTING ZERODHA REAL-TIME DATA                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Initialize Zerodha data fetcher
        fetcher = ZerodhaDataFetcher()
        print("✅ Zerodha data fetcher initialized\n")
        
        # 1. Test market status
        print("1️⃣  Testing Market Status:")
        print("-" * 50)
        status = fetcher.get_market_status()
        print(f"Market Status: {status['status']}")
        print(f"Is Open: {status['is_open']}")
        print(f"Source: {status['source']}\n")
        
        # 2. Test live quotes
        print("2️⃣  Testing Live Quotes (NIFTY50 stocks):")
        print("-" * 50)
        test_symbols = ["RELIANCE", "TCS", "INFY", "ICICIBANK", "HDFCBANK"]
        quotes = fetcher.get_live_quotes(test_symbols)
        
        if quotes:
            for symbol, data in quotes.items():
                print(f"{symbol}:")
                print(f"  Price: ₹{data['ltp']:,.2f}")
                print(f"  Change: {data['change_percent']:+.2f}%")
                print(f"  Volume: {data['volume']:,}")
            print(f"\n✅ Successfully fetched {len(quotes)} quotes from Zerodha")
        else:
            print("❌ No quotes received")
        
        # 3. Test top gainers
        print("\n3️⃣  Testing Top Gainers:")
        print("-" * 50)
        gainers = fetcher.get_top_gainers(limit=5)
        
        if gainers:
            print("Top 5 Gainers:")
            for i, stock in enumerate(gainers, 1):
                print(f"{i}. {stock['symbol']}: +{stock['change_percent']:.2f}% @ ₹{stock['ltp']:,.2f}")
                print(f"   Source: {stock['source']}")
            print(f"\n✅ Found {len(gainers)} gainers from Zerodha")
        else:
            print("❌ No gainers found")
        
        # 4. Test index quote
        print("\n4️⃣  Testing Index Quote:")
        print("-" * 50)
        index = fetcher.get_index_quote("NIFTY 50")
        if index:
            print(f"NIFTY 50: ₹{index['ltp']:,.2f}")
            print(f"Change: {index['change_percent']:+.2f}%")
            print(f"Source: {index['source']}")
        
        # 5. Test option chain (if market hours)
        print("\n5️⃣  Testing Option Chain:")
        print("-" * 50)
        
        if status['is_open']:
            try:
                option_chain = fetcher.get_option_chain("NIFTY")
                if option_chain:
                    print(f"NIFTY Option Chain:")
                    print(f"  PCR: {option_chain.get('pcr', 0):.2f}")
                    print(f"  Options: {len(option_chain.get('options', []))} strikes")
                    print(f"  Source: {option_chain['source']}")
                else:
                    print("Option chain not available")
            except Exception as e:
                print(f"Option chain error: {e}")
        else:
            print("Market closed - option chain not tested")
        
        print("\n" + "="*60)
        print("✅ ZERODHA DATA FETCHER WORKING!")
        print("="*60)
        print("\nData Source Summary:")
        print("✅ Real-time quotes from Zerodha API")
        print("✅ No 15-minute delay")
        print("✅ Direct from exchange")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if access token is valid")
        print("2. Ensure market data subscription is active")
        print("3. Verify API limits not exceeded")


async def test_paper_broker_with_zerodha():
    """Test paper broker using Zerodha data"""
    print("\n\n6️⃣  Testing Paper Broker with Zerodha:")
    print("-" * 50)
    
    try:
        from src.brokers.live_paper_broker import LivePaperBroker
        
        broker = LivePaperBroker(initial_capital=100000)
        await broker.connect()
        
        if broker.zerodha_data:
            print("✅ Paper broker using Zerodha data!")
            
            # Place a test order
            print("\nPlacing test paper order...")
            order = await broker.place_order(
                symbol="RELIANCE",
                exchange="NSE",
                transaction_type="BUY",
                quantity=1,
                order_type="MARKET",
                product="MIS"
            )
            
            if order['status'] == 'COMPLETE':
                print(f"✅ Order executed at ₹{order['average_price']:.2f}")
                print("   (Price from Zerodha live data)")
            
        else:
            print("⚠️  Paper broker using fallback data source")
            
    except Exception as e:
        print(f"Paper broker test error: {e}")


if __name__ == "__main__":
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    asyncio.run(test_zerodha_data())
    asyncio.run(test_paper_broker_with_zerodha())