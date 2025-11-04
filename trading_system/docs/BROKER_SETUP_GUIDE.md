# 🏦 Broker API Setup Guide - 9:15 Strategy Trading System

This guide provides step-by-step instructions for setting up broker APIs that support automated trading in India.

## 🥇 Zerodha Kite Connect Setup (Recommended)

Zerodha Kite Connect is the most popular and well-documented API for Indian retail traders.

### Step 1: Account Requirements
- Active Zerodha trading account
- Demat account with Zerodha
- KYC completion verified
- Options trading enabled

### Step 2: Create Developer Account
1. **Visit Kite Connect Portal**
   - Go to: https://kite.trade/
   - Click on "Sign up" if you don't have a developer account

2. **Register Developer Account**
   - Use the same email as your trading account
   - Verify your email address
   - Complete the registration process

### Step 3: Create API Application
1. **Login to Developer Console**
   - Access: https://developers.kite.trade/
   - Login with your developer credentials

2. **Create New App**
   ```
   App Name: 9:15 Strategy Trading Bot
   App Type: Connect
   Website URL: http://localhost (for personal use)
   Redirect URL: http://localhost:8080
   Description: Automated options trading system
   ```

3. **Get API Credentials**
   - After approval, you'll receive:
     - **API Key** (public)
     - **API Secret** (keep secret)

### Step 4: Generate Access Token
1. **Initial Authorization**
   ```python
   from kiteconnect import KiteConnect
   
   kite = KiteConnect(api_key="your_api_key")
   print(kite.login_url())  # Visit this URL
   ```

2. **Get Request Token**
   - Visit the login URL
   - Login with your Zerodha credentials
   - Allow the app permissions
   - Copy the `request_token` from redirect URL

3. **Generate Session**
   ```python
   data = kite.generate_session("request_token_here", api_secret="your_api_secret")
   access_token = data["access_token"]
   ```

4. **Save Access Token**
   - Store the access token securely
   - This token is valid until you change your password

### Step 5: Configuration
Add to your `.env` file:
```bash
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here  
ZERODHA_ACCESS_TOKEN=your_access_token_here
```

### Step 6: Test Connection
```python
from kiteconnect import KiteConnect

kite = KiteConnect(api_key="your_api_key")
kite.set_access_token("your_access_token")

# Test connection
profile = kite.profile()
print(f"Welcome {profile['user_name']}")
```

### API Costs (Zerodha)
- **Connect API**: ₹2,000/month
- **Historical Data**: Additional ₹2,000/month (optional)
- **WebSocket**: Included with Connect API

---

## 🚀 Upstox API Setup

Upstox provides competitive API pricing and good documentation.

### Step 1: Account Requirements
- Active Upstox trading account
- Demat account with Upstox
- KYC completion verified
- Options trading enabled

### Step 2: Developer Registration
1. **Visit Developer Portal**
   - Go to: https://upstox.com/developer/
   - Click "Get Started"

2. **Register Application**
   ```
   App Name: 9:15 Strategy Bot
   App Type: Personal Trading App
   Redirect URI: http://localhost:8080
   Description: Automated options trading
   ```

### Step 3: API Credentials
1. **Get Credentials**
   - **API Key**
   - **API Secret**
   - **Redirect URI**

2. **Generate Access Token**
   ```python
   import upstox_client
   
   # Step 1: Get authorization URL
   auth_url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={api_key}&redirect_uri={redirect_uri}"
   
   # Step 2: Visit URL, get authorization code
   # Step 3: Exchange code for token
   ```

### Step 4: Configuration
Add to your `.env` file:
```bash
UPSTOX_API_KEY=your_api_key_here
UPSTOX_API_SECRET=your_api_secret_here
UPSTOX_ACCESS_TOKEN=your_access_token_here
```

### API Costs (Upstox)
- **Basic Plan**: ₹999/month
- **Pro Plan**: ₹1,999/month
- **Premium Plan**: ₹4,999/month

---

## 📊 Angel One SmartAPI Setup

Angel One offers competitive pricing for API access.

### Step 1: Account Setup
- Active Angel One trading account
- Complete KYC verification
- Options trading enabled

### Step 2: API Registration
1. **Visit SmartAPI Portal**
   - Go to: https://smartapi.angelbroking.com/
   - Register for API access

2. **Application Details**
   ```
   App Name: 9:15 Strategy
   App Type: Personal Use
   Category: Trading Application
   ```

### Step 3: Get Credentials
- **API Key**
- **Client ID**
- **Password**
- **TOTP Secret**

