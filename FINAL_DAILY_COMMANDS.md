# 🎯 FINAL DAILY COMMANDS - NEVER CHANGE THESE!

## 📅 **EVERY TRADING DAY - ONLY 3 COMMANDS**

### **1️⃣ GET ACCESS TOKEN (8:30 AM)**
```bash
python3 get_access_token.py
```
**What it does:** Gets fresh token for the day

---

### **2️⃣ PRE-MARKET ANALYSIS (9:10 AM - Optional)**
```bash
python3 check_shriram.py
```
**What it does:** Shows current top gainers to preview

---

### **3️⃣ MAIN 9:15 TRADING (9:14 AM)**
```bash
cd options_trading_bot
python3 CORRECT_915_NIFTY50.py
```
**What it does:** 
- Waits for 9:15:00
- Scans ALL 50 NIFTY50 stocks
- Finds REAL #1 gainer in entire NIFTY50
- Executes trade signal
- Shows results

---

### **4️⃣ AFTER TRADE MONITORING (After 9:15)**
```bash
cd web_interface
python3 app.py
```
**What it does:** Opens dashboard at http://localhost:8080

---

## 🎯 **THAT'S IT! ONLY THESE 4 COMMANDS**

### **NEVER USE:**
- ❌ ULTIMATE_915.py (hangs)
- ❌ WORKING_915.py (only scans 10 stocks)
- ❌ BULLETPROOF_915_strategy.py (too complex)
- ❌ INSTANT_915_trader.py (too fast)
- ❌ Any other scripts I mentioned

### **ALWAYS USE:**
- ✅ get_access_token.py (for token)
- ✅ check_shriram.py (for preview)  
- ✅ cd options_trading_bot && python3 CORRECT_915_NIFTY50.py (for trading - scans ALL 50 NIFTY50 stocks)
- ✅ web_interface/app.py (for monitoring)

## 📋 **COPY-PASTE DAILY ROUTINE**

```bash
# Morning (8:30 AM)
python3 get_access_token.py

# Pre-market check (9:10 AM - optional)
python3 check_shriram.py

# Main trading (9:14 AM)
cd options_trading_bot
python3 CORRECT_915_NIFTY50.py

# After trade monitoring
cd web_interface
python3 app.py
```

## 🚨 **IMPORTANT RULES**

1. **NEVER** run any command other than these 4
2. **ALWAYS** get fresh token daily (command 1)
3. **ALWAYS** use cd options_trading_bot && python3 CORRECT_915_NIFTY50.py (never WORKING_915.py or ULTIMATE_915.py)
4. **NEVER** change these commands

These are your **FINAL, PERMANENT** commands. No more changes!