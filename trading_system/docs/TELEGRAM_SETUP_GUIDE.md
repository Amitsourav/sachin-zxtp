# 📱 Telegram Bot Setup Guide - 9:15 Strategy Trading System

Get real-time notifications about your trading activity through Telegram.

## 🤖 Why Telegram Notifications?

- **Instant Alerts**: Get immediate notifications about trades
- **Rich Formatting**: See formatted messages with emojis and structure
- **Mobile Access**: Receive alerts on your phone anywhere
- **Free Service**: No additional costs for messaging
- **Reliable Delivery**: High uptime and delivery rates

## 📋 Prerequisites

- Telegram account (mobile app or web)
- Basic understanding of bot interactions
- 5-10 minutes setup time

---

## 🚀 Step-by-Step Setup

### Step 1: Install Telegram
1. **Download Telegram**
   - **Mobile**: Download from App Store/Google Play
   - **Desktop**: Download from https://telegram.org/
   - **Web**: Use https://web.telegram.org/

2. **Create Account**
   - Sign up with your phone number
   - Verify with SMS code
   - Set up your profile

### Step 2: Create Your Trading Bot

1. **Find BotFather**
   - Search for `@BotFather` in Telegram
   - Start a conversation with BotFather
   - BotFather is the official bot for creating other bots

2. **Create New Bot**
   ```
   Send: /newbot
   
   BotFather will ask for:
   1. Bot Name: "9:15 Strategy Trading Bot" (or any name you prefer)
   2. Bot Username: "your_name_915_trading_bot" (must end with 'bot')
   ```

3. **Get Bot Token**
   - BotFather will provide a token like: `123456789:ABCdefGHIjklmnoPQRSTUVWXYZ`
   - **SAVE THIS TOKEN** - you'll need it for configuration
   - Keep this token **SECRET** - don't share it

### Step 3: Get Your Chat ID

**Method 1: Using @userinfobot (Recommended)**
1. Search for `@userinfobot` in Telegram
2. Send `/start` to the bot
3. The bot will reply with your User ID
4. **Save this number** - this is your Chat ID

**Method 2: Manual Method**
1. Send a message to your bot (from Step 2)
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id":YOUR_CHAT_ID}`
4. Copy the Chat ID number

**Method 3: Using Command Line**
```bash
# Replace YOUR_BOT_TOKEN with your actual token
curl https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
```

### Step 4: Test Your Bot

1. **Start conversation with your bot**
   - Go to your bot's username
   - Send `/start` to activate it

2. **Send test message** (optional)
   ```bash
   # Replace with your actual token and chat ID
   curl -X POST \
        -H 'Content-Type: application/json' \
        -d '{"chat_id": "YOUR_CHAT_ID", "text": "Hello from 9:15 Strategy Bot!"}' \
        https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage
   ```

---

## ⚙️ Configuration

### Add to .env File
```bash
# Add these lines to your .env file
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRSTUVWXYZ
TELEGRAM_CHAT_ID=987654321
```

### Update config.yaml
```yaml
notifications:
  telegram:
    enabled: true
    bot_token: ""  # Will be loaded from .env
    chat_id: ""    # Will be loaded from .env
```

### Test Configuration
```bash
# Run the system test to verify Telegram setup
python src/main.py test
```

---

## 📨 Message Types You'll Receive

### System Status Messages
```
🤖 9:15 Strategy system initialized and ready for trading!
```

### Market Scan Results
```
🔍 Starting pre-market scan for NIFTY50 gainers...

📈 Trade Signal Found!
Stock: RELIANCE
Strike: 3000
PCR: 1.25
Gain: 2.45%
```

### Trade Execution
```
✅ Trade Executed!
Symbol: RELIANCE24JAN3000CE
Entry Price: ₹85.50
Target: ₹92.34 (+8%)
Order ID: PAPER_1001
```

### Trade Exit
```
🎯 Position Closed!
Reason: Target reached
Exit Price: ₹92.50
PnL: ₹7.00 (8.19%)
Duration: 0:15:30
```

### Error Alerts
```
🚨 URGENT 🚨
❌ Error Alert - Trading Error
Failed to place order: Insufficient margin
```

### Daily Summary
```
📊 Daily Trading Summary
=========================

✅ Trade Executed: RELIANCE24JAN3000CE
📈 Entry Price: ₹85.50
📊 Exit Price: ₹92.50
💰 PnL: ₹7.00 (8.19%)
⏱️ Duration: 15 minutes

📊 Market Info:
VIX: 15.25
Top Gainer: RELIANCE (+2.45%)
```

