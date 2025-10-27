#!/usr/bin/env python3
"""
Check HINDALCO expiry dates
"""

from kiteconnect import KiteConnect
import yaml
from pathlib import Path
from datetime import datetime

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
║           CHECKING HINDALCO EXPIRY DATES                      ║
╚══════════════════════════════════════════════════════════════╝
""")

try:
    # Get all NFO instruments
    print("Fetching NFO instruments from Zerodha...")
    instruments = kite.instruments("NFO")
    
    # Filter for HINDALCO options
    hindalco_options = [i for i in instruments if i['name'] == 'HINDALCO']
    
    # Get unique expiry dates
    expiry_dates = sorted(set(opt['expiry'] for opt in hindalco_options))
    
    print(f"\n📅 HINDALCO Option Expiry Dates Available:")
    print("-" * 40)
    
    today = datetime.now().date()
    print(f"Today: {today.strftime('%d %B %Y')}")
    print("\nUpcoming Expiries:")
    
    for i, expiry in enumerate(expiry_dates[:10], 1):  # Show next 10 expiries
        if expiry >= today:
            day_of_week = expiry.strftime('%A')
            days_from_today = (expiry - today).days
            print(f"{i}. {expiry.strftime('%d %B %Y')} ({day_of_week}) - {days_from_today} days away")
    
    # Find nearest expiry
    nearest_expiry = None
    for expiry in expiry_dates:
        if expiry >= today:
            nearest_expiry = expiry
            break
    
    print(f"\n✅ NEAREST Expiry: {nearest_expiry.strftime('%d %B %Y')}")
    print(f"   Format should be: HINDALCO{nearest_expiry.strftime('%y%b').upper()}{nearest_expiry.day}27800CE")
    
except Exception as e:
    print(f"Error: {e}")