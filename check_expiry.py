#!/usr/bin/env python3
"""
Check actual option expiry dates from Zerodha
"""

from kiteconnect import KiteConnect
import yaml
from pathlib import Path
from datetime import datetime
import pandas as pd

# Load config
config_path = Path("config/config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

broker_config = config.get('broker', {})

# Initialize Zerodha
kite = KiteConnect(api_key=broker_config['api_key'])
kite.set_access_token(broker_config['access_token'])

print("""
╔══════════════════════════════════════════════════════════════╗
║           CHECKING OPTION EXPIRY DATES                        ║
╚══════════════════════════════════════════════════════════════╝
""")

try:
    # Get all NFO instruments
    print("Fetching NFO instruments from Zerodha...")
    instruments = kite.instruments("NFO")
    
    # Filter for CIPLA options
    cipla_options = [i for i in instruments if i['name'] == 'CIPLA']
    
    # Get unique expiry dates
    expiry_dates = set()
    for opt in cipla_options:
        expiry_dates.add(opt['expiry'])
    
    # Sort expiry dates
    sorted_expiries = sorted(expiry_dates)
    
    print(f"\n📅 CIPLA Option Expiry Dates Available:")
    print("-" * 40)
    
    for i, expiry in enumerate(sorted_expiries[:5], 1):  # Show next 5 expiries
        day_of_week = expiry.strftime('%A')
        print(f"{i}. {expiry.strftime('%d %B %Y')} ({day_of_week})")
    
    # Find nearest expiry
    today = datetime.now().date()
    nearest_expiry = None
    for expiry in sorted_expiries:
        if expiry >= today:
            nearest_expiry = expiry
            break
    
    print(f"\n✅ Nearest Expiry: {nearest_expiry.strftime('%d %B %Y')}")
    print(f"   Format: CIPLA{nearest_expiry.strftime('%y%b').upper()}{nearest_expiry.day}1650CE")
    
    # Check for other popular stocks
    print("\n📊 Other Stock Options (Next Expiry):")
    print("-" * 40)
    
    stocks = ['RELIANCE', 'TCS', 'INFY', 'ICICIBANK']
    for stock in stocks:
        stock_options = [i for i in instruments if i['name'] == stock]
        if stock_options:
            expiries = sorted(set(opt['expiry'] for opt in stock_options))
            next_expiry = next((e for e in expiries if e >= today), None)
            if next_expiry:
                print(f"{stock}: {next_expiry.strftime('%d-%b-%Y')}")
    
    # Check NIFTY weekly expiries
    print("\n📈 NIFTY Weekly Expiries:")
    print("-" * 40)
    nifty_options = [i for i in instruments if i['name'] == 'NIFTY']
    nifty_expiries = sorted(set(opt['expiry'] for opt in nifty_options))[:4]
    
    for expiry in nifty_expiries:
        print(f"   {expiry.strftime('%d-%b-%Y')} ({expiry.strftime('%A')})")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure your access token is valid!")