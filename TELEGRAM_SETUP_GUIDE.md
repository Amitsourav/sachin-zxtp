# 📱 Telegram Bot Setup Guide - Step by Step

## 🎯 Quick Setup (5 minutes)

### Step 1: Create Your Bot (2 minutes)

1. **Open Telegram** on your phone or desktop
2. **Search for** `@BotFather` (official bot creator)
3. **Start a chat** and type `/newbot`
4. **Follow prompts:**
   ```
   BotFather: Choose a name for your bot
   You: My Trading Bot
   
   BotFather: Choose a username (must end in 'bot')
   You: my_trading_915_bot
   
   BotFather: Done! Your token is:
   5123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
5. **SAVE THIS TOKEN!** You'll need it soon.

### Step 2: Get Your Chat ID (1 minute)

1. **Search for** `@userinfobot` in Telegram
2. **Start a chat** - it will immediately show:
   ```
   Your user ID: 987654321
   ```
3. **SAVE THIS ID!** This is your chat ID.

### Step 3: Configure the Bot (2 minutes)

1. **Open** `config/config.yaml` in your project
2. **Add your credentials:**
   ```yaml
   notifications:
     telegram_enabled: true
     telegram_token: "5123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Your token
     telegram_chat_id: "987654321"  # Your chat ID
   ```
3. **Save the file**

### Step 4: Test Your Bot

1. **Run this test script:**
   ```bash
   python3 test_telegram.py
   ```
2. **Check your Telegram** - You should receive:
   ```
   🤖 Trading Bot Active!
   This is a test message.
   ```

## ✅ That's It! Your Telegram is Ready!

---

## 📝 What You'll Receive

### Trade Alerts
```
🔔 Trade Alert
━━━━━━━━━━
RELIANCE 2800 CE
Entry: ₹45.50
Target: ₹49.14
Quantity: 250
```

### Profit Notifications
```
🎯 Target Reached!
━━━━━━━━━━
Profit: ₹925 (+8.1%)
Duration: 45 minutes
```

### Daily Summary
```
📊 Daily Summary
━━━━━━━━━━
Trades: 2
P&L: +₹3,450
Win Rate: 100%
```

---

## 🔐 Security Notes

- **Never share your token** - It's like a password
- **Only your chat ID can control the bot** - Others are blocked
- **Token in config file** - Not in code
- **Bot is private** - Only responds to you

---

## 🛠️ Troubleshooting

### Bot doesn't respond?
- Check token is correct (no extra spaces)
- Ensure you started chat with your bot
- Verify chat ID is correct

### "Unauthorized" error?
- Chat ID doesn't match
- Use @userinfobot to get correct ID

### Connection error?
- Check internet connection
- Telegram might be blocked (use VPN)

---

## 📱 Bot Commands

Once set up, you can use these commands:

```
/start - Initialize bot
/status - Check current status
/positions - View open positions
/pnl - Today's profit/loss
/stop - Stop trading
/help - Get help
```

---

## 🎉 Setup Complete!

Your Telegram bot is now ready to:
- ✅ Send instant trade alerts
- ✅ Notify you of profits/losses
- ✅ Accept remote commands
- ✅ Keep you updated anywhere

**Next Step:** Run `python3 main.py` to start trading with Telegram notifications!