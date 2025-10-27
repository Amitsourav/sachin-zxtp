#!/usr/bin/env python3
"""
Test fetching actual option chain with correct expiry from Zerodha
"""

from kiteconnect import KiteConnect
import yaml
from datetime import datetime, timedelta
import pandas as pd

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

kite = KiteConnect(api_key=config['broker']['api_key'])
kite.set_access_token(config['broker']['access_token'])

print("Fetching Option Chain from Zerodha...")
print("=" * 80)

# Get all NFO instruments
print("Loading NFO instruments...")
instruments = kite.instruments("NFO")

# Convert to DataFrame for easier filtering
df = pd.DataFrame(instruments)

# Test with SBILIFE
symbol = "SBILIFE"
print(f"\nSearching options for: {symbol}")

# Filter SBILIFE options
sbilife_options = df[df['name'] == symbol]

# Get unique expiry dates
expiries = sorted(sbilife_options['expiry'].unique())

print(f"\nAvailable Expiries for {symbol}:")
for i, exp in enumerate(expiries[:5]):  # Show first 5 expiries
    days_to_expiry = (exp - datetime.now().date()).days
    print(f"  {i+1}. {exp} ({exp.strftime('%A')}) - {days_to_expiry} days")

# Get tomorrow's date (Oct 28, 2025)
tomorrow = datetime.now().date() + timedelta(days=1)
print(f"\nTomorrow's Date: {tomorrow} ({tomorrow.strftime('%A')})")

# Find weekly expiry (usually Thursday for stocks)
# For index options, it's Wednesday
current_week_expiry = None
for exp in expiries:
    if exp >= tomorrow and exp.weekday() in [2, 3]:  # Wed or Thu
        current_week_expiry = exp
        break

print(f"Current Week Expiry: {current_week_expiry}")

# Get current spot price
quote = kite.quote([f"NSE:{symbol}"])
spot_price = quote[f"NSE:{symbol}"]['last_price']
print(f"\nSpot Price: ₹{spot_price:.2f}")

# Calculate ATM strike
atm_strike = round(spot_price / 50) * 50 if spot_price < 1000 else round(spot_price / 100) * 100
print(f"ATM Strike: {atm_strike}")

# Find specific option contract
print(f"\nSearching for {symbol} {atm_strike} CE expiring {current_week_expiry}...")

# Filter for exact contract
ce_options = sbilife_options[
    (sbilife_options['instrument_type'] == 'CE') &
    (sbilife_options['strike'] == atm_strike) &
    (sbilife_options['expiry'] == current_week_expiry)
]

if not ce_options.empty:
    option = ce_options.iloc[0]
    print(f"\n✅ Found Option Contract:")
    print(f"   Symbol: {option['tradingsymbol']}")
    print(f"   Strike: {option['strike']}")
    print(f"   Expiry: {option['expiry']}")
    print(f"   Lot Size: {option['lot_size']}")
    print(f"   Token: {option['instrument_token']}")
    
    # Get live price for this option
    option_quote = kite.quote([option['instrument_token']])
    if option['instrument_token'] in option_quote:
        opt_data = option_quote[option['instrument_token']]
        print(f"\n📊 Live Option Data:")
        print(f"   LTP: ₹{opt_data['last_price']:.2f}")
        print(f"   Bid: ₹{opt_data['depth']['buy'][0]['price']:.2f}" if opt_data['depth']['buy'] else "   Bid: N/A")
        print(f"   Ask: ₹{opt_data['depth']['sell'][0]['price']:.2f}" if opt_data['depth']['sell'] else "   Ask: N/A")
        print(f"   Volume: {opt_data['volume']:,}")
        print(f"   OI: {opt_data['oi']:,}" if 'oi' in opt_data else "   OI: N/A")
else:
    print("❌ Option contract not found")
    
    # Show available strikes for debugging
    print(f"\nAvailable {symbol} CE strikes for {current_week_expiry}:")
    available = sbilife_options[
        (sbilife_options['instrument_type'] == 'CE') &
        (sbilife_options['expiry'] == current_week_expiry)
    ]['strike'].unique()
    
    for strike in sorted(available)[:10]:
        print(f"  {strike}")

# Also check for tomorrow specifically (Oct 28, 2025)
print(f"\n" + "="*60)
print(f"Checking for Oct 28, 2025 expiry specifically...")

oct28_expiry = datetime(2025, 10, 28).date()
oct28_options = sbilife_options[sbilife_options['expiry'] == oct28_expiry]

if not oct28_options.empty:
    print(f"✅ Found {len(oct28_options)} options expiring Oct 28, 2025")
    
    # Show some CE options
    ce_oct28 = oct28_options[oct28_options['instrument_type'] == 'CE'].head(5)
    print("\nSample CE options for Oct 28:")
    for idx, opt in ce_oct28.iterrows():
        print(f"  {opt['tradingsymbol']} - Strike: {opt['strike']}")
else:
    print(f"❌ No options found expiring Oct 28, 2025")
    
    # Find next available expiry
    next_expiry = None
    for exp in expiries:
        if exp > tomorrow:
            next_expiry = exp
            break
    
    print(f"\nNext available expiry: {next_expiry} ({next_expiry.strftime('%A')})")