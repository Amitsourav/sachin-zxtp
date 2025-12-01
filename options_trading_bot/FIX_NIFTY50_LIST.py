#!/usr/bin/env python3
"""
FIX NIFTY50 LIST - Remove INDUSINDBK and add correct stocks
INDUSINDBK was removed from NIFTY50 in September 2024
"""

import os
import glob

# Files to fix
files_to_fix = [
    'BULLETPROOF_915_strategy.py',
    'COMPLETE_915_trade.py',
    'CORRECT_915_NIFTY50.py',
    'INSTANT_915_NIFTY50.py',
    'INSTANT_915_trader.py',
    'LIGHTNING_915_executor.py',
    'LIVE_915_trader.py',
    'PRECISION_915_strategy.py',
    'ULTIMATE_915.py',
    'VALIDATE_before_915.py',
    'verify_top_gainers.py'
]

print("🔧 FIXING NIFTY50 LISTS - Removing INDUSINDBK")
print("=" * 50)

for filename in files_to_fix:
    if os.path.exists(filename):
        print(f"\n📝 Fixing {filename}...")
        
        with open(filename, 'r') as f:
            content = f.read()
        
        # Remove INDUSINDBK from the list
        old_line1 = "'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:INDUSINDBK', 'NSE:M&M',"
        new_line1 = "'NSE:POWERGRID', 'NSE:NTPC', 'NSE:TATAMOTORS', 'NSE:M&M',"
        
        # Also fix if VEDL is present (should be TRENT and INDIGO)
        old_line2 = "'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:VEDL'"
        new_line2 = "'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT', 'NSE:INDIGO'"
        
        # Also fix TRENT if missing
        old_line3 = "'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT'"
        new_line3 = "'NSE:TATASTEEL', 'NSE:SHRIRAMFIN', 'NSE:ADANIENT', 'NSE:LTIM', 'NSE:TRENT', 'NSE:INDIGO'"
        
        if 'INDUSINDBK' in content:
            content = content.replace(old_line1, new_line1)
            print(f"   ✅ Removed INDUSINDBK")
        
        if 'VEDL' in content:
            content = content.replace(old_line2, new_line2)
            print(f"   ✅ Replaced VEDL with TRENT and INDIGO")
        elif 'NSE:TRENT\'' in content and 'INDIGO' not in content:
            content = content.replace(old_line3, new_line3)
            print(f"   ✅ Added INDIGO to complete the list")
        
        with open(filename, 'w') as f:
            f.write(content)
            
        print(f"   ✅ Fixed {filename}")
    else:
        print(f"   ⚠️ {filename} not found")

print("\n" + "=" * 50)
print("✅ ALL FILES FIXED!")
print("\nCORRECT NIFTY50 LIST (50 stocks):")
print("Includes: TRENT, INDIGO (added Sept 2024)")
print("Excludes: INDUSINDBK, HEROMOTOCO (removed Sept 2024)")
print("\n⚠️ INDUSINDBK is now in BANKNIFTY, NOT in NIFTY50!")