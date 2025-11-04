#!/usr/bin/env python3
"""
Installation and setup script for 9:15 Strategy Trading System
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Check if pip is available
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        
        # Install requirements
        requirements_file = "requirements.txt"
        if os.path.exists(requirements_file):
            print(f"Installing packages from {requirements_file}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", requirements_file
            ])
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Requirements file not found: {requirements_file}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print("❌ pip not found. Please install pip first.")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["logs", "data", "config"]
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def setup_environment_file():
    """Setup environment file from template"""
    print("\n⚙️ Setting up environment file...")
    
    env_example = ".env.example"
    env_file = ".env"
    
    if os.path.exists(env_example):
        if not os.path.exists(env_file):
            shutil.copy(env_example, env_file)
            print(f"✅ Created {env_file} from template")
            print(f"📝 Please edit {env_file} with your credentials")
        else:
            print(f"ℹ️ {env_file} already exists")
        return True
    else:
        print(f"⚠️ Template file {env_example} not found")
        # Create basic .env file
        with open(env_file, 'w') as f:
            f.write("""# Broker API Credentials
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
ZERODHA_ACCESS_TOKEN=your_access_token_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_RECIPIENT=recipient@gmail.com

# Environment Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
""")
        print(f"✅ Created basic {env_file}")
        return True

def check_config_file():
    """Check if configuration file exists"""
    print("\n📋 Checking configuration file...")
    
    config_file = "config/config.yaml"
    
    if os.path.exists(config_file):
        print(f"✅ Configuration file found: {config_file}")
        return True
    else:
        print(f"⚠️ Configuration file not found: {config_file}")
        print("The system will use default configuration")
        return True

def run_system_test():
    """Run basic system test"""
    print("\n🧪 Running system test...")
    
    try:
        # Import and run the test
        import test_system
        success = test_system.run_comprehensive_test()
        return success
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for user"""
    print("\n🚀 Installation Complete!")
    print("=" * 40)
    print("\n📝 Next Steps:")
    print("1. Edit .env file with your broker credentials")
    print("2. Configure config/config.yaml if needed")
    print("3. Test the system:")
    print("   python src/main.py test")
    print("4. Run paper trading:")
    print("   python src/main.py run --paper")
    print("5. Run backtest:")
    print("   python src/main.py backtest")
    
    print("\n📚 Documentation:")
    print("- Read README.md for detailed instructions")
    print("- Check logs/ directory for system logs")
    print("- Use --help flag for command options")
    
    print("\n⚠️ Important Notes:")
    print("- Start with paper trading to test the system")
    print("- Only use real trading after thorough testing")
    print("- Monitor logs for any issues")
    print("- Ensure you understand the risks involved")

def main():
    """Main installation function"""
    print("🎯 9:15 Strategy Trading System Installation")
    print("=" * 50)
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Create Directories", create_directories),
        ("Install Dependencies", install_dependencies),
        ("Setup Environment File", setup_environment_file),
        ("Check Configuration", check_config_file),
        ("Run System Test", run_system_test)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        
        if not step_func():
            print(f"\n❌ Installation failed at: {step_name}")
            print("Please check the error messages above and try again.")
            sys.exit(1)
    
    print_next_steps()
    print("\n✅ Installation completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed with error: {e}")
        sys.exit(1)