#!/usr/bin/env python3
"""
Test timing precision for 9:15:00 execution
"""
import time
from datetime import datetime, timedelta

def test_precision_timing():
    """Test how accurately we can hit 9:15:00"""
    
    print("🕘 TIMING PRECISION TEST")
    print("=" * 50)
    
    # Set a target time 10 seconds from now for testing
    now = datetime.now()
    target = now + timedelta(seconds=10)
    
    print(f"Current time: {now.strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Target time:  {target.strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Waiting {10} seconds...")
    
    # Calculate precise wait time
    wait_seconds = (target - now).total_seconds()
    
    # Wait until target time
    time.sleep(wait_seconds)
    
    # Check actual execution time
    actual = datetime.now()
    difference_ms = (actual - target).total_seconds() * 1000
    
    print(f"\nRESULTS:")
    print(f"Target time:  {target.strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Actual time:  {actual.strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Difference:   {difference_ms:+.1f} milliseconds")
    
    if abs(difference_ms) < 100:
        print("✅ EXCELLENT: Within 100ms")
    elif abs(difference_ms) < 500:
        print("✅ GOOD: Within 500ms")
    elif abs(difference_ms) < 1000:
        print("⚠️  ACCEPTABLE: Within 1 second")
    else:
        print("❌ POOR: More than 1 second off")

def simulate_915_execution():
    """Simulate waiting for 9:15:00"""
    
    print("\n🚀 SIMULATING 9:15:00 EXECUTION")
    print("=" * 50)
    
    # For demo, use current time + 5 seconds as "9:15:00"
    now = datetime.now()
    mock_915 = now + timedelta(seconds=5)
    
    print(f"Mock 9:15:00: {mock_915.strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Current time: {now.strftime('%H:%M:%S.%f')[:-3]}")
    print("Waiting for market open...")
    
    # Precise timing calculation
    wait_seconds = (mock_915 - now).total_seconds()
    time.sleep(wait_seconds)
    
    execution_time = datetime.now()
    print(f"⚡ EXECUTED AT: {execution_time.strftime('%H:%M:%S.%f')[:-3]}")
    
    # Calculate precision
    delay_ms = (execution_time - mock_915).total_seconds() * 1000
    print(f"Execution delay: {delay_ms:+.1f} milliseconds")
    
    return delay_ms

if __name__ == "__main__":
    print("Testing timing precision for 9:15 strategy...\n")
    
    # Test 1: Basic precision
    test_precision_timing()
    
    # Test 2: Simulate 9:15 execution
    delay = simulate_915_execution()
    
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    print(f"Execution delay: {delay:+.1f}ms")
    
    if abs(delay) < 50:
        print("🎯 PERFECT: Sub-50ms precision")
        print("   Ready for live trading")
    elif abs(delay) < 200:
        print("✅ EXCELLENT: Sub-200ms precision") 
        print("   Suitable for 9:15 strategy")
    elif abs(delay) < 500:
        print("✅ GOOD: Sub-500ms precision")
        print("   Should work for most cases")
    else:
        print("⚠️  NEEDS IMPROVEMENT")
        print("   Consider system optimization")