# 🔐 Zerodha Access Token Setup

## Quick Fix Steps:

### Step 1: Open this URL in your browser
```
https://kite.zerodha.com/connect/login?api_key=ke8cqy177kub89v8&v=3
```

### Step 2: Login with your Zerodha credentials
- Enter your User ID
- Enter your Password  
- Complete 2FA if required

### Step 3: After login, you'll be redirected to:
```
127.0.0.1:5000/?request_token=XXXXXXXXXX&action=login&status=success
```

### Step 4: Copy the request_token value from the URL
Example: If URL is `127.0.0.1:5000/?request_token=ABC123XYZ&action=login`
Copy: `ABC123XYZ`

### Step 5: Run this command with your token:
```bash
cd "/Users/sumanprasad/Downloads/sachin zxtp/options_trading_bot"
python3 -c "
from kiteconnect import KiteConnect
import yaml

request_token = 'PASTE_YOUR_REQUEST_TOKEN_HERE'
api_key = 'ke8cqy177kub89v8'
api_secret = 'pq3jxj1id7nf2q3xytttarbc0qz4z7on'

kite = KiteConnect(api_key=api_key)
data = kite.generate_session(request_token, api_secret=api_secret)
access_token = data['access_token']

# Update config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
config['broker']['access_token'] = access_token
with open('config/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print(f'✅ Access Token Updated: {access_token[:20]}...')
"
```

### Step 6: Test Connection
```bash
python3 test_zerodha_connection.py
```

---

## Alternative: Paper Trading (No Login Required)

If you just want to test the bot without real Zerodha connection:

```bash
python3 paper_trade_live.py
```

This will:
- Use simulated trading
- No real money involved
- No Zerodha login needed
- Perfect for testing

---

## Common Issues:

1. **Token Expires Daily**: Generate new token each day at 7:30 AM
2. **Wrong API Key/Secret**: Verify credentials in Zerodha Console
3. **2FA Issues**: Complete PIN/TOTP authentication
4. **Browser Issues**: Try different browser or incognito mode