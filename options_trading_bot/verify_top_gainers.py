#!/usr/bin/env python3
"""
Verify actual top gainers in NIFTY50 right now
"""

from kiteconnect import KiteConnect
import yaml
from datetime import datetime

def verify_top_gainers():
    # Load config
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
    kite = KiteConnect(api_key=config['broker']['api_key'])
    kite.set_access_token(config['broker']['access_token'])
    
    print(f"🕐 Checking NIFTY50 top gainers at {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    
    # Complete NIFTY50 list with SHRIRAMFIN
    nifty50 = [
        'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 'NSE:ICICIBANK',
        'NSE:KOTAKBANK', 'NSE:SBIN', 'NSE:BHARTIARTL', 'NSE:ITC', 'NSE:AXISBANK',
        'NSE:LT', 'NSE:BAJFINANCE', 'NSE:WIPRO', 'NSE:MARUTI', 'NSE:HCLTECH',
        'NSE:ASIANPAINT', 'NSE:ULTRACEMCO', 'NSE:TITAN', 'NSE:SUNPHARMA', 'NSE:TECHM',
        'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:M&M',
        'NSE:HINDUNILVR', 'NSE:ADANIPORTS', 'NSE:COALINDIA', 'NSE:DIVISLAB', 'NSE:DRREDDY',
        'NSE:UPL', 'NSE:ONGC', 'NSE:JSWSTEEL', 'NSE:GRASIM', 'NSE:BPCL',
        'NSE:CIPLA', 'NSE:EICHERMOT', 'NSE:MAXHEALTH', 'NSE:BAJAJFINSV', 'NSE:NESTLEIND',
        'NSE:BRITANNIA', 'NSE:TATACONSUM', 'NSE:HINDALCO', 'NSE:SBILIFE', 'NSE:APOLLOHOSP',
        'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT', 'NSE:INDIGO'
    ]
    
    print(f"Scanning {len(nifty50)} stocks...")
    
    # Fetch quotes for all
    try:
        quotes = kite.quote(nifty50)
        
        gainers = []
        losers = []
        errors = []
        
        for symbol in nifty50:
            if symbol in quotes:
                data = quotes[symbol]
                prev_close = data['ohlc']['close']
                ltp = data['last_price']
                
                if prev_close > 0:
                    change_pct = ((ltp - prev_close) / prev_close) * 100
                    
                    stock_data = {
                        'symbol': symbol.split(':')[1],
                        'ltp': ltp,
                        'change': change_pct,
                        'volume': data.get('volume', 0)
                    }
                    
                    if change_pct > 0:
                        gainers.append(stock_data)
                    else:
                        losers.append(stock_data)
            else:
                errors.append(symbol)
        
        # Sort gainers by percentage
        gainers.sort(key=lambda x: x['change'], reverse=True)
        
        print(f"\n📈 TOP 10 GAINERS:")
        print("-" * 70)
        print(f"{'Rank':<5} {'Symbol':<15} {'LTP':<12} {'Change %':<12} {'Volume':<15}")
        print("-" * 70)
        
        for i, stock in enumerate(gainers[:10], 1):
            print(f"{i:<5} {stock['symbol']:<15} ₹{stock['ltp']:<11.2f} {stock['change']:+11.2f}% {stock['volume']:>14,}")
            
            # Highlight SHRIRAMFIN if present
            if stock['symbol'] == 'SHRIRAMFIN':
                print(f"      ⬆️  SHRIRAMFIN found at position #{i}")
        
        # Check if SHRIRAMFIN is in the list
        shriram_found = False
        for stock in gainers:
            if stock['symbol'] == 'SHRIRAMFIN':
                shriram_found = True
                rank = gainers.index(stock) + 1
                print(f"\n🔍 SHRIRAMFIN Details:")
                print(f"   Rank: #{rank} out of {len(gainers)} gainers")
                print(f"   Price: ₹{stock['ltp']:.2f}")
                print(f"   Change: {stock['change']:+.2f}%")
                print(f"   Volume: {stock['volume']:,}")
                break
        
        if not shriram_found:
            # Check in losers
            for stock in losers:
                if stock['symbol'] == 'SHRIRAMFIN':
                    print(f"\n❌ SHRIRAMFIN is NEGATIVE today:")
                    print(f"   Price: ₹{stock['ltp']:.2f}")
                    print(f"   Change: {stock['change']:.2f}%")
                    break
        
        if errors:
            print(f"\n⚠️  Failed to fetch: {errors}")
            
        # Show what the script would pick
        if gainers:
            print(f"\n🎯 SCRIPT WOULD SELECT: {gainers[0]['symbol']} (+{gainers[0]['change']:.2f}%)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_top_gainers()