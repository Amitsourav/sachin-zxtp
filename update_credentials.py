#!/usr/bin/env python3
"""
Update Zerodha Credentials in config.yaml
"""

import yaml
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════╗
║           UPDATE ZERODHA CREDENTIALS                         ║
╚══════════════════════════════════════════════════════════════╝

Enter your Zerodha API credentials:
""")

# Get credentials
api_key = input("1. API Key: ").strip()
api_secret = input("2. API Secret: ").strip()
access_token = input("3. Access Token: ").strip()

# Load config
config_path = Path("config/config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Update broker section
config['broker']['api_key'] = api_key
config['broker']['api_secret'] = api_secret
config['broker']['access_token'] = access_token
config['broker']['name'] = 'zerodha'

# Ask about trading mode
print("\nTrading Mode:")
print("1. LIVE (Real Money)")
print("2. PAPER (Testing)")
mode_choice = input("Choose (1 or 2): ").strip()

if mode_choice == '1':
    config['trading']['mode'] = 'live'
    print("⚠️  Set to LIVE trading - will use REAL MONEY!")
else:
    config['trading']['mode'] = 'paper'
    print("✅ Set to PAPER trading - safe testing mode")

# Save config
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("\n✅ Configuration updated successfully!")
print("\nNext step: Test connection with:")
print("  python3 test_zerodha_connection.py")