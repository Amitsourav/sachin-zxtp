# 🎯 How Bot Selects Which Option to Buy at 9:15

## 📊 The Complete Decision Process

### Step 1: Pre-Market Scan (9:14:00 - 9:14:50)

```python
# At 9:14 AM, the bot scans NIFTY50 stocks
Top Gainers Found:
1. RELIANCE: +2.35%  ← Highest gainer
2. TCS: +1.80%
3. HDFC: +1.45%
4. INFY: +1.20%
5. ICICIBANK: +0.95%
```

### Step 2: Select the Stock (9:14:50)

**RULE: Pick the TOP GAINER from NIFTY50**

```python
selected_stock = "RELIANCE"  # Highest % gain
current_price = 2805.50       # Live price
```

### Step 3: Check PCR Filter (9:14:50)

**RULE: PCR must be between 0.7 - 1.5**

```python
pcr = 0.85  # Live PCR from option chain

if 0.7 <= pcr <= 1.5:
    signal = "BUY"  ✅
else:
    signal = "SKIP"  ❌
```

### Step 4: Calculate Strike Price (9:14:55)

**RULE: Buy At-The-Money (ATM) Call Option**

```python
spot_price = 2805.50

# Round to nearest 100 for stocks
atm_strike = round(2805.50 / 100) * 100 = 2800

# For NIFTY: Round to nearest 50
# For BANKNIFTY: Round to nearest 100
```

### Step 5: Select Expiry (9:14:55)

**RULE: Current Week Expiry (Nearest Thursday)**

```python
today = Monday, Jan 20
expiry = Thursday, Jan 23  # This week's expiry

option_symbol = "RELIANCE23JAN2800CE"
```

### Step 6: Final Option Selection (9:14:58)

```python
SELECTED OPTION:
================
Stock: RELIANCE
Strike: 2800
Type: CE (Call)
Expiry: 23-JAN (current week)
Symbol: RELIANCE23JAN2800CE
Current Premium: ₹45.50
Lot Size: 250
```

### Step 7: Execute at 9:15:00

```python
# At EXACTLY 9:15:00
ORDER:
------
Buy: 250 quantity (1 lot)
Symbol: RELIANCE23JAN2800CE
Type: MARKET order
Price: ₹45.50 per unit
Total: ₹11,375
```

---

## 📋 Complete Selection Rules

### 1. **Stock Selection**
```python
def select_stock():
    # Get NIFTY50 stocks sorted by % gain
    gainers = get_top_gainers()
    
    # Pick #1 gainer
    selected = gainers[0]
    
    # Must have positive change
    if selected['change_percent'] > 0:
        return selected['symbol']
    else:
        return None  # No trade today
```

### 2. **Strike Selection**
```python
def calculate_strike(spot_price, instrument):
    if instrument == "NIFTY":
        # Round to nearest 50
        return round(spot_price / 50) * 50
    
    elif instrument == "BANKNIFTY":
        # Round to nearest 100
        return round(spot_price / 100) * 100
    
    else:  # Individual stocks
        if spot_price < 500:
            # Round to nearest 20
            return round(spot_price / 20) * 20
        elif spot_price < 1000:
            # Round to nearest 50
            return round(spot_price / 50) * 50
        else:
            # Round to nearest 100
            return round(spot_price / 100) * 100
```

### 3. **Option Type**
```python
# ALWAYS CALL OPTIONS (CE)
option_type = "CE"

# Why calls?
# - Top gainer = Bullish momentum
# - 9:15 strategy = Momentum play
# - Calls benefit from upward movement
```

### 4. **Expiry Selection**
```python
def get_expiry():
    today = datetime.now()
    
    # Find next Thursday (weekly expiry)
    days_ahead = 3 - today.weekday()  # Thursday = 3
    if days_ahead <= 0:
        days_ahead += 7
    
    expiry = today + timedelta(days=days_ahead)
    return expiry.strftime("%d%b").upper()
```

---

## 🔍 Real Examples from Different Days

### Example 1: Bullish Day
```
Date: Monday Morning
Top Gainer: TATAMOTORS +3.2%
Spot Price: ₹750
PCR: 0.75 ✅

SELECTED: TATAMOTORS23JAN750CE
Entry: ₹18.50
Target: ₹19.98 (+8%)
Stop Loss: ₹12.95 (-30%)
```

### Example 2: Moderate Day
```
Date: Tuesday Morning
Top Gainer: INFY +1.5%
Spot Price: ₹1450
PCR: 1.2 ✅

SELECTED: INFY23JAN1450CE
Entry: ₹22.00
Target: ₹23.76 (+8%)
Stop Loss: ₹15.40 (-30%)
```

### Example 3: PCR Filter Blocks Trade
```
Date: Wednesday Morning
Top Gainer: HDFC +2.8%
Spot Price: ₹1650
PCR: 1.8 ❌ (Above 1.5)

SELECTED: NONE - Skip today
Reason: PCR too high (bearish sentiment)
```

---

## 📊 Why This Selection Works

### 1. **Top Gainer = Momentum**
- Stocks showing strength at open
- Likely to continue upward
- High volume and interest

### 2. **ATM Options = Best Risk/Reward**
- Maximum time value
- Good delta (0.5)
- Liquid and tradeable

### 3. **Weekly Expiry = Quick Profits**
- Low premium cost
- High gamma (fast movement)
- Exit same day (8% target)

### 4. **PCR Filter = Market Sentiment**
- 0.7-1.5 = Neutral to mild bearish
- Avoids extremely bullish/bearish days
- Better success rate

---

## 🎯 The Complete Decision at 9:15

```
9:14:00 - Start scanning
        ↓
9:14:30 - RELIANCE tops at +2.35%
        ↓
9:14:40 - PCR = 0.85 ✅
        ↓
9:14:50 - Strike = 2800 (ATM)
        ↓
9:14:55 - Symbol = RELIANCE23JAN2800CE
        ↓
9:15:00 - BUY 250 qty @ ₹45.50
        ↓
9:15:01 - Order executed!
```

---

## 💡 Special Cases

### If Top Gainer is NIFTY ETF:
```python
# Skip ETFs, go to next stock
if symbol in ['NIFTYBEES', 'BANKBEES']:
    select_next_stock()
```

### If Multiple Stocks Same %:
```python
# Pick by volume
if stock1_change == stock2_change:
    select_higher_volume_stock()
```

### If No Positive Gainers:
```python
# No trade day
if all_stocks_negative:
    skip_trading_today()
```

---

## ✅ Summary: What Gets Bought at 9:15

**The bot buys:**
1. **CALL option (CE)** of
2. **Top gaining NIFTY50 stock** with
3. **ATM strike price** and
4. **Current week expiry**
5. **Only if PCR is 0.7-1.5**

**Example for tomorrow:**
If RELIANCE is top gainer (+2.5%) at ₹2850:
- Bot will buy: **RELIANCE23JAN2850CE**
- Quantity: **250 (1 lot)**
- At exactly: **9:15:00 AM**

The selection is 100% rule-based and automatic - no manual intervention needed!