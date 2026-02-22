#!/usr/bin/env python3
"""
Quick script to update only the access token in config
"""

import yaml
from pathlib import Path
import sys

# Check if token provided as argument
if len(sys.argv) > 1:
    new_token = sys.argv[1]
else:
    print("Enter new Zerodha Access Token:")
    new_token = input("> ").strip()

if not new_token:
    print("❌ No token provided")
    sys.exit(1)

# Load config
config_path = Path("config/config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Update only the access token
old_token = config['broker']['access_token']
config['broker']['access_token'] = new_token

# Save config
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"✅ Access token updated!")
print(f"   Old: {old_token[:10]}...")
print(f"   New: {new_token[:10]}...")
print("\nTest connection with:")
print("  python3 test_zerodha_connection.py")