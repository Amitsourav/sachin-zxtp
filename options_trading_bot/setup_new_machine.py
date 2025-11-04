#!/usr/bin/env python3
"""
🚀 Trading Bot Setup Script for New Machines
Automatically installs and configures the bot on a fresh system
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_banner():
    print("\n" + "="*60)
    print("🚀 TRADING BOT SETUP FOR NEW MACHINE")
    print("="*60)
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Location: {os.getcwd()}")
    print("="*60 + "\n")

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        print("💡 Please install Python 3.8 or higher")
        return False

def check_required_files():
    """Check if essential files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        "requirements.txt",
        "main.py", 
        "src/core/config.py",
        "web_interface/app.py",
        "config/config.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   • {file}")
        print("\n💡 Please copy all bot files to this directory")
        return False
    else:
        print("✅ All required files present")
        return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True, capture_output=True)
        print("✅ Pip upgraded")
        
        # Install requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Try manual installation:")
        print("   pip3 install pandas numpy pydantic yfinance flask flask-socketio")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    test_modules = [
        "pandas", "numpy", "pydantic", "yfinance", 
        "flask", "flask_socketio", "yaml", "requests"
    ]
    
    failed_imports = []
    for module in test_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("✅ All modules imported successfully")
        return True

def create_directories():
    """Create necessary directories"""
    print("📂 Creating directories...")
    
    directories = ["logs", "data", "__pycache__"]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  ✅ {dir_name}/")
    
    print("✅ Directory structure created")

def test_configuration():
    """Test configuration loading"""
    print("⚙️  Testing configuration...")
    
    try:
        # Test config import
        from src.core.config import ConfigManager
        config = ConfigManager()
        
        print(f"  ✅ Config loaded")
        print(f"  📊 Mode: {config.trading.mode}")
        print(f"  💰 Capital: ₹{config.trading.capital:,}")
        print(f"  🎯 Target: {config.trading.profit_target_percent}%")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_bot_startup():
    """Test if bot can start without errors"""
    print("🤖 Testing bot startup...")
    
    try:
        # Quick import test
        from main import TradingBotOrchestrator
        print("✅ Bot modules loaded successfully")
        
        # Test web interface
        import sys
        sys.path.append("web_interface")
        import app
        print("✅ Web interface loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot startup test failed: {e}")
        return False

def create_quick_start_script():
    """Create a quick start script"""
    print("📝 Creating quick start script...")
    
    script_content = '''#!/usr/bin/env python3
# Quick Start Script - Generated by setup
import subprocess
import sys
import os

print("🚀 Starting Trading Bot...")
print("🔗 Dashboard will be at: http://localhost:8080")
print("🛑 Press Ctrl+C to stop")

try:
    subprocess.run([sys.executable, "start_trading.py"])
except KeyboardInterrupt:
    print("\\n👋 Bot stopped")
except Exception as e:
    print(f"\\n❌ Error: {e}")
'''
    
    with open("quick_start.py", "w") as f:
        f.write(script_content)
    
    # Make executable
    os.chmod("quick_start.py", 0o755)
    print("✅ Created quick_start.py")

def display_next_steps():
    """Display what to do next"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1️⃣  Review config: config/config.yaml")
    print("2️⃣  Test run: python3 start_trading.py")
    print("3️⃣  Open dashboard: http://localhost:8080")
    print("4️⃣  Check logs: tail -f logs/trading_bot.log")
    
    print("\n🚀 Quick Commands:")
    print("  • Start bot: python3 quick_start.py")
    print("  • Paper trade: python3 start_trading.py")  
    print("  • Emergency stop: Ctrl+C")
    
    print("\n⚠️  Remember:")
    print("  • Bot starts in PAPER TRADING mode (safe)")
    print("  • Uses virtual ₹1,00,000 capital")
    print("  • No real money at risk")
    
    print("\n📚 Documentation:")
    print("  • Installation: INSTALLATION_GUIDE.md")
    print("  • Usage: README.md")
    print("  • Telegram: TELEGRAM_SETUP_GUIDE.md")
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print_banner()
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files), 
        ("Dependencies", install_dependencies),
        ("Module Imports", test_imports),
        ("Directories", create_directories),
        ("Configuration", test_configuration),
        ("Bot Startup", test_bot_startup),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
            failed_checks.append(check_name)
    
    # Create helper scripts
    create_quick_start_script()
    
    # Final result
    if failed_checks:
        print(f"\n❌ Setup completed with {len(failed_checks)} issues:")
        for check in failed_checks:
            print(f"   • {check}")
        print("\n💡 Please fix these issues before running the bot")
        return False
    else:
        display_next_steps()
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Setup failed: {e}")
        sys.exit(1)