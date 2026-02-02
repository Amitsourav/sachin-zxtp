#!/usr/bin/env python3
"""
QUICK EXIT - Instantly close all live positions
Usage: python3 exit_now.py

- No confirmation required
- Uses LIMIT order (avoids market order protection error)
- Exits immediately
"""

import yaml
from kiteconnect import KiteConnect
from pathlib import Path

def exit_now():
    print("🔴 QUICK EXIT - Closing all positions...")

    # Load config
    config_path = Path("config/config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    kite = KiteConnect(api_key=config['broker']['api_key'])
    kite.set_access_token(config['broker']['access_token'])

    # Get all positions
    try:
        positions = kite.positions()
    except Exception as e:
        print(f"❌ Failed to get positions: {e}")
        return

    open_positions = [p for p in positions['day'] if p['quantity'] != 0]

    if not open_positions:
        print("✅ No open positions")
        return

    for pos in open_positions:
        symbol = pos['tradingsymbol']
        qty = pos['quantity']
        exchange = pos['exchange']

        try:
            # Get current quote for LIMIT price
            quote_symbol = f"{exchange}:{symbol}"
            quote = kite.quote([quote_symbol])

            if quote_symbol in quote:
                ltp = quote[quote_symbol]['last_price']
                depth = quote[quote_symbol].get('depth', {})

                if qty > 0:  # Long - SELL
                    bid = depth.get('buy', [{}])[0].get('price', ltp) if depth.get('buy') else ltp
                    exit_price = round(max(bid * 0.97, 0.05), 2)  # 3% below bid
                    txn_type = 'SELL'
                else:  # Short - BUY
                    ask = depth.get('sell', [{}])[0].get('price', ltp) if depth.get('sell') else ltp
                    exit_price = round(ask * 1.03, 2)  # 3% above ask
                    txn_type = 'BUY'
            else:
                exit_price = round(pos['last_price'] * 0.95, 2)
                txn_type = 'SELL' if qty > 0 else 'BUY'

            # Place LIMIT order
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=exchange,
                tradingsymbol=symbol,
                transaction_type=txn_type,
                quantity=abs(qty),
                product=pos['product'],
                order_type=kite.ORDER_TYPE_LIMIT,
                price=exit_price
            )

            print(f"✅ {symbol} | {txn_type} @ ₹{exit_price} | Order: {order_id}")

        except Exception as e:
            print(f"❌ {symbol} failed: {e}")

    print("\n✅ Exit orders placed")

if __name__ == "__main__":
    exit_now()
