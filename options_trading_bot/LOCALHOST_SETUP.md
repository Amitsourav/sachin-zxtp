# 🚀 Running Trading Bot on Localhost

## Quick Start (3 Steps)

### Step 1: Navigate to Web Interface Directory
```bash
cd options_trading_bot/web_interface
```

### Step 2: Make Script Executable (Mac/Linux)
```bash
chmod +x run_local.sh
```

### Step 3: Run the Application

#### On Mac/Linux:
```bash
./run_local.sh
```

#### On Windows:
```cmd
run_local.bat
```

#### Or Manually with Python:
```bash
# Install dependencies
pip install Flask Flask-SocketIO Flask-Login python-dotenv

# Run the app
python app.py
```

---

## 🌐 Access the Dashboard

Once running, open your browser and go to:

### **http://localhost:5000**

---

## 🔐 Login Credentials

### Demo Account:
- **Username:** `demo`
- **Password:** `demo123`

---

## 📱 What You'll See

### 1. Welcome Page
- Landing page with login button
- Feature highlights

### 2. Login Page
- Simple username/password form
- Demo credentials displayed

### 3. Main Dashboard
- **Real-time Status** - Running/Stopped/Paused
- **Capital Display** - ₹1,00,000
- **Today's P&L** - Live profit/loss
- **Control Buttons** - START, PAUSE, STOP
- **Current Positions** - Live position tracking
- **Activity Log** - Recent actions

---

## 🎮 How to Use

### Starting the Bot:
1. Click the big green **"▶️ START TRADING"** button
2. Bot status changes to "RUNNING"
3. Positions will appear as trades execute

### Changing Settings:
1. **Risk Level**: Click Low/Medium/High buttons
2. **Trading Mode**: Toggle between Paper/Live trading
3. Changes apply immediately

### Monitoring:
- Dashboard auto-refreshes every 5 seconds
- Real-time P&L updates
- Color-coded indicators (green = profit, red = loss)

---

## 🛠️ Features Available on Localhost

### Working Features:
✅ Start/Stop/Pause controls  
✅ Status display  
✅ Risk level selection  
✅ Paper/Live trading toggle  
✅ Real-time WebSocket updates  
✅ Responsive design  
✅ Activity logging  

### Demo Features (Simulated):
- Sample positions display
- Mock P&L calculations
- Demo trade history
- Sample performance metrics

---

## 📁 File Structure

```
web_interface/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── run_local.sh          # Mac/Linux startup script
├── run_local.bat         # Windows startup script
└── templates/
    ├── index.html        # Welcome page
    ├── login.html        # Login page
    └── dashboard.html    # Main dashboard
```

---

## 🔧 Troubleshooting

### Port Already in Use:
If you see "Address already in use", change the port:
```python
# In app.py, change the last line to:
socketio.run(app, debug=True, port=5001)  # or any other port
```
Then access at: http://localhost:5001

### Module Not Found:
Install missing modules:
```bash
pip install Flask Flask-SocketIO Flask-Login
```

### Permission Denied (Mac/Linux):
```bash
chmod +x run_local.sh
```

### Python Not Found:
Make sure Python 3.8+ is installed:
```bash
python3 --version
```

---

## 🎨 Customization

### Change Colors/Theme:
Edit the CSS in `templates/dashboard.html`:
```css
/* Change primary color gradient */
background: linear-gradient(135deg, #YOUR_COLOR 0%, #YOUR_COLOR 100%);
```

### Add Your Logo:
Replace the emoji in dashboard.html:
```html
<div class="logo">Your Logo Here</div>
```

### Modify Risk Levels:
In `app.py`, adjust the risk settings:
```python
bot_state = {
    'risk_level': 'low',  # Change default
    ...
}
```

---

## 🔌 Connecting to Real Bot

To connect to actual trading bot (future):

1. **Import Bot Modules** in `app.py`:
```python
from src.core.config import get_settings
from src.risk.risk_manager import RiskManager
from src.brokers.paper_broker import PaperTradingBroker
```

2. **Replace Mock Data** with real calls:
```python
# Instead of bot_state dict, use:
real_status = trading_bot.get_status()
real_positions = broker.get_positions()
```

3. **Add API Authentication**:
```python
# Add proper authentication
from flask_jwt_extended import JWTManager
```

---

## 🚦 System Requirements

### Minimum:
- Python 3.8+
- 1GB RAM
- Modern web browser
- Internet connection (for real trading)

### Recommended:
- Python 3.10+
- 2GB RAM
- Chrome/Firefox/Safari latest version
- Stable internet connection

---

## 📱 Mobile Access

The dashboard is fully responsive. To access from your phone:

1. Find your computer's IP address:
   - Mac: `ifconfig | grep inet`
   - Windows: `ipconfig`
   - Linux: `ip addr show`

2. On your phone's browser, go to:
   ```
   http://YOUR_COMPUTER_IP:5000
   ```
   Example: `http://192.168.1.100:5000`

3. Make sure both devices are on the same WiFi network

---

## 🔒 Security Note

⚠️ **For Development Only**: The current setup is for local testing. For production:

1. Change the secret key
2. Use HTTPS
3. Implement proper authentication
4. Add rate limiting
5. Use environment variables for sensitive data
6. Deploy behind a reverse proxy (nginx)

---

## 💡 Next Steps

After testing on localhost:

1. **Deploy to Cloud** (for 24/7 access):
   - Heroku (free tier available)
   - AWS EC2
   - DigitalOcean
   - Google Cloud Platform

2. **Add Real Trading**:
   - Connect to broker APIs
   - Implement real position tracking
   - Add actual P&L calculation

3. **Enhance Features**:
   - Add charts and graphs
   - Implement backtesting interface
   - Add trade history export
   - Create mobile app

---

## 🆘 Getting Help

If you encounter issues:

1. Check the terminal/console for error messages
2. Verify all dependencies are installed
3. Ensure Python version is 3.8+
4. Try running with `python3` instead of `python`
5. Check if port 5000 is available

---

## 📝 Quick Commands Reference

```bash
# Start server
python app.py

# Install all dependencies
pip install -r requirements.txt

# Check Python version
python --version

# Kill process on port 5000 (if stuck)
# Mac/Linux:
lsof -ti:5000 | xargs kill -9
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

---

**🎉 That's it! Your trading bot dashboard is now running on localhost:5000**

Open your browser, go to http://localhost:5000, and start trading!