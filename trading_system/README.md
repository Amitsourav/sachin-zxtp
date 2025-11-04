# 9:15 Strategy - Automated Options Trading System

An intelligent, rule-based automated trading system designed to trade NIFTY50 option contracts using pre-market analysis and precise timing at market open (9:15 AM IST).

## 🎯 Strategy Overview

The **9:15 Strategy** automatically:

1. **Pre-market Scan (9:14 AM)**: Identifies top NIFTY50 gainers with highest percentage gain
2. **Option Analysis**: Finds ATM (At-the-Money) strike price and calculates Put/Call Ratio (PCR)
3. **PCR Filter**: Only trades if PCR is between 0.7-1.5, otherwise moves to next gainer
4. **Execution (9:15 AM)**: Places buy order for selected ATM Call option
5. **Exit Strategy**: Auto-exits at 8% profit target, no re-entry allowed

## 🚀 Features

- ✅ **Fully Automated**: No manual intervention required
- 📊 **Real-time Data**: Uses NSE APIs and free data sources
- 🤖 **Paper Trading**: Safe testing mode included
- 📈 **Backtesting**: Historical strategy performance analysis
- 📱 **Notifications**: Telegram and Email alerts
- 🔒 **Risk Management**: Built-in volatility filters and position limits
- 📋 **Comprehensive Logging**: Detailed trade and system logs
- ⚙️ **Configurable**: Easy parameter adjustments

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- 2GB RAM minimum
- Stable internet connection
- Windows/Linux/macOS

### Broker Requirements
- Active trading account with supported broker (Zerodha/Upstox)
- API access enabled
- Sufficient margin for options trading

## 🛠️ Installation

### 1. Clone/Download the Project
```bash
# If using git
git clone <repository-url>
cd trading_system

# Or extract the downloaded folder
cd trading_system
```

### 2. Install Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

### 3. Configuration Setup

#### a) Copy Environment File
```bash
cp .env.example .env
```

#### b) Edit Configuration
Edit `config/config.yaml` and `.env` files with your settings:

**For Paper Trading (Recommended for testing):**
```yaml
# config/config.yaml
broker:
  paper_trading: true  # Start with paper trading
  
notifications:
  telegram:
    enabled: true  # Enable if you want notifications
```

**For Live Trading:**
```yaml
# config/config.yaml
broker:
  name: "zerodha"  # or "upstox"
  paper_trading: false
```

```bash
# .env file
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
ZERODHA_ACCESS_TOKEN=your_access_token_here

TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## 🎮 Usage

### Quick Start (Paper Trading)
```bash
# Test system components
python src/main.py test

# Run strategy in paper trading mode
python src/main.py run --paper
```

### Backtesting
```bash
# Quick 6-month backtest
python src/main.py backtest

# Custom date range backtest
python src/main.py backtest -s 2024-01-01 -e 2024-06-30

# Quick 3-month backtest
python src/main.py backtest -m 3
```

### Live Trading
```bash
# After configuring broker credentials
python src/main.py run
```

### System Status
```bash
# Check system status
python src/main.py status
```

## 📊 Strategy Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| PCR Range | 0.7 - 1.5 | Put/Call Ratio filter range |
| Profit Target | 8% | Exit target percentage |
| Scan Time | 9:14 AM | Pre-market scan timing |
| Execution Time | 9:15 AM | Trade execution timing |
| Max Daily Trades | 1 | Maximum trades per day |
| VIX Threshold | 25 | Market volatility filter |

## 🔧 Configuration

### Trading Parameters
```yaml
trading:
  pcr_min_range: 0.7
  pcr_max_range: 1.5
  profit_target_percent: 8.0
  execution_time: "09:15:00"
  timezone: "Asia/Kolkata"
```

### Risk Management
```yaml
risk:
  max_daily_trades: 1
  trading_holidays_check: true
  market_volatility_filter: true
  volatility_threshold: 25.0
```

### Notifications
```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "your_bot_token"
    chat_id: "your_chat_id"
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    email: "your_email@gmail.com"
    password: "your_app_password"
```

## 📱 Setting Up Notifications

### Telegram Setup
1. Create a bot: Message @BotFather on Telegram
2. Send `/newbot` and follow instructions
3. Get your bot token
4. Get your chat ID: Message @userinfobot
5. Add credentials to `.env` file

### Email Setup
1. Enable 2-factor authentication on Gmail
2. Generate app password
3. Add credentials to configuration

## 🏗️ Broker Setup

### Zerodha Kite Connect
1. Visit [Kite Connect](https://kite.trade/)
2. Create developer account
3. Create new app
4. Get API key and secret
5. Generate access token

### Upstox API
1. Visit [Upstox Developer](https://upstox.com/developer/)
2. Create account and app
3. Get API credentials
4. Configure in settings

## 📁 Project Structure

```
trading_system/
├── src/
│   ├── main.py              # Main application entry point
│   ├── trading_strategy.py  # Core strategy logic
│   ├── data_fetcher.py      # Market data fetching
│   ├── broker_interface.py  # Broker API integration
│   ├── notifications.py     # Notification system
│   ├── backtesting.py       # Backtesting engine
│   ├── config_manager.py    # Configuration management
│   └── logger.py            # Logging system
├── config/
│   └── config.yaml          # Main configuration file
├── logs/                    # Log files directory
├── data/                    # Data storage directory
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🔍 Monitoring & Logs

### Log Files
- `logs/trading.log` - Main application logs
- `logs/trades.log` - Trade execution records
- `logs/errors.log` - Error logs

### Real-time Monitoring
```bash
# Watch main log
tail -f logs/trading.log

# Watch trade log
tail -f logs/trades.log
```

## 🧪 Testing

### Paper Trading
Always test with paper trading before live trading:
```bash
python src/main.py run --paper
```

### Component Testing
```bash
python src/main.py test
```

### Backtesting
```bash
# Test strategy on historical data
python src/main.py backtest -m 6
```

## ⚠️ Risk Warnings

1. **Options Trading Risk**: Options can lose 100% value quickly
2. **Market Risk**: Past performance doesn't guarantee future results
3. **Technical Risk**: System failures can cause losses
4. **Regulatory Risk**: Ensure compliance with local regulations

## 🛡️ Safety Features

- **Paper Trading Mode**: Test without real money
- **Daily Trade Limits**: Maximum 1 trade per day
- **Volatility Filters**: Skip trading on high VIX days
- **Holiday Detection**: Automatic holiday calendar
- **Position Monitoring**: Real-time P&L tracking
- **Error Handling**: Comprehensive error management

## 🔧 Troubleshooting

### Common Issues

1. **"No suitable trading signal found"**
   - Check PCR range settings
   - Verify market data connectivity
   - Check if it's a trading day

2. **"Broker authentication failed"**
   - Verify API credentials
   - Check token expiry
   - Ensure API is enabled

3. **"Data fetching error"**
   - Check internet connectivity
   - Verify NSE website accessibility
   - Try alternative data sources

### Debug Mode
```bash
python src/main.py run --verbose
```

## 📈 Performance Optimization

### System Requirements
- Use SSD for faster data access
- Ensure stable internet (>10 Mbps)
- Consider VPS for 24/7 operation

### Configuration Tips
- Adjust PCR range based on market conditions
- Monitor and adjust profit targets
- Use backtesting to optimize parameters

## 🚀 Deployment

### Local Deployment
```bash
# Run as background service (Linux/Mac)
nohup python src/main.py run > output.log 2>&1 &
```

### Cloud Deployment
1. **AWS EC2**: Deploy on t3.micro instance
2. **Google Cloud**: Use e2-micro instance
3. **DigitalOcean**: Basic droplet sufficient

### Scheduling
```bash
# Add to crontab for daily execution
crontab -e
# Add line: 0 9 * * 1-5 cd /path/to/trading_system && python src/main.py run
```

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review log files for errors
3. Test with paper trading first
4. Verify all configurations

## 📝 Disclaimer

This software is for educational and research purposes. Users are responsible for:
- Understanding options trading risks
- Complying with local regulations
- Testing thoroughly before live trading
- Managing their own risk exposure

**USE AT YOUR OWN RISK. NO GUARANTEES OF PROFIT.**

## 📄 License

This project is provided as-is for educational purposes. Users assume all responsibility for its use.

---

**Happy Trading! 📈**