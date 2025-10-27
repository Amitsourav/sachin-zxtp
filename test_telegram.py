#!/usr/bin/env python3
"""
Test Telegram Bot Setup
Verifies your Telegram configuration is working
"""

import asyncio
import sys
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.notifications.telegram_bot import TelegramNotifier
from src.core.config import ConfigManager


async def test_telegram():
    """Test Telegram bot configuration"""
    print("\n" + "="*50)
    print("TELEGRAM BOT TEST")
    print("="*50)
    
    try:
        # Load configuration
        print("\n1. Loading configuration...")
        config = ConfigManager('config/config.yaml')
        
        if not config.notifications.telegram_enabled:
            print("❌ Telegram is disabled in config")
            print("   Set telegram_enabled: true in config.yaml")
            return False
            
        if not config.notifications.telegram_token:
            print("❌ Telegram token not found")
            print("   Add your bot token to config.yaml")
            return False
            
        if not config.notifications.telegram_chat_id:
            print("❌ Telegram chat ID not found")
            print("   Add your chat ID to config.yaml")
            return False
            
        print("✅ Configuration loaded")
        print(f"   Token: {config.notifications.telegram_token[:20]}...")
        print(f"   Chat ID: {config.notifications.telegram_chat_id}")
        
        # Initialize bot
        print("\n2. Initializing Telegram bot...")
        telegram = TelegramNotifier(config)
        await telegram.initialize()
        print("✅ Bot initialized")
        
        # Send test message
        print("\n3. Sending test message...")
        await telegram.send_message(
            "🤖 Trading Bot Test\n"
            "━━━━━━━━━━━━\n"
            "✅ Telegram setup successful!\n"
            "Your bot is ready to send notifications."
        )
        print("✅ Message sent!")
        
        # Send sample trade alert
        print("\n4. Sending sample trade alert...")
        sample_trade = {
            'symbol': 'RELIANCE2800CE',
            'quantity': 250,
            'entry_price': 45.50,
            'target': 49.14,
            'stop_loss': 31.85
        }
        await telegram.send_trade_alert(sample_trade)
        print("✅ Trade alert sent!")
        
        # Send sample P&L update
        print("\n5. Sending sample P&L update...")
        sample_position = {
            'symbol': 'RELIANCE2800CE',
            'quantity': 250
        }
        await telegram.send_position_update(
            sample_position,
            current_price=48.50,
            pnl=750,
            pnl_percent=6.6
        )
        print("✅ P&L update sent!")
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
        print("\n📱 Check your Telegram for messages")
        print("   You should have received 3 test messages")
        
        return True
        
    except FileNotFoundError:
        print("\n❌ Configuration file not found!")
        print("   Create config/config.yaml first")
        print("\nExample config:")
        print("""
notifications:
  telegram_enabled: true
  telegram_token: "YOUR_BOT_TOKEN"
  telegram_chat_id: "YOUR_CHAT_ID"
        """)
        return False
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nCommon issues:")
        print("1. Wrong bot token - Get from @BotFather")
        print("2. Wrong chat ID - Get from @userinfobot")
        print("3. Haven't started chat with your bot")
        print("4. Network/firewall blocking Telegram")
        return False


async def interactive_setup():
    """Interactive Telegram setup helper"""
    print("\n" + "="*50)
    print("TELEGRAM BOT INTERACTIVE SETUP")
    print("="*50)
    
    print("\nLet's set up your Telegram bot step by step!")
    
    # Check if config exists
    config_path = Path('config/config.yaml')
    if not config_path.exists():
        print("\n❌ No config file found. Creating one...")
        config_path.parent.mkdir(exist_ok=True)
        
        # Get user input
        print("\n1. Create a bot:")
        print("   - Open Telegram")
        print("   - Search for @BotFather")
        print("   - Send /newbot")
        print("   - Follow instructions")
        token = input("\nEnter your bot token: ").strip()
        
        print("\n2. Get your chat ID:")
        print("   - Search for @userinfobot")
        print("   - Start chat")
        print("   - It will show your ID")
        chat_id = input("\nEnter your chat ID: ").strip()
        
        # Create config
        config = {
            'notifications': {
                'telegram_enabled': True,
                'telegram_token': token,
                'telegram_chat_id': chat_id,
                'alert_on_trade': True,
                'alert_on_target': True,
                'alert_on_stop_loss': True,
                'daily_summary': True
            },
            'trading': {
                'mode': 'paper',
                'capital': 100000,
                'profit_target_percent': 8.0,
                'stop_loss_percent': 30.0,
                'pcr_min': 0.7,
                'pcr_max': 1.5
            },
            'risk': {
                'max_risk_per_trade': 2.0,
                'max_daily_loss': 5000,
                'max_positions': 1,
                'stop_loss_enabled': True
            }
        }
        
        # Save config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        print("\n✅ Configuration saved!")
        
    # Test the setup
    print("\n3. Testing your setup...")
    success = await test_telegram()
    
    if success:
        print("\n🎉 Congratulations! Your Telegram bot is ready!")
        print("   You can now run: python3 main.py")
    else:
        print("\n😔 Setup failed. Please check the errors above.")


async def main():
    """Main entry point"""
    print("\n🤖 Telegram Bot Setup Utility")
    print("Choose an option:")
    print("1. Test existing configuration")
    print("2. Interactive setup (create new config)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        await test_telegram()
    elif choice == "2":
        await interactive_setup()
    else:
        print("Invalid choice. Please run again.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")