---

## 🔧 Advanced Features

### Custom Bot Commands

You can add custom commands to your bot:

1. **Talk to BotFather again**
2. **Send**: `/setcommands`
3. **Select your bot**
4. **Add commands**:
   ```
   status - Get system status
   help - Get help information
   settings - Show current settings
   ```

### Bot Customization

**Set Bot Description:**
```
/setdescription
Your Bot Name
9:15 Strategy Trading Bot - Automated options trading notifications
```

**Set Bot Profile Photo:**
```
/setuserpic
Your Bot Name
[Upload an image]
```

**Set About Text:**
```
/setabouttext
Your Bot Name
Automated trading bot for 9:15 strategy notifications
```

---

## 🔐 Security Best Practices

### Bot Token Security
```bash
# ✅ Good - Use environment variables
TELEGRAM_BOT_TOKEN=your_token_here

# ❌ Bad - Never hardcode in source code
bot_token = "123456789:ABCdefGHIjklmnoPQRSTUVWXYZ"
```

### Chat ID Protection
- Don't share your Chat ID publicly
- Only your bot should know your Chat ID
- Regularly check bot permissions

### Bot Permissions
- Set bot to private (default)
- Don't add bot to public groups
- Review bot settings periodically

---

## 🧪 Testing Your Setup

### Test Script
```python
#!/usr/bin/env python3
"""
Test Telegram Bot Setup
"""
import os
import requests

def test_telegram_bot():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Missing Telegram credentials in .env file")
        return False
    
    # Test bot info
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    response = requests.get(url)
    
    if response.status_code == 200:
        bot_info = response.json()
        print(f"✅ Bot connected: {bot_info['result']['first_name']}")
    else:
        print("❌ Bot token invalid")
        return False
    
    # Test message sending
    message = "🧪 Test message from 9:15 Strategy Trading System"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ Test message sent successfully")
        return True
    else:
        print(f"❌ Failed to send message: {response.text}")
        return False

if __name__ == "__main__":
    test_telegram_bot()
```

### Run Test
```bash
python test_telegram.py
```

---

## 🚨 Troubleshooting

### Common Issues

**❌ "Unauthorized" Error**
```
Solution: Check your bot token
- Verify token is correct
- Ensure no extra spaces
- Regenerate token if needed via BotFather
```

**❌ "Chat not found" Error**
```
Solution: Check your chat ID
- Verify chat ID is correct
- Send /start to your bot first
- Use @userinfobot to get correct ID
```

**❌ "Bot was blocked by the user"**
```
Solution: Unblock the bot
- Find your bot in Telegram
- Tap "RESTART" or "START"
- Send /start command
```

**❌ No messages received**
```
Solution: Check configuration
- Verify both token and chat ID
- Test with simple curl command
- Check .env file syntax
```

### Debug Steps

1. **Verify Bot Token**
   ```bash
   curl https://api.telegram.org/botYOUR_TOKEN/getMe
   ```

2. **Check Chat ID**
   ```bash
   curl https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```

3. **Test Manual Message**
   ```bash
   curl -X POST \
        -H 'Content-Type: application/json' \
        -d '{"chat_id": "YOUR_CHAT_ID", "text": "Test"}' \
        https://api.telegram.org/botYOUR_TOKEN/sendMessage
   ```

---

## 📞 Getting Help

### Telegram Support Resources
- **BotFather Help**: Send `/help` to @BotFather
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Bot FAQ**: https://core.telegram.org/bots/faq

### Common Commands
- `/start` - Start conversation with bot
- `/help` - Get help from bot
- `/settings` - Bot settings (if implemented)
- `/cancel` - Cancel current operation

---

## 🎯 Quick Setup Summary

1. **Create Bot**: Chat with @BotFather → `/newbot`
2. **Get Token**: Save the token BotFather gives you
3. **Get Chat ID**: Use @userinfobot to get your ID
4. **Configure**: Add token and chat ID to `.env` file
5. **Test**: Run `python src/main.py test`

### Example .env Configuration
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRSTUVWXYZ
TELEGRAM_CHAT_ID=987654321
```

### Enable in config.yaml
```yaml
notifications:
  telegram:
    enabled: true
```

**✅ You're all set! Your trading bot will now send you Telegram notifications.**

---

**🔒 Security Reminder:** Keep your bot token secret and never share it publicly!