#!/usr/bin/env python3
"""
PRE-MARKET VALIDATOR - Run this at 9:10 AM to ensure everything is perfect
Validates NIFTY50 list and identifies potential top gainers BEFORE 9:15
"""

from kiteconnect import KiteConnect
import yaml
from datetime import datetime
import json

def validate_before_market_open():
    # Load config
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
    kite = KiteConnect(api_key=config['broker']['api_key'])
    kite.set_access_token(config['broker']['access_token'])
    
    print("=" * 80)
    print(f"⚡ PRE-MARKET VALIDATION - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    
    # Complete NIFTY50 list
    nifty50_primary = [
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
    
    print(f"Validating {len(nifty50_primary)} NIFTY50 stocks...")
    
    # Step 1: Verify all stocks are accessible
    print("\n📋 STOCK VALIDATION:")
    print("-" * 40)
    
    valid_stocks = []
    invalid_stocks = []
    
    # Check in batches
    batch_size = 10
    for i in range(0, len(nifty50_primary), batch_size):
        batch = nifty50_primary[i:i+batch_size]
        try:
            quotes = kite.quote(batch)
            for symbol in batch:
                if symbol in quotes:
                    valid_stocks.append(symbol)
                else:
                    invalid_stocks.append(symbol)
                    print(f"❌ {symbol} - NOT FOUND")
        except Exception as e:
            print(f"⚠️  Batch error: {e}")
            for symbol in batch:
                invalid_stocks.append(symbol)
    
    print(f"\n✅ Valid stocks: {len(valid_stocks)}/50")
    if invalid_stocks:
        print(f"❌ Invalid stocks: {invalid_stocks}")
    
    # Step 2: Check pre-market gainers
    print("\n📈 PRE-MARKET MOVERS (Preview):")
    print("-" * 40)
    
    try:
        # Get quotes for all valid stocks
        all_quotes = {}
        for i in range(0, len(valid_stocks), batch_size):
            batch = valid_stocks[i:i+batch_size]
            batch_quotes = kite.quote(batch)
            all_quotes.update(batch_quotes)
        
        # Calculate gains
        gainers = []
        for symbol in valid_stocks:
            if symbol in all_quotes:
                data = all_quotes[symbol]
                prev_close = data['ohlc']['close']
                ltp = data['last_price']
                
                if prev_close > 0:
                    change_pct = ((ltp - prev_close) / prev_close) * 100
                    gainers.append({
                        'symbol': symbol.split(':')[1],
                        'ltp': ltp,
                        'change': change_pct,
                        'volume': data.get('volume', 0)
                    })
        
        # Sort by gain
        gainers.sort(key=lambda x: x['change'], reverse=True)
        
        # Show top 10
        print(f"{'Rank':<5} {'Symbol':<15} {'LTP':<12} {'Change %':<10}")
        print("-" * 40)
        for i, stock in enumerate(gainers[:10], 1):
            marker = "🔥" if stock['change'] > 2 else "📈"
            print(f"{i:<5} {stock['symbol']:<15} ₹{stock['ltp']:<11.2f} {stock['change']:+9.2f}% {marker}")
        
        # Special alerts
        print("\n⚠️  ALERTS:")
        if gainers[0]['change'] > 5:
            print(f"🚨 HUGE MOVER: {gainers[0]['symbol']} is up {gainers[0]['change']:.2f}%!")
        
        # Check for SHRIRAMFIN specifically
        shriram_found = False
        for i, stock in enumerate(gainers):
            if stock['symbol'] == 'SHRIRAMFIN':
                shriram_found = True
                print(f"📍 SHRIRAMFIN at position #{i+1} with +{stock['change']:.2f}%")
                break
        
        if not shriram_found:
            print("⚠️  SHRIRAMFIN not found in gainers!")
        
        # Save validation result
        validation_result = {
            'timestamp': datetime.now().isoformat(),
            'valid_stocks': len(valid_stocks),
            'top_gainer': gainers[0] if gainers else None,
            'top_5': gainers[:5] if gainers else []
        }
        
        with open('pre_market_validation.json', 'w') as f:
            json.dump(validation_result, f, indent=2)
        
        print("\n✅ Validation complete. Results saved to pre_market_validation.json")
        
        # Final recommendations
        print("\n🎯 RECOMMENDATIONS:")
        print("-" * 40)
        
        if gainers[0]['change'] > 3:
            print(f"1. {gainers[0]['symbol']} looks very strong (+{gainers[0]['change']:.2f}%)")
        
        if len(gainers) > 1 and gainers[1]['change'] > 2:
            print(f"2. {gainers[1]['symbol']} is also strong (+{gainers[1]['change']:.2f}%)")
        
        print(f"\n⏰ Run BULLETPROOF_915_strategy.py at exactly 9:15:00")
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    validate_before_market_open()