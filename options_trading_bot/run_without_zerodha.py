#!/usr/bin/env python3
"""
Run trading bot in paper mode without Zerodha connection
Perfect for testing when Zerodha login is not working
"""

import yaml
from pathlib import Path
import subprocess
import sys

print("""
╔══════════════════════════════════════════════════════════════╗
║           PAPER TRADING MODE (No Zerodha Required)            ║
╚══════════════════════════════════════════════════════════════╝

This will run the bot in simulation mode:
✅ No real money
✅ No Zerodha login needed  
✅ Safe for testing
✅ Uses simulated market data
""")

# Update config to paper mode
config_path = Path("config/config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Force paper trading mode
config['trading']['mode'] = 'paper'
config['trading']['use_live_data'] = False  # Use simulated data
config['notifications']['telegram_enabled'] = False  # Disable telegram

# Save config
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("Configuration updated for paper trading")
print("\nStarting bot in PAPER TRADING mode...")
print("-" * 60)

# Run the paper trading script
try:
    subprocess.run([sys.executable, "paper_trade_live.py"])
except KeyboardInterrupt:
    print("\n\nBot stopped by user")
except Exception as e:
    print(f"\nError: {e}")
    print("\nTrying alternative script...")
    subprocess.run([sys.executable, "main.py"])