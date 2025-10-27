"""
COMPLETE NIFTY50 STOCKS LIST - CRITICAL FOR TRADING
DO NOT MODIFY WITHOUT VERIFICATION
Last Updated: October 2024
"""

# COMPLETE NIFTY50 LIST - ALL 50 STOCKS
NIFTY50_STOCKS = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJAJFINSV.NS", "BAJFINANCE.NS", "BHARTIARTL.NS", "BPCL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS",
    "INFY.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
    "LTIM.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS",
    "TECHM.NS", "TITAN.NS", "UPL.NS", "ULTRACEMCO.NS", "WIPRO.NS"
]

# Verify we have exactly 50 stocks
assert len(NIFTY50_STOCKS) == 50, f"ERROR: NIFTY50 list has {len(NIFTY50_STOCKS)} stocks, should be 50!"

# For NSE API (without .NS suffix)
NIFTY50_NSE_SYMBOLS = [s.replace('.NS', '') for s in NIFTY50_STOCKS]

def validate_nifty50_data(stocks_data):
    """
    CRITICAL VALIDATION: Ensure we're checking ALL stocks
    """
    if len(stocks_data) < 45:  # Allow for some stocks with missing data
        raise ValueError(f"CRITICAL: Only {len(stocks_data)} stocks found! Need at least 45 of 50.")
    
    return True

def get_missing_stocks(fetched_symbols):
    """
    Check which stocks are missing from fetched data
    """
    all_symbols = set(s.replace('.NS', '') for s in NIFTY50_STOCKS)
    fetched = set(fetched_symbols)
    missing = all_symbols - fetched
    
    if missing:
        print(f"⚠️ WARNING: Missing {len(missing)} stocks: {missing}")
    
    return list(missing)