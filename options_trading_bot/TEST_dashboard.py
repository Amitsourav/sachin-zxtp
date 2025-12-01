#!/usr/bin/env python3
"""
Quick test to show the trading dashboard without endless monitoring
"""

from CORRECT_915_NIFTY50 import Correct915Strategy

def test_dashboard():
    print("🧪 TESTING TRADING DASHBOARD")
    print("=" * 50)
    
    # Initialize strategy
    strategy = Correct915Strategy(live_trading=False)
    
    # Execute the strategy
    success = strategy.execute_at_915()
    
    if success:
        print("\n✅ Dashboard test complete!")
    else:
        print("\n❌ Dashboard test failed")

if __name__ == "__main__":
    test_dashboard()