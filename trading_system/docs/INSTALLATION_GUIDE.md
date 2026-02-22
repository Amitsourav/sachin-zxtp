# 🚀 Complete Installation Guide - 9:15 Strategy Trading System

This comprehensive guide will take you through the entire installation process step-by-step.

## 📋 What You Need to Get Started

### Essential Requirements
- [ ] **Trading Account** with Zerodha, Upstox, or other supported broker
- [ ] **Computer/VPS** with Python 3.8+ and stable internet
- [ ] **API Access** from your broker (₹999-₹2000/month)
- [ ] **Basic Trading Knowledge** of options and PCR analysis
- [ ] **30 minutes** for initial setup

### Optional but Recommended
- [ ] **Telegram Account** for real-time notifications
- [ ] **Email Account** for backup notifications  
- [ ] **VPS/Cloud Server** for 24/7 operation
- [ ] **Backup Internet** for reliability

---

## 🏗️ Phase 1: System Preparation

### Step 1: Check Your System
```bash
# Check Python version (must be 3.8+)
python --version
# or
python3 --version

# Check if pip is installed
pip --version
```

**Required Output:**
```
Python 3.8.x or higher
pip 21.x.x or higher
```

### Step 2: Download the System
```bash
# If you have git
git clone <repository-url>
cd trading_system

# Or extract the downloaded folder
unzip trading_system.zip
cd trading_system
```

### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# For virtual environment (recommended)
python -m venv trading_env
source trading_env/bin/activate  # On Windows: trading_env\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Run Initial Setup
```bash
# Run the installation script
python install.py
```

**Expected Output:**
```
🎯 9:15 Strategy Trading System Installation
==================================================

✅ Python 3.9.x is compatible
✅ Created directory: logs
✅ Created directory: data
✅ Dependencies installed successfully
✅ Created .env from template
✅ Configuration file found: config/config.yaml
✅ Installation completed successfully!
```

---

## 🏦 Phase 2: Broker Setup

### Choose Your Broker

**Recommendation for Beginners:**
1. **Zerodha** (Most Popular)
   - Cost: ₹2,000/month
   - Best documentation
   - Excellent support

2. **Upstox** (Budget Option)
   - Cost: ₹999/month
   - Good features
   - Competitive pricing

### Step 1: Get API Access

**For Zerodha:**
1. Visit https://kite.trade/
2. Create developer account
3. Create new app
4. Get API Key and Secret
5. Generate Access Token

**For Upstox:**
1. Visit https://upstox.com/developer/
2. Register application
3. Get API credentials

📖 **Detailed Guide:** See `docs/BROKER_SETUP_GUIDE.md`

### Step 2: Configure Broker Credentials
```bash
# Edit .env file
nano .env  # or use any text editor
```

**Add your credentials:**
```bash
# For Zerodha
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here  
ZERODHA_ACCESS_TOKEN=your_access_token_here

# For Upstox
UPSTOX_API_KEY=your_api_key_here
UPSTOX_API_SECRET=your_api_secret_here
UPSTOX_ACCESS_TOKEN=your_access_token_here
```

### Step 3: Test Broker Connection
```bash
# Test your broker setup
python src/main.py test
```

**Expected Output:**
```
✅ Broker connection successful
✅ Paper trading broker working
```

---

## 📱 Phase 3: Notifications Setup (Optional)

### Telegram Setup (Recommended)

**Step 1: Create Telegram Bot**
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Choose name: "9:15 Strategy Bot"
5. Choose username: "your_name_915_bot"
6. Save the bot token

**Step 2: Get Your Chat ID**
1. Search for `@userinfobot`
2. Send `/start`
3. Copy your User ID

**Step 3: Configure Telegram**
```bash
# Add to .env file
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRSTUVWXYZ
TELEGRAM_CHAT_ID=987654321
```

**Step 4: Enable in Config**
```yaml
# Edit config/config.yaml
notifications:
  telegram:
    enabled: true
```

📖 **Detailed Guide:** See `docs/TELEGRAM_SETUP_GUIDE.md`

### Email Setup (Alternative)

**Step 1: Gmail App Password**
1. Enable 2-factor authentication on Gmail
2. Generate app password
3. Use app password (not your regular password)

**Step 2: Configure Email**
```bash
# Add to .env file
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_RECIPIENT=recipient@gmail.com
```

**Step 3: Enable in Config**
```yaml
notifications:
  email:
    enabled: true
```

---

## ⚙️ Phase 4: Strategy Configuration

### Step 1: Review Default Settings
```yaml
# config/config.yaml
trading:
  pcr_min_range: 0.7          # Minimum PCR
  pcr_max_range: 1.5          # Maximum PCR  
  profit_target_percent: 8.0   # Profit target
  execution_time: "09:15:00"   # Trade time
```

### Step 2: Customize Risk Parameters
```yaml
risk:
  max_daily_trades: 1          # Max trades per day
  volatility_threshold: 25.0   # VIX threshold
  trading_holidays_check: true # Check holidays
```

