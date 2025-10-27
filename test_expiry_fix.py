#!/usr/bin/env python3
"""
Test expiry selection fix
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

print("Testing expiry selection for HINDALCO...")

try:
    # Get all NFO instruments
    instruments = kite.instruments("NFO")
    
    # Filter for HINDALCO options
    symbol = 'HINDALCO'
    symbol_options = [i for i in instruments if i['name'] == symbol]
    
    # Get unique expiry dates
    expiry_dates = sorted(set(opt['expiry'] for opt in symbol_options))
    
    # Current logic
    today = datetime.now().date()
    current_hour = datetime.now().hour
    
    # If market is open (after 9:15 AM), include today's expiry
    if current_hour >= 9:
        min_date = today
    else:
        min_date = today
    
    print(f"\nToday: {today}")
    print(f"Looking for expiries from {min_date} onwards...")
    
    # Get all valid expiries and show first few
    valid_expiries = [exp for exp in expiry_dates if exp >= min_date]
    
    if valid_expiries:
        print(f"Available expiries: {', '.join([exp.strftime('%d-%b-%Y') for exp in valid_expiries[:5]])}")
        nearest_expiry = valid_expiries[0]  # Pick the FIRST/NEAREST one
        print(f"\n✅ Selected NEAREST expiry: {nearest_expiry.strftime('%d-%b-%Y')}")
        
        # Format option symbol
        strike = 800
        year_short = nearest_expiry.strftime('%y')  
        month = nearest_expiry.strftime('%b').upper()
        day = nearest_expiry.day
        
        option_symbol = f"{symbol}{year_short}{month}{day}{int(strike)}CE"
        print(f"Option Symbol: {option_symbol}")
        
        if '27' in option_symbol and 'NOV' in option_symbol:
            print("\n❌ ERROR: Still selecting November 27!")
        elif '28' in option_symbol and 'OCT' in option_symbol:
            print("\n✅ SUCCESS: Correctly selecting October 28!")
        
except Exception as e:
    print(f"Error: {e}")