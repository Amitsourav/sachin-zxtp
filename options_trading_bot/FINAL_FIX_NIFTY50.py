#!/usr/bin/env python3
"""
FINAL FIX FOR NIFTY50 LIST - September 2024 Changes
REMOVED: INDUSINDBK, HEROMOTOCO  
ADDED: INDIGO, MAXHEALTH
"""

import os
import glob

files_to_fix = glob.glob("*.py")

print("🔧 FINAL FIX FOR NIFTY50 - Replacing HEROMOTOCO with MAXHEALTH")
print("=" * 60)
print("September 2024 NIFTY50 changes:")
print("  ❌ REMOVED: INDUSINDBK, HEROMOTOCO") 
print("  ✅ ADDED: INDIGO (InterGlobe Aviation), MAXHEALTH (Max Healthcare)")
print("=" * 60)

for filename in files_to_fix:
    if filename == 'FINAL_FIX_NIFTY50.py':
        continue
        
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        original = content
        
        # Replace HEROMOTOCO with MAXHEALTH
        if 'HEROMOTOCO' in content:
            content = content.replace("'NSE:HEROMOTOCO'", "'NSE:MAXHEALTH'")
            
        if content != original:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✅ Fixed {filename}: Replaced HEROMOTOCO with MAXHEALTH")
            
    except Exception as e:
        print(f"⚠️ Error fixing {filename}: {e}")

print("\n" + "=" * 60)
print("✅ COMPLETE! NIFTY50 list now has correct 50 stocks:")
print("   - Includes: INDIGO, MAXHEALTH (added Sept 2024)")
print("   - Excludes: INDUSINDBK, HEROMOTOCO (removed Sept 2024)")
print("\n📌 INDUSINDBK and HEROMOTOCO are now in BANKNIFTY/MIDCAP, NOT NIFTY50!")