### Step 3: Set Paper Trading (Start Here)
```yaml
broker:
  paper_trading: true  # Always start with paper trading
```

---

## 🧪 Phase 5: Testing & Validation

### Step 1: System Component Test
```bash
# Test all components
python src/main.py test
```

**Expected Output:**
```
✅ Today is a trading day
✅ Broker connection successful  
✅ Telegram notification test
✅ Paper trading broker working
Component testing completed
```

### Step 2: Paper Trading Test
```bash
# Run in paper trading mode
python src/main.py run --paper
```

**Expected Behavior:**
- System waits until 9:14 AM for pre-market scan
- Analyzes NIFTY50 gainers
- Shows PCR calculations
- Places paper trades if conditions met
- Monitors positions for profit target

### Step 3: Backtesting
```bash
# Test strategy on historical data
python src/main.py backtest -m 3
```

**Review Results:**
- Win rate should be >60%
- Average PnL should be positive
- Maximum drawdown should be acceptable

---

## 📊 Phase 6: Go-Live Preparation

### Step 1: Paper Trading Period
- [ ] Run paper trading for **minimum 1 week**
- [ ] Analyze at least **20+ paper trades**
- [ ] Verify win rate and risk metrics
- [ ] Check system stability

### Step 2: Live Trading Transition
```yaml
# Change in config/config.yaml
broker:
  paper_trading: false  # Enable live trading
```

### Step 3: Live Trading Start
```bash
# For live trading
python src/main.py run
```

**⚠️ Important:** Start with small position sizes!

---

## 🚀 Phase 7: Deployment Options

### Option 1: Local Computer
**Pros:** Full control, no additional costs
**Cons:** Must keep computer running during trading hours

```bash
# Run in background (Linux/Mac)
nohup python src/main.py run > trading.log 2>&1 &

# Windows (use Task Scheduler)
# Create task to run: python src/main.py run
```

### Option 2: VPS/Cloud Server
**Pros:** 24/7 operation, reliable internet
**Cons:** Monthly costs (₹500-₹1500/month)

**Recommended VPS Providers:**
- **DigitalOcean**: $5/month droplet
- **AWS EC2**: t3.micro instance
- **Google Cloud**: e2-micro instance
- **Vultr**: $3.5/month VPS

### Option 3: Raspberry Pi
**Pros:** Low power consumption, dedicated device
**Cons:** Initial setup complexity

---

## 📋 Daily Operation Checklist

### Before Market Hours (9:00 AM)
- [ ] Check system status: `python src/main.py status`
- [ ] Verify internet connectivity
- [ ] Check if today is trading day
- [ ] Ensure sufficient margin in trading account

### During Trading Hours
- [ ] Monitor Telegram/Email notifications
- [ ] Check logs: `tail -f logs/trading.log`
- [ ] Watch for any error alerts

### After Market Hours (3:30 PM)
- [ ] Review trade performance
- [ ] Check daily summary
- [ ] Analyze any errors or issues
- [ ] Update strategy parameters if needed

---

## 🔧 Maintenance & Updates

### Weekly Tasks
- [ ] Review trading performance
- [ ] Check system resource usage
- [ ] Update market holiday calendar
- [ ] Backup configuration files

### Monthly Tasks
- [ ] Analyze strategy performance
- [ ] Review and rotate API keys
- [ ] Check for system updates
- [ ] Optimize strategy parameters

---

## 🆘 Emergency Procedures

### If System Fails During Trading
1. **Immediate Action:**
   ```bash
   # Check running status
   python src/main.py status
   
   # Restart if needed
   python src/main.py run
   ```

2. **Manual Intervention:**
   - Login to broker manually
   - Check open positions
   - Close positions manually if needed

3. **Contact Support:**
   - Broker support for trading issues
   - System developer for technical issues

### Emergency Contacts
```
Zerodha Support: 080-47181888
Upstox Support: 022-61171700
System Emergency: [Your contact info]
```

---

## ✅ Installation Complete!

### Verification Checklist
- [ ] All dependencies installed
- [ ] Broker API working
- [ ] Notifications configured
- [ ] Paper trading tested
- [ ] Backtesting completed
- [ ] System monitoring set up

### Next Steps
1. **Start with Paper Trading** for 1-2 weeks
2. **Monitor Performance** and analyze results  
3. **Optimize Parameters** based on results
4. **Gradually Move to Live Trading** with small sizes
5. **Scale Up** after confidence is built

### Getting Help
- **Documentation**: Check all files in `docs/` folder
- **Logs**: Check `logs/` directory for error details
- **Testing**: Run `python src/main.py test` anytime
- **Status**: Check `python src/main.py status` for current state

---

**🎉 Congratulations! Your 9:15 Strategy Trading System is ready to use.**

**⚠️ Remember:** Always start with paper trading and understand the risks before using real money!