### Step 4: Configuration
```bash
ANGEL_API_KEY=your_api_key_here
ANGEL_CLIENT_ID=your_client_id_here
ANGEL_PASSWORD=your_password_here
ANGEL_TOTP_SECRET=your_totp_secret_here
```

### API Costs (Angel One)
- **SmartAPI**: ₹999/month
- **Real-time Data**: Included

---

## 🏪 5paisa API Setup

Budget-friendly option with basic API features.

### Step 1: Account Setup
- Active 5paisa trading account
- Complete KYC process
- Enable API access

### Step 2: API Configuration
1. **Contact Support**
   - Email: support@5paisa.com
   - Request API access
   - Provide account details

2. **Get Credentials**
   - **API Key**
   - **App Name**
   - **App Source**
   - **User ID**
   - **Password**

### API Costs (5paisa)
- **API Access**: ₹500/month
- **Real-time Data**: Additional charges

---

## 🔒 Security Best Practices

### API Key Management
1. **Environment Variables**
   ```bash
   # Never hardcode in source code
   export BROKER_API_KEY="your_key"
   export BROKER_API_SECRET="your_secret"
   ```

2. **File Permissions**
   ```bash
   chmod 600 .env  # Restrict access to .env file
   ```

3. **Key Rotation**
   - Rotate API keys periodically
   - Monitor API usage logs
   - Set up alerts for unusual activity

### Access Control
- **IP Whitelisting**: Enable if supported
- **API Rate Limiting**: Monitor and respect limits
- **Session Management**: Implement proper token refresh

---

## 🧪 Testing Your Broker API

### Test Script
```python
#!/usr/bin/env python3
"""
Broker API Test Script
"""

def test_zerodha_api():
    try:
        from kiteconnect import KiteConnect
        
        api_key = "your_api_key"
        access_token = "your_access_token"
        
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        
        # Test profile
        profile = kite.profile()
        print(f"✅ Zerodha API: Connected as {profile['user_name']}")
        
        # Test positions
        positions = kite.positions()
        print(f"✅ Positions retrieved: {len(positions['day'])} day positions")
        
        return True
        
    except Exception as e:
        print(f"❌ Zerodha API test failed: {e}")
        return False

def test_upstox_api():
    # Similar test for Upstox
    pass

def test_paper_trading():
    """Test paper trading functionality"""
    try:
        from src.broker_interface import PaperTradingBroker
        
        broker = PaperTradingBroker()
        if broker.authenticate():
            print("✅ Paper trading broker working")
            
            # Test order
            result = broker.place_order("TEST", 1, "MARKET")
            if result['success']:
                print("✅ Paper order placement working")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Paper trading test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Broker APIs...")
    
    # Test paper trading first
    test_paper_trading()
    
    # Test real broker APIs
    test_zerodha_api()
    # test_upstox_api()
```

---

## 📋 API Comparison Table

| Feature | Zerodha | Upstox | Angel One | 5paisa |
|---------|---------|---------|-----------|---------|
| **Monthly Cost** | ₹2,000 | ₹999+ | ₹999 | ₹500 |
| **Documentation** | Excellent | Good | Good | Basic |
| **WebSocket** | ✅ | ✅ | ✅ | ❌ |
| **Historical Data** | ✅ | ✅ | ✅ | Limited |
| **Order Types** | Comprehensive | Good | Good | Basic |
| **Support** | Excellent | Good | Good | Limited |
| **Reliability** | Very High | High | High | Medium |
| **Rate Limits** | 3 req/sec | 5 req/sec | 10 req/sec | 1 req/sec |

## 🏆 Recommendation

**For 9:15 Strategy Trading System:**

1. **Best Overall**: Zerodha Kite Connect
   - Most reliable and well-documented
   - Large developer community
   - Excellent support

2. **Budget Option**: Upstox API
   - Good balance of features and cost
   - Reliable performance
   - Growing developer support

3. **Testing**: Always start with Paper Trading
   - Test all functionality without risk
   - Validate order flows
   - Check system integration

---

## 🚨 Important Notes

### Regulatory Compliance
- Automated trading is allowed for retail traders
- Ensure compliance with SEBI regulations
- Maintain proper trade records
- Understand tax implications

### Risk Management
- Start with small position sizes
- Implement circuit breakers
- Monitor API usage limits
- Have manual override procedures

### Support Contacts

**Zerodha Support:**
- Email: connect@zerodha.com
- Phone: 080-47181888
- Telegram: @kiteconnect

**Upstox Support:**
- Email: connect@upstox.com
- Support Portal: https://upstox.com/support/

**Angel One Support:**
- Email: support@angelbroking.com
- Phone: 022-62738000

---

**⚠️ Disclaimer:** API access and costs are subject to change. Always verify current pricing and terms with the broker before proceeding.