#!/usr/bin/env python3
"""
EASY COMMAND RUNNER - Run from anywhere!
This script automatically finds and runs the correct commands
"""

import os
import sys
import subprocess

def find_project_root():
    """Find the options_trading_bot directory"""
    # Check current directory
    if os.path.exists('ULTIMATE_915.py'):
        return os.getcwd()
    
    # Check if we're in parent directory
    if os.path.exists('options_trading_bot/ULTIMATE_915.py'):
        return os.path.join(os.getcwd(), 'options_trading_bot')
    
    # Check if we're in sachin-zxtp
    if os.path.exists('sachin-zxtp/options_trading_bot/ULTIMATE_915.py'):
        return os.path.join(os.getcwd(), 'sachin-zxtp/options_trading_bot')
    
    # Check common paths
    home = os.path.expanduser("~")
    common_paths = [
        f"{home}/sachin-zxtp/options_trading_bot",
        f"{home}/Documents/sachin-zxtp/options_trading_bot",
        f"{home}/Desktop/sachin-zxtp/options_trading_bot",
        f"{home}/Downloads/sachin-zxtp/options_trading_bot",
    ]
    
    for path in common_paths:
        if os.path.exists(f"{path}/ULTIMATE_915.py"):
            return path
    
    return None

def main():
    print("🔍 SMART COMMAND RUNNER")
    print("=" * 50)
    
    # Find project directory
    project_dir = find_project_root()
    
    if not project_dir:
        print("❌ Cannot find options_trading_bot folder!")
        print("\nPlease run from inside the cloned repository:")
        print("  cd sachin-zxtp")
        print("  python3 RUN_COMMANDS.py")
        sys.exit(1)
    
    print(f"✅ Found project at: {project_dir}")
    os.chdir(project_dir)
    
    # Show menu
    print("\n📋 AVAILABLE COMMANDS:")
    print("-" * 50)
    print("1. Get Access Token")
    print("2. Run ULTIMATE 9:15 Strategy")
    print("3. Paper Trading")
    print("4. Validate Before 9:15")
    print("5. Web Dashboard")
    print("6. Test Symbols")
    print("7. Check Configuration")
    print("0. Exit")
    
    while True:
        choice = input("\nEnter choice (0-7): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            print("\n🔑 Getting Access Token...")
            subprocess.run([sys.executable, "get_access_token.py"])
        elif choice == '2':
            print("\n🚀 Running ULTIMATE 9:15...")
            subprocess.run([sys.executable, "ULTIMATE_915.py"])
        elif choice == '3':
            print("\n📝 Running Paper Trading...")
            subprocess.run([sys.executable, "FINAL_paper_trade_zerodha.py"])
        elif choice == '4':
            print("\n✅ Validating...")
            subprocess.run([sys.executable, "VALIDATE_before_915.py"])
        elif choice == '5':
            print("\n🌐 Starting Web Dashboard...")
            web_dir = os.path.join(project_dir, "web_interface")
            os.chdir(web_dir)
            subprocess.run([sys.executable, "app.py"])
            os.chdir(project_dir)
        elif choice == '6':
            print("\n🧪 Testing Symbols...")
            subprocess.run([sys.executable, "test_symbols.py"])
        elif choice == '7':
            print("\n⚙️ Checking Configuration...")
            config_path = os.path.join(project_dir, "config/config.yaml")
            if os.path.exists(config_path):
                print("✅ config.yaml exists")
                with open(config_path, 'r') as f:
                    lines = f.readlines()[:10]
                    print("\nFirst 10 lines of config:")
                    for line in lines:
                        if 'access_token' not in line and 'secret' not in line:
                            print(f"  {line.rstrip()}")
            else:
                print("❌ config.yaml not found!")
                print("Creating from example...")
                example = os.path.join(project_dir, "config/config.example.yaml")
                if os.path.exists(example):
                    import shutil
                    shutil.copy(example, config_path)
                    print("✅ Created config.yaml - Please add your API keys!")
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()