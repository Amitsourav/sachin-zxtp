# 📊 9:15 AM STOCK SELECTION FLOWCHART

## 🎯 Strategy Overview
The system selects ONE stock from NIFTY50 for options trading at exactly 9:15:00 AM

```
┌─────────────────────────────────────────────────────────────┐
│                    START (9:14:00 AM)                       │
│                  Pre-Market Scanning Begins                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              1️⃣  FETCH NIFTY50 STOCK DATA                   │
├─────────────────────────────────────────────────────────────┤
│  Priority Order:                                            │
│  1. NSE Real-time API (if available)                        │
│  2. Yahoo Finance (15-min delayed) - FALLBACK               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              2️⃣  CALCULATE % CHANGE FOR EACH STOCK          │
├─────────────────────────────────────────────────────────────┤
│  Formula: ((Current Price - Previous Close) / Previous Close) × 100│
│  Example: TATAMOTORS: (1050 - 1000) / 1000 × 100 = +5%     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              3️⃣  SORT BY PERCENTAGE GAIN                    │
├─────────────────────────────────────────────────────────────┤
│  Rank all NIFTY50 stocks by % change (highest first)        │
│  Example Ranking:                                           │
│  1. TATAMOTORS: +5.2%  ← TOP GAINER                        │
│  2. ICICIBANK:  +3.4%                                       │
│  3. RELIANCE:   +2.1%                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              4️⃣  SELECT TOP GAINER                          │
├─────────────────────────────────────────────────────────────┤
│  Pick Stock #1 from sorted list                             │
│  Selected: TATAMOTORS (Top Gainer)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              5️⃣  CHECK PUT-CALL RATIO (PCR)                 │
├─────────────────────────────────────────────────────────────┤
│  Fetch Option Chain Data for selected stock                 │
│  Calculate: PCR = Put Open Interest / Call Open Interest    │
│  Example: PCR = 8500 / 10000 = 0.85                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ PCR Between     │
                    │ 0.7 and 1.5?    │
                    └─────────────────┘
                       │           │
                      YES          NO
                       │           │
                       ▼           ▼
        ┌──────────────────┐  ┌──────────────────────┐
        │ ✅ STOCK APPROVED │  │ ❌ STOCK REJECTED    │
        │    FOR TRADE      │  │  Move to Next Gainer │
        └──────────────────┘  └──────────────────────┘
                       │                    │
                       │                    ▼
                       │         ┌──────────────────────┐
                       │         │ Try Stock #2, #3...  │
                       │         │ Repeat PCR Check     │
                       │         └──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              6️⃣  PREPARE OPTION DETAILS                     │
├─────────────────────────────────────────────────────────────┤
│  1. Find ATM Strike: Round(Spot Price / 50) × 50            │
│     Example: Round(1050/50) × 50 = 1050                     │
│  2. Select Weekly Expiry (Next Thursday)                    │
│  3. Choose CALL Option (for bullish trade)                  │
│  4. Format: SYMBOL + DDMMM + Strike + CE                    │
│     Example: TATAMOTORS16OCT1050CE                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              7️⃣  WAIT FOR 9:15:00 AM                        │
├─────────────────────────────────────────────────────────────┤
│  High-frequency polling (100Hz)                             │
│  NTP time sync for precision                                │
│  Target: < 1ms execution delay                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              8️⃣  EXECUTE TRADE AT 9:15:00                   │
├─────────────────────────────────────────────────────────────┤
│  Place BUY order for selected option                        │
│  Quantity: 1 lot (50 for NIFTY stocks)                      │
│  Order Type: Market Order                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              9️⃣  MONITOR POSITION                           │
├─────────────────────────────────────────────────────────────┤
│  Exit Conditions:                                           │
│  • Profit Target: +8% → EXIT WITH PROFIT                    │
│  • Stop Loss: -30% → EXIT WITH LOSS                         │
│  • End of Day: Close position before 3:15 PM               │
└─────────────────────────────────────────────────────────────┘
```

## 🔍 WHY ICICIBANK WAS SELECTED INSTEAD OF TATAMOTORS

```
┌─────────────────────────────────────────────────────────────┐
│                   DATA DELAY PROBLEM                        │
├─────────────────────────────────────────────────────────────┤
│  Real Market at 9:32 AM:                                    │
│  1. TATAMOTORS: +5.2% (ACTUAL TOP GAINER)                  │
│  2. ICICIBANK:  +3.4%                                       │
│                                                              │
│  What Yahoo Shows at 9:32 AM (15-min delayed):             │
│  Data from 9:17 AM:                                         │
│  1. ICICIBANK:  +0.34% (WAS TOP AT 9:17 AM)               │
│  2. TATAMOTORS: +0.20%                                      │
│                                                              │
│  Result: System picks ICICIBANK (outdated top gainer)       │
└─────────────────────────────────────────────────────────────┘
```

## 📋 SELECTION CRITERIA SUMMARY

| Step | Criteria | Value | Purpose |
|------|----------|-------|---------|
| 1 | Market | NIFTY50 Only | Liquid stocks with options |
| 2 | Direction | Top Gainers Only | Momentum strategy |
| 3 | Ranking | #1 Gainer First | Strongest momentum |
| 4 | PCR Range | 0.7 - 1.5 | Balanced sentiment filter |
| 5 | Option Type | ATM Call | Maximum gamma exposure |
| 6 | Timing | Exactly 9:15:00 | Market open momentum |
| 7 | Exit | +8% or -30% | Risk management |

## 🚨 KEY DECISION POINTS

1. **Stock Selection**: ALWAYS picks top gainer first
2. **PCR Filter**: If PCR outside range, moves to next gainer
3. **No Manual Selection**: Fully automated based on ranking
4. **Single Position**: Only ONE trade at a time
5. **Data Source Priority**: NSE > Yahoo (with delay warning)

## 💡 CURRENT ISSUE
- Yahoo Finance shows 15-minute old data during market hours
- At 9:32 AM, system sees 9:17 AM data
- ICICIBANK was top at 9:17, but TATAMOTORS became top later
- Solution: Need real-time data source or broker API