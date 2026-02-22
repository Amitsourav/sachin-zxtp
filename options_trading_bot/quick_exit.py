#!/usr/bin/env python3
"""
QUICK EXIT - Close specific or all open positions INSTANTLY
Speed is priority - market order, no delays, no confirmations after selection
"""

from kiteconnect import KiteConnect
import yaml
import sys
import os
from datetime import datetime

def quick_exit():
    # Load config - same as your other scripts
    config_path = 'config/config.yaml'
    if not os.path.exists(config_path):
        print("Config not found. Run from options_trading_bot/ directory.")
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    kite = KiteConnect(api_key=config['broker']['api_key'])
    kite.set_access_token(config['broker']['access_token'])

    # Fetch all open positions in one call
    try:
        positions = kite.positions()
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    open_positions = [p for p in positions['day'] if p['quantity'] != 0]

    if not open_positions:
        print("No open positions.")
        return

    # Display positions with live P&L
    print(f"\n{'='*80}")
    print(f"  OPEN POSITIONS - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*80}")
    print(f"{'#':<4} {'Symbol':<30} {'Qty':<8} {'Entry':<12} {'LTP':<12} {'P&L':<15} {'%':<8}")
    print(f"{'-'*80}")

    total_pnl = 0
    for i, pos in enumerate(open_positions, 1):
        qty = pos['quantity']
        avg_price = pos['average_price']
        ltp = pos['last_price']
        pnl = pos['pnl']
        total_pnl += pnl

        if avg_price > 0:
            pnl_pct = ((ltp - avg_price) / avg_price) * 100
        else:
            pnl_pct = 0

        icon = "+" if pnl >= 0 else ""
        print(f"{i:<4} {pos['tradingsymbol']:<30} {qty:<8} {avg_price:<12.2f} {ltp:<12.2f} {icon}{pnl:<14.2f} {icon}{pnl_pct:.2f}%")

    print(f"{'-'*80}")
    print(f"{'TOTAL P&L:':<66} {'+' if total_pnl >= 0 else ''}{total_pnl:.2f}")
    print(f"{'='*80}")

    # Get user choice
    if len(open_positions) == 1:
        print(f"\n1 position found. Enter 1 to close or 'all': ", end="")
    else:
        print(f"\nWhich to close? (1-{len(open_positions)} / all): ", end="")

    choice = input().strip().lower()

    # Determine which positions to close
    to_close = []
    if choice == 'all':
        to_close = open_positions
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(open_positions):
            to_close = [open_positions[idx]]
        else:
            print("Invalid number.")
            return
    else:
        print("Invalid input.")
        return

    # CLOSE NOW - MARKET ORDER - NO DELAY
    print(f"\nCLOSING {len(to_close)} position(s)...")

    for pos in to_close:
        symbol = pos['tradingsymbol']
        qty = abs(pos['quantity'])
        # If quantity > 0 we bought it, so SELL to close. If < 0, BUY to close.
        exit_type = 'SELL' if pos['quantity'] > 0 else 'BUY'

        try:
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=pos['exchange'],
                tradingsymbol=symbol,
                transaction_type=exit_type,
                quantity=qty,
                product=pos['product'],
                order_type=kite.ORDER_TYPE_MARKET
            )
            print(f"  {symbol} -> {exit_type} {qty} MARKET | Order: {order_id}")
        except Exception as e:
            print(f"  FAILED {symbol}: {e}")

    # Quick summary after orders placed
    print(f"\n{'='*80}")
    print(f"  EXIT SUMMARY - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*80}")

    closed_pnl = 0
    for pos in to_close:
        pnl = pos['pnl']
        closed_pnl += pnl
        icon = "+" if pnl >= 0 else ""
        print(f"  {pos['tradingsymbol']}: {icon}{pnl:.2f}")

    print(f"{'-'*80}")
    print(f"  Total Closed P&L: {'+' if closed_pnl >= 0 else ''}{closed_pnl:.2f}")
    print(f"{'='*80}")

if __name__ == "__main__":
    quick_exit()
