#!/usr/bin/env python3
"""
Force Exit Tool - Manually close positions
Use this to exit trades immediately regardless of P&L
"""

import sys
import yaml
from pathlib import Path
from kiteconnect import KiteConnect
from datetime import datetime

def force_exit_all_positions():
    """Force exit all open positions"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              FORCE EXIT - EMERGENCY CLOSE                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Load config
    config_path = Path("config/config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    broker_config = config.get('broker', {})
    
    # Initialize Zerodha
    kite = KiteConnect(api_key=broker_config['api_key'])
    kite.set_access_token(broker_config['access_token'])
    
    try:
        # Get all positions
        positions = kite.positions()
        open_positions = [p for p in positions['day'] if p['quantity'] != 0]
        
        if not open_positions:
            print("✅ No open positions to close")
            return
        
        print(f"\n⚠️  Found {len(open_positions)} open positions:")
        for pos in open_positions:
            print(f"   {pos['tradingsymbol']}: {pos['quantity']} @ ₹{pos['last_price']:.2f}")
            print(f"   P&L: ₹{pos['pnl']:.2f}")
        
        # Confirm
        response = input("\n🔴 Force exit ALL positions? (YES to confirm): ")
        
        if response == "YES":
            for pos in open_positions:
                try:
                    # Place exit order
                    order_id = kite.place_order(
                        variety=kite.VARIETY_REGULAR,
                        exchange=pos['exchange'],
                        tradingsymbol=pos['tradingsymbol'],
                        transaction_type='SELL' if pos['quantity'] > 0 else 'BUY',
                        quantity=abs(pos['quantity']),
                        product=pos['product'],
                        order_type='MARKET'
                    )
                    print(f"✅ Exit order placed for {pos['tradingsymbol']}: {order_id}")
                except Exception as e:
                    print(f"❌ Failed to exit {pos['tradingsymbol']}: {e}")
            
            print("\n✅ Force exit completed!")
        else:
            print("❌ Force exit cancelled")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    force_exit_all_positions()