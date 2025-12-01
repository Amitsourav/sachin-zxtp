#!/usr/bin/env python3
"""
SIMPLE 9:15 TEST - Minimal script to test execution
"""

from kiteconnect import KiteConnect
import yaml
from datetime import datetime
import time

print(f"Starting at {datetime.now().strftime('%H:%M:%S')}")

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

kite = KiteConnect(api_key=config['broker']['api_key'])
kite.set_access_token(config['broker']['access_token'])

# Wait for 9:15 (with timeout)
now = datetime.now()
if now.time() < datetime.strptime("09:15", "%H:%M").time():
    target = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
    wait = (target - now).total_seconds()
    
    print(f"Waiting {wait:.0f} seconds for 9:15...")
    
    # Wait with timeout
    max_wait = min(wait, 300)  # Max 5 minutes wait for testing
    time.sleep(max_wait)

print(f"Executing at {datetime.now().strftime('%H:%M:%S')}")

# Simple test
try:
    print("Testing connection...")
    quotes = kite.quote(['NSE:RELIANCE'])
    print(f"Success! RELIANCE: ₹{quotes['NSE:RELIANCE']['last_price']}")
except Exception as e:
    print(f"Error: {e}")

print("Done!")