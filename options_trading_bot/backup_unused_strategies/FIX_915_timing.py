#!/usr/bin/env python3
"""
FIX for 9:15 timing issue - Debug and fix timing problems
"""

from datetime import datetime, timedelta
import time
import pytz

def check_timing_issue():
    """Diagnose timing problems"""
    print("=" * 60)
    print("🔍 DIAGNOSING 9:15 TIMING ISSUE")
    print("=" * 60)
    
    # Check current time
    now = datetime.now()
    print(f"\n1. System Time:")
    print(f"   Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Day: {now.strftime('%A')}")
    
    # Check if market day
    if now.weekday() in [5, 6]:  # Saturday = 5, Sunday = 6
        print(f"   ⚠️  WARNING: Today is {now.strftime('%A')} - Market is closed!")
    
    # Check timezone
    print(f"\n2. Timezone Check:")
    try:
        ist = pytz.timezone('Asia/Kolkata')
        ist_time = datetime.now(ist)
        print(f"   IST time: {ist_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    except:
        print(f"   IST time: Cannot determine (pytz not installed)")
    
    # Check 9:15 target
    print(f"\n3. Target Time Calculation:")
    target_time = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
    print(f"   Target 9:15: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calculate wait time
    wait_seconds = (target_time - now).total_seconds()
    
    if wait_seconds > 0:
        print(f"   Wait time: {wait_seconds:.0f} seconds ({wait_seconds/60:.1f} minutes)")
        print(f"\n4. Testing Wait Logic:")
        print(f"   Would wait until: {target_time}")
        
        if wait_seconds > 3600:  # More than 1 hour
            print(f"   ✅ Normal - Market hasn't opened yet")
        else:
            print(f"   ⏰ Market opening soon")
    else:
        print(f"   ⚠️  9:15 has already passed today")
        print(f"   Time since 9:15: {abs(wait_seconds/60):.1f} minutes ago")
    
    # Test the actual wait logic
    print(f"\n5. Testing Execution Logic:")
    print("   Simulating what would happen at 9:15...")
    
    # Simulate the wait
    if now.time() < datetime.strptime("09:15", "%H:%M").time():
        print(f"   Script would wait {wait_seconds:.0f} seconds")
        print(f"   Then execute at 9:15:00")
    else:
        print(f"   Script would execute immediately (past 9:15)")
    
    return True

def test_immediate_execution():
    """Test if the script can execute properly"""
    print(f"\n" + "=" * 60)
    print("🧪 TESTING IMMEDIATE EXECUTION")
    print("=" * 60)
    
    try:
        # Test imports
        print("\n1. Testing imports...")
        from kiteconnect import KiteConnect
        import yaml
        import pandas as pd
        print("   ✅ All imports successful")
        
        # Test config
        print("\n2. Testing config file...")
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print(f"   ✅ Config loaded")
        print(f"   API Key: {config['broker']['api_key'][:10]}...")
        
        # Test connection
        print("\n3. Testing Zerodha connection...")
        kite = KiteConnect(api_key=config['broker']['api_key'])
        kite.set_access_token(config['broker']['access_token'])
        
        # Try a simple API call
        try:
            profile = kite.profile()
            print(f"   ✅ Connected to Zerodha")
            print(f"   User: {profile.get('user_name', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Connection failed: {str(e)[:50]}...")
            print(f"   Access token might be expired")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def create_fixed_script():
    """Create a fixed version of ULTIMATE_915.py"""
    print(f"\n" + "=" * 60)
    print("🔧 CREATING FIXED TIMING SCRIPT")
    print("=" * 60)
    
    fixed_code = '''#!/usr/bin/env python3
"""
FIXED ULTIMATE 9:15 - With better timing and error handling
"""

from kiteconnect import KiteConnect
import yaml
import pandas as pd
from datetime import datetime, timedelta
import time
import sys

print("🚀 ULTIMATE 9:15 STRATEGY - FIXED VERSION")
print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")

# Load config
try:
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print("✅ Config loaded")
except Exception as e:
    print(f"❌ Config error: {e}")
    sys.exit(1)

# Initialize connection
try:
    kite = KiteConnect(api_key=config['broker']['api_key'])
    kite.set_access_token(config['broker']['access_token'])
    print("✅ Zerodha connected")
except Exception as e:
    print(f"❌ Connection error: {e}")
    sys.exit(1)

# Wait for 9:15
now = datetime.now()
current_time = now.time()

if current_time < datetime.strptime("09:15", "%H:%M").time():
    target = datetime.combine(now.date(), datetime.strptime("09:15:00", "%H:%M:%S").time())
    wait = (target - now).total_seconds()
    
    print(f"⏰ Waiting {wait:.0f} seconds until 9:15:00...")
    
    # Wait with progress updates
    while datetime.now() < target:
        remaining = (target - datetime.now()).total_seconds()
        if remaining > 60:
            print(f"   {remaining/60:.1f} minutes remaining...", end='\\r')
            time.sleep(10)
        elif remaining > 10:
            print(f"   {remaining:.0f} seconds remaining...", end='\\r')
            time.sleep(1)
        else:
            print(f"   {remaining:.1f} seconds - GET READY!", end='\\r')
            time.sleep(0.1)
    
    print(f"\\n🔔 9:15:00 REACHED! Executing now...")

# Execute strategy
print(f"⚡ Scanning at {datetime.now().strftime('%H:%M:%S')}")

try:
    # Quick test scan
    quotes = kite.quote(['NSE:RELIANCE', 'NSE:TCS'])
    
    for symbol, data in quotes.items():
        ltp = data['last_price']
        change = ((ltp - data['ohlc']['close']) / data['ohlc']['close']) * 100
        print(f"   {symbol}: ₹{ltp:.2f} ({change:+.2f}%)")
    
    print("✅ Strategy would execute here")
    
except Exception as e:
    print(f"❌ Execution error: {e}")
'''
    
    # Save the fixed script
    with open('ULTIMATE_915_FIXED.py', 'w') as f:
        f.write(fixed_code)
    
    print("✅ Created ULTIMATE_915_FIXED.py")
    print("\nRun this fixed version:")
    print("   python3 ULTIMATE_915_FIXED.py")
    
    return True

def main():
    print("\n🔧 FIXING 9:15 TIMING ISSUE\n")
    
    # Step 1: Diagnose
    check_timing_issue()
    
    # Step 2: Test execution
    test_immediate_execution()
    
    # Step 3: Create fixed script
    create_fixed_script()
    
    print(f"\n" + "=" * 60)
    print("📋 RECOMMENDATIONS:")
    print("=" * 60)
    print("\n1. Make sure your system time is correct")
    print("2. Run on weekdays only (Mon-Fri)")
    print("3. Get fresh access token daily")
    print("4. Use the fixed script: python3 ULTIMATE_915_FIXED.py")
    print("\nFor immediate testing, run:")
    print("   python3 check_shriram.py")

if __name__ == "__main__":
    main()