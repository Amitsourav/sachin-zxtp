# 💻 Trading Bot Installation Guide
## Moving to Different Laptop/Account

### 📦 **What You Need to Copy**

#### **Essential Files (Must Copy):**
```
options_trading_bot/
├── src/                     # Core bot code
├── web_interface/           # Dashboard
├── config/config.yaml       # Your settings
├── requirements.txt         # Dependencies
├── main.py                  # Main bot
├── start_trading.py         # Python starter
└── morning_trading_starter.ipynb  # Jupyter notebook
```

#### **Optional Files:**
```
├── logs/                    # Historical logs (optional)
├── data/                    # Database (optional) 
└── *.md files              # Documentation (helpful)
```

---

## 🔧 **Step-by-Step Installation**

### **Method 1: Copy Entire Folder** ⭐ (Easiest)

#### **On Original Laptop:**
```bash
# Compress the entire project
cd "/Users/sumanprasad/Downloads/sachin zxtp/"
tar -czf trading_bot_backup.tar.gz options_trading_bot/

# Or use zip
zip -r trading_bot_backup.zip options_trading_bot/
```

#### **On New Laptop:**
```bash
# Extract to desired location
tar -xzf trading_bot_backup.tar.gz
# Or: unzip trading_bot_backup.zip

# Navigate to folder
cd options_trading_bot/
```

### **Method 2: Manual Setup** 🔧 (If copying fails)

#### **1. Create Project Structure:**
```bash
# On new laptop
mkdir -p trading_bot/{src,web_interface,config,logs}
cd trading_bot/
```

#### **2. Copy Core Files:**
Copy these files from original laptop:
- All files in `src/` folder
- All files in `web_interface/` folder  
- `config/config.yaml`
- `requirements.txt`
- `main.py`
- `start_trading.py`

---

## 🐍 **Python Setup on New Machine**

### **1. Check Python Version:**
```bash
python3 --version
# Should be Python 3.8 or higher
```

### **2. Install Dependencies:**
```bash
# Navigate to project folder
cd trading_bot/

# Install all requirements
pip3 install -r requirements.txt

# If some fail, install individually:
pip3 install pandas numpy pydantic yfinance flask
```

### **3. Install Missing System Dependencies:**
```bash
# On macOS:
brew install python3

# On Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip

# On Windows:
# Download from python.org
```

---

## ⚙️ **Configuration Setup**

### **1. Update Config for New Machine:**
```bash
# Edit config file
nano config/config.yaml
# Or: code config/config.yaml
```

### **2. Verify Settings:**
```yaml
trading:
  mode: paper              # Start with paper trading
  use_live_data: true      # Use real market data
  capital: 100000          # Virtual capital

broker:
  name: "paper"            # Safe for testing

notifications:
  telegram_enabled: false  # Setup later if needed
```

### **3. Test Configuration:**
```python
python3 -c "
from src.core.config import ConfigManager
config = ConfigManager()
print('✅ Config loaded successfully')
print(f'Mode: {config.trading.mode}')
print(f'Capital: ₹{config.trading.capital:,}')
"
```

---

## 🧪 **Testing Installation**

### **1. Quick Dependency Test:**
```python
python3 -c "
import pandas, numpy, pydantic, yfinance, flask
print('✅ All dependencies working')
"
```

### **2. Bot Startup Test:**
```bash
# Test main bot (will exit quickly - that's normal)
python3 main.py

# Should see startup banner without errors
```

### **3. Web Dashboard Test:**
```bash
# Start dashboard
cd web_interface/
python3 app.py

# Open browser: http://localhost:8080
# Should see login page
```

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: Module Not Found**
```bash
# Error: No module named 'xyz'
# Solution:
pip3 install xyz

# Or install all:
pip3 install -r requirements.txt
```

### **Issue 2: Permission Denied**
```bash
# Error: Permission denied
# Solution (macOS/Linux):
chmod +x start_trading.py
chmod +x *.sh

# Or run with python directly:
python3 start_trading.py
```

### **Issue 3: Port Already in Use**
```bash
# Error: Port 8080 in use
# Solution: Kill existing process
sudo lsof -ti:8080 | xargs kill -9

# Or use different port in web_interface/app.py
```

### **Issue 4: Config File Not Found**
```bash
# Error: config.yaml not found
# Solution: Create from template
cp config/config.yaml.example config/config.yaml

# Or let bot create default:
python3 -c "from src.core.config import ConfigManager; ConfigManager()"
```

---

## 📱 **Account-Specific Settings**

### **For Different Trading Accounts:**

#### **1. Separate Config Files:**
```bash
# Create account-specific configs
cp config/config.yaml config/config_account1.yaml
cp config/config.yaml config/config_account2.yaml

# Use specific config:
python3 main.py --config config/config_account1.yaml
```

#### **2. Different Data Folders:**
```yaml
# In config file
database_url: "sqlite:///./data/account1_trading.db"
logging:
  file: "logs/account1_trading.log"
```

#### **3. Different Telegram Bots:**
```yaml
# Account 1
notifications:
  telegram_token: "ACCOUNT1_BOT_TOKEN"
  telegram_chat_id: "ACCOUNT1_CHAT_ID"

# Account 2  
notifications:
  telegram_token: "ACCOUNT2_BOT_TOKEN"
  telegram_chat_id: "ACCOUNT2_CHAT_ID"
```

---

## 🔐 **Security Considerations**

### **1. Clean Sensitive Data:**
```bash
# Before copying to new machine:
# Remove logs with sensitive info
rm -rf logs/*

# Remove temporary files
rm -rf __pycache__/
find . -name "*.pyc" -delete
```

### **2. Environment Variables:**
```bash
# Instead of hardcoding in config:
export TRADING_API_KEY="your_key"
export TRADING_SECRET="your_secret"

# Reference in config:
# api_key: ${TRADING_API_KEY}
```

### **3. Different Broker Accounts:**
```yaml
# Use different API credentials per machine
broker:
  api_key: "MACHINE_SPECIFIC_KEY"
  api_secret: "MACHINE_SPECIFIC_SECRET"
```

---

## 🚀 **Quick Setup Script**

Save this as `setup_new_machine.py`:

```python
#!/usr/bin/env python3
import subprocess
import sys
import os

def setup_trading_bot():
    print("🚀 Setting up Trading Bot on new machine...")
    
    # Check Python
    try:
        subprocess.run([sys.executable, "--version"], check=True)
        print("✅ Python found")
    except:
        print("❌ Python not found - please install Python 3.8+")
        return
    
    # Install dependencies
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
    except:
        print("❌ Failed to install dependencies")
        return
    
    # Test imports
    try:
        subprocess.run([sys.executable, "-c", "import pandas, yfinance, flask"], check=True)
        print("✅ Core modules working")
    except:
        print("❌ Module import failed")
        return
    
    # Create directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    print("✅ Directories created")
    
    # Test config
    try:
        subprocess.run([sys.executable, "-c", "from src.core.config import ConfigManager; ConfigManager()"], check=True)
        print("✅ Configuration working")
    except:
        print("❌ Configuration failed")
        return
    
    print("\n🎉 Setup complete! Ready to trade.")
    print("💡 Next: Run 'python3 start_trading.py'")

if __name__ == "__main__":
    setup_new_machine()
```

---

## 📋 **Installation Checklist**

### **Before Moving:**
- [ ] Copy entire `options_trading_bot/` folder
- [ ] Backup `config/config.yaml` with your settings
- [ ] Note any custom modifications you made
- [ ] Clean sensitive data if needed

### **On New Machine:**
- [ ] Extract/copy files to desired location
- [ ] Install Python 3.8+ if not present
- [ ] Run `pip3 install -r requirements.txt`
- [ ] Test with `python3 setup_new_machine.py`
- [ ] Verify config settings
- [ ] Test run with `python3 start_trading.py`

### **Final Verification:**
- [ ] Bot starts without errors
- [ ] Web dashboard accessible at localhost:8080
- [ ] Paper trading mode enabled
- [ ] No sensitive data exposed

---

## 💡 **Pro Tips**

1. **Use Git for sync** (if comfortable):
   ```bash
   git clone your_repo_url
   ```

2. **Cloud storage sync**:
   - Put folder in Dropbox/iCloud
   - Access from any machine

3. **Virtual environments**:
   ```bash
   python3 -m venv trading_env
   source trading_env/bin/activate
   pip install -r requirements.txt
   ```

4. **Docker container** (advanced):
   - Package entire environment
   - Run identically anywhere

**Your bot is now portable and ready to run anywhere! 🌍**