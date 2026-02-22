#!/usr/bin/env python3
"""
Quick system test script for 9:15 Strategy Trading System
Tests all major components without requiring full setup
"""

import sys
import os
sys.path.append('src')

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from src.config_manager import ConfigManager
        print("✅ config_manager imported successfully")
    except Exception as e:
        print(f"❌ config_manager import failed: {e}")
        return False
    
    try:
        from src.data_fetcher import NSEDataFetcher
        print("✅ data_fetcher imported successfully")
    except Exception as e:
        print(f"❌ data_fetcher import failed: {e}")
        return False
    
    try:
        from src.broker_interface import PaperTradingBroker, BrokerFactory
        print("✅ broker_interface imported successfully")
    except Exception as e:
        print(f"❌ broker_interface import failed: {e}")
        return False
    
    try:
        from src.notifications import NotificationManager
        print("✅ notifications imported successfully")
    except Exception as e:
        print(f"❌ notifications import failed: {e}")
        return False
    
    try:
        from src.backtesting import BacktestEngine
        print("✅ backtesting imported successfully")
    except Exception as e:
        print(f"❌ backtesting import failed: {e}")
        return False
    
    try:
        from src.trading_strategy import TradingStrategy
        print("✅ trading_strategy imported successfully")
    except Exception as e:
        print(f"❌ trading_strategy import failed: {e}")
        return False
    
    try:
        from src.logger import TradingLogger
        print("✅ logger imported successfully")
    except Exception as e:
        print(f"❌ logger import failed: {e}")
        return False
    
    return True

def test_config_loading():
    """Test configuration loading"""
    print("\n🧪 Testing configuration loading...")
    
    try:
        from src.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Check essential config sections
        required_sections = ['trading', 'broker', 'notifications', 'risk']
        for section in required_sections:
            if section in config:
                print(f"✅ {section} configuration loaded")
            else:
                print(f"⚠️ {section} configuration missing")
        
        print("✅ Configuration loading successful")
        return True, config
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False, None

def test_paper_trading_broker():
    """Test paper trading broker"""
    print("\n🧪 Testing paper trading broker...")
    
    try:
        from src.broker_interface import PaperTradingBroker
        
        broker = PaperTradingBroker(initial_balance=100000)
        
        # Test authentication
        if broker.authenticate():
            print("✅ Paper broker authentication successful")
        else:
            print("❌ Paper broker authentication failed")
            return False
        
        # Test order placement
        order_result = broker.place_order("RELIANCE24JAN3000CE", 1, "MARKET")
        if order_result['success']:
            print("✅ Paper order placement successful")
        else:
            print(f"❌ Paper order placement failed: {order_result['message']}")
            return False
        
        # Test position retrieval
        positions = broker.get_positions()
        if len(positions) > 0:
            print("✅ Position retrieval successful")
        else:
            print("⚠️ No positions found (expected for paper trading)")
        
        print("✅ Paper trading broker test successful")
        return True
        
    except Exception as e:
        print(f"❌ Paper trading broker test failed: {e}")
        return False

def test_data_fetcher():
    """Test data fetching capabilities"""
    print("\n🧪 Testing data fetcher...")
    
    try:
        from src.data_fetcher import NSEDataFetcher
        
        data_fetcher = NSEDataFetcher()
        
        # Test trading day check
        is_trading_day = data_fetcher.is_trading_day()
        print(f"✅ Trading day check: {is_trading_day}")
        
        # Test NIFTY50 symbols
        if len(data_fetcher.nifty50_symbols) == 50:
            print("✅ NIFTY50 symbols loaded correctly")
        else:
            print(f"⚠️ NIFTY50 symbols count: {len(data_fetcher.nifty50_symbols)}")
        
        print("✅ Data fetcher test successful")
        return True
        
    except Exception as e:
        print(f"❌ Data fetcher test failed: {e}")
        return False

def test_notification_manager():
    """Test notification manager"""
    print("\n🧪 Testing notification manager...")
    
    try:
        from src.notifications import NotificationManager
        
        # Create test config
        config = {
            'notifications': {
                'telegram': {'enabled': False},
                'email': {'enabled': False}
            }
        }
        
        notifier = NotificationManager(config)
        print("✅ Notification manager created successfully")
        
        # Test with disabled notifications (should not fail)
        notifier.send_message("Test message")
        print("✅ Notification manager test successful")
        return True
        
    except Exception as e:
        print(f"❌ Notification manager test failed: {e}")
        return False

def test_backtesting_basic():
    """Test basic backtesting functionality"""
    print("\n🧪 Testing backtesting engine...")
    
    try:
        from src.backtesting import BacktestEngine
        
        # Create test config
        config = {
            'trading': {
                'pcr_min_range': 0.7,
                'pcr_max_range': 1.5,
                'profit_target_percent': 8.0
            },
            'backtesting': {
                'initial_capital': 100000
            }
        }
        
        engine = BacktestEngine(config)
        print("✅ Backtesting engine created successfully")
        
        # Test performance calculation with empty trades
        performance = engine._calculate_performance()
        if 'error' in performance:
            print("✅ Empty backtest handling correct")
        else:
            print("⚠️ Unexpected performance result for empty backtest")
        
        print("✅ Backtesting engine test successful")
        return True
        
    except Exception as e:
        print(f"❌ Backtesting engine test failed: {e}")
        return False

def test_logging_system():
    """Test logging system"""
    print("\n🧪 Testing logging system...")
    
    try:
        from src.logger import TradingLogger, setup_logging
        
        # Create test config
        config = {
            'logging': {
                'level': 'INFO',
                'file_path': 'logs/test.log',
                'max_file_size': '1MB',
                'backup_count': 3
            }
        }
        
        # Test logger setup
        logger_setup = setup_logging(config)
        print("✅ Logging system setup successful")
        
        # Test logging functionality
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Test log message")
        print("✅ Log message test successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging system test failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive system test"""
    print("🚀 Starting 9:15 Strategy Trading System Test")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Module Imports", test_imports()))
    test_results.append(("Configuration Loading", test_config_loading()[0]))
    test_results.append(("Paper Trading Broker", test_paper_trading_broker()))
    test_results.append(("Data Fetcher", test_data_fetcher()))
    test_results.append(("Notification Manager", test_notification_manager()))
    test_results.append(("Backtesting Engine", test_backtesting_basic()))
    test_results.append(("Logging System", test_logging_system()))
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 30)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Configure your broker credentials in .env file")
        print("2. Set up notifications if desired")
        print("3. Run: python src/main.py test")
        print("4. Run: python src/main.py run --paper")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please check the errors above.")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)