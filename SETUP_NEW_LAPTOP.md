# 🚀 SETUP GUIDE FOR NEW LAPTOP

## Step 1: Clone Repository
```bash
git clone https://github.com/Amitsourav/sachin-zxtp.git
```

## Step 2: Navigate to Project
```bash
cd sachin-zxtp/options_trading_bot
```

## Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```
If pip install fails, try:
```bash
pip3 install -r requirements.txt
# OR
python3 -m pip install -r requirements.txt
```

## Step 4: Setup Configuration
```bash
# Copy example config
cp config/config.example.yaml config/config.yaml

# Edit config with your API keys
nano config/config.yaml
# OR use any text editor
```

## Step 5: Test Installation
```bash
# Check Python version
python3 --version

# Test imports
python3 -c "import kiteconnect; print('KiteConnect OK')"
```

## Step 6: Get Access Token
```bash
# Make sure you're in options_trading_bot folder
pwd  # Should show: .../sachin-zxtp/options_trading_bot

# Run access token script
python3 get_access_token.py
```

## Step 7: Run Trading Bot
```bash
# Paper trading
python3 ULTIMATE_915.py

# OR specific scripts
python3 FINAL_paper_trade_zerodha.py
```

## 🔧 COMMON ISSUES & FIXES

### Issue 1: "No such file or directory"
**Solution:** You're in wrong folder!
```bash
# Check current location
pwd

# Go to correct folder
cd ~/sachin-zxtp/options_trading_bot

# Try again
python3 get_access_token.py
```

### Issue 2: "Module not found"
**Solution:** Install dependencies
```bash
pip install kiteconnect pandas numpy pyyaml
```

### Issue 3: "Permission denied"
**Solution:** Make scripts executable
```bash
chmod +x *.py
```

### Issue 4: "Config not found"
**Solution:** Create config file
```bash
cp config/config.example.yaml config/config.yaml
# Add your API keys to config.yaml
```

## 📁 PROJECT STRUCTURE
```
sachin-zxtp/
├── options_trading_bot/     ← YOU MUST BE HERE TO RUN SCRIPTS
│   ├── ULTIMATE_915.py
│   ├── get_access_token.py
│   ├── config/
│   │   └── config.yaml
│   └── src/
└── trading_system/
```

## ✅ QUICK COMMANDS (Run from options_trading_bot folder)

### Daily Trading Commands:
```bash
# 1. Get token (8:30 AM)
python3 get_access_token.py

# 2. Trade (9:14:30 AM)
python3 ULTIMATE_915.py

# 3. Dashboard (after trade)
cd web_interface && python3 app.py
```

## 🎯 ALWAYS REMEMBER
Before running ANY command, make sure you're in:
```bash
sachin-zxtp/options_trading_bot/
```

Not in:
- sachin-zxtp/ (wrong - too high)
- sachin-zxtp/trading_system/ (wrong folder)
- Your home directory (wrong)