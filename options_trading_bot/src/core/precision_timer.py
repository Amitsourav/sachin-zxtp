"""
High-precision timing system for exact 09:15:00 execution
Ensures trades execute with minimal delay (target: <500ms)
"""

import asyncio
import time
import ntplib
from datetime import datetime, time as dt_time, timedelta
from typing import Optional, Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PrecisionTimer:
    """High-precision timer for exact time execution with NTP sync"""
    
    def __init__(self):
        self.ntp_offset = 0.0
        self.last_sync_time = None
        self.sync_interval = 3600  # Re-sync every hour
        
    async def sync_with_ntp(self, server: str = "time.google.com") -> float:
        """
        Sync system clock with NTP server for accurate time
        Returns offset in seconds (positive = system ahead)
        """
        try:
            client = ntplib.NTPClient()
            response = client.request(server, version=3, timeout=5)
            self.ntp_offset = response.offset
            self.last_sync_time = datetime.now()
            
            logger.info(f"NTP sync successful. Offset: {self.ntp_offset:.3f}s")
            
            # Warn if offset is significant
            if abs(self.ntp_offset) > 1.0:
                logger.warning(f"System clock offset is {self.ntp_offset:.3f}s - consider syncing system time")
                
            return self.ntp_offset
            
        except Exception as e:
            logger.error(f"NTP sync failed: {e}. Using system time.")
            self.ntp_offset = 0.0
            return 0.0
    
    def get_accurate_time(self) -> datetime:
        """Get current time adjusted for NTP offset"""
        return datetime.now() - timedelta(seconds=self.ntp_offset)
    
    async def wait_until_precise_time(
        self,
        target_hour: int,
        target_minute: int,
        target_second: int = 0,
        target_microsecond: int = 0
    ) -> datetime:
        """
        Wait until exact target time with microsecond precision
        Returns actual execution time for logging
        """
        # Create target datetime for today
        now = self.get_accurate_time()
        target = datetime.combine(
            now.date(),
            dt_time(target_hour, target_minute, target_second, target_microsecond)
        )
        
        # If target already passed today, set for tomorrow
        if target <= now:
            target += timedelta(days=1)
            
        logger.info(f"Waiting for precise time: {target.strftime('%H:%M:%S.%f')[:-3]}")
        
        # Phase 1: Sleep until 10 seconds before target with countdown
        last_shown_minute = -1
        while True:
            now = self.get_accurate_time()
            remaining = (target - now).total_seconds()
            
            # Show countdown every minute for better user experience
            minutes_left = int(remaining // 60)
            if minutes_left != last_shown_minute and remaining > 60:
                hours = minutes_left // 60
                mins = minutes_left % 60
                if hours > 0:
                    print(f"⏰ Trading in: {hours}h {mins}m ({target.strftime('%H:%M:%S')})")
                else:
                    print(f"⏰ Trading in: {mins}m {int(remaining % 60)}s ({target.strftime('%H:%M:%S')})")
                last_shown_minute = minutes_left
            
            if remaining <= 10:
                print(f"🚀 Final countdown: {remaining:.1f}s until {target.strftime('%H:%M:%S')}")
                break
            elif remaining > 3600:
                # If more than an hour away, sleep longer and re-sync NTP
                await asyncio.sleep(1800)  # Sleep 30 minutes
                await self.sync_with_ntp()
            elif remaining > 60:
                await asyncio.sleep(30)  # Sleep 30 seconds
            else:
                await asyncio.sleep(5)  # Sleep 5 seconds
        
        # Phase 2: Medium precision (10s to 1s before)
        while True:
            now = self.get_accurate_time()
            remaining = (target - now).total_seconds()
            
            if remaining <= 1.0:
                break
            await asyncio.sleep(0.1)  # Check every 100ms
        
        # Phase 3: High precision (last 1 second)
        while True:
            now = self.get_accurate_time()
            remaining = (target - now).total_seconds()
            
            if remaining <= 0.1:
                break
            await asyncio.sleep(0.01)  # Check every 10ms
        
        # Phase 4: Ultra-high precision (last 100ms)
        while True:
            now = self.get_accurate_time()
            if now >= target:
                break
            await asyncio.sleep(0.001)  # Check every 1ms
        
        # Return actual execution time
        actual_time = self.get_accurate_time()
        delay_ms = (actual_time - target).total_seconds() * 1000
        
        if delay_ms < 50:
            logger.info(f"✅ Executed at {actual_time.strftime('%H:%M:%S.%f')[:-3]} (delay: {delay_ms:.1f}ms)")
        elif delay_ms < 500:
            logger.warning(f"⚠️ Executed at {actual_time.strftime('%H:%M:%S.%f')[:-3]} (delay: {delay_ms:.1f}ms)")
        else:
            logger.error(f"❌ Executed at {actual_time.strftime('%H:%M:%S.%f')[:-3]} (delay: {delay_ms:.1f}ms)")
            
        return actual_time


class Strategy915Timer:
    """Specialized timer for 9:15 strategy execution"""
    
    def __init__(self):
        self.timer = PrecisionTimer()
        self.pre_market_scan_time = dt_time(9, 14, 0)  # Start scanning at 9:14
        self.prepare_time = dt_time(9, 14, 50)  # Prepare orders at 9:14:50
        self.execute_time = dt_time(9, 15, 0)  # Execute at exactly 9:15:00
        
        self.pre_calculated_data = {}
        self.order_prepared = False
        
    async def initialize(self):
        """Initialize timer and sync with NTP"""
        await self.timer.sync_with_ntp()
        logger.info("Strategy timer initialized with NTP sync")
        
    async def pre_market_scan(self, scan_callback: Callable) -> Dict[str, Any]:
        """
        Execute pre-market scanning at 9:14:00
        This gives us 1 minute to analyze and prepare
        """
        logger.info("Starting pre-market scan phase...")
        
        # Run the scan callback
        scan_result = await scan_callback()
        
        # Store results for later use
        self.pre_calculated_data = {
            'scan_time': self.timer.get_accurate_time(),
            'scan_result': scan_result,
            'selected_symbol': scan_result.get('top_gainer'),
            'pcr': scan_result.get('pcr'),
            'entry_price': scan_result.get('entry_price')
        }
        
        logger.info(f"Pre-market scan complete. Selected: {self.pre_calculated_data['selected_symbol']}")
        return self.pre_calculated_data
        
    async def prepare_order(self, prepare_callback: Callable) -> Dict[str, Any]:
        """
        Prepare order parameters at 9:14:50
        Everything calculated and ready, just waiting for trigger
        """
        logger.info("Preparing order for immediate execution...")
        
        # Use pre-calculated data to prepare order
        order_params = await prepare_callback(self.pre_calculated_data)
        
        self.pre_calculated_data['order_params'] = order_params
        self.order_prepared = True
        
        logger.info("Order prepared and ready for instant execution")
        return order_params
        
    async def execute_at_9_15(self, execute_callback: Callable) -> Dict[str, Any]:
        """
        Execute trade at EXACTLY 9:15:00 with minimal delay
        All calculations done beforehand, this just fires the order
        """
        if not self.order_prepared:
            raise RuntimeError("Order not prepared! Call prepare_order first")
            
        logger.info("Waiting for 9:15:00 trigger...")
        
        # Wait for exact time
        execution_time = await self.timer.wait_until_precise_time(9, 15, 0, 0)
        
        # IMMEDIATE EXECUTION - No calculations here!
        start_exec = time.perf_counter()
        result = await execute_callback(self.pre_calculated_data['order_params'])
        exec_duration = (time.perf_counter() - start_exec) * 1000
        
        # Log execution metrics
        result['execution_metrics'] = {
            'target_time': '09:15:00.000',
            'actual_time': execution_time.strftime('%H:%M:%S.%f')[:-3],
            'wait_delay_ms': (execution_time - datetime.combine(execution_time.date(), self.execute_time)).total_seconds() * 1000,
            'exec_duration_ms': exec_duration,
            'total_delay_ms': (execution_time - datetime.combine(execution_time.date(), self.execute_time)).total_seconds() * 1000 + exec_duration
        }
        
        logger.info(f"Order executed in {exec_duration:.1f}ms")
        logger.info(f"Total delay from 9:15:00: {result['execution_metrics']['total_delay_ms']:.1f}ms")
        
        return result
        
    async def run_complete_sequence(
        self,
        scan_callback: Callable,
        prepare_callback: Callable,
        execute_callback: Callable
    ) -> Dict[str, Any]:
        """
        Run the complete 9:15 strategy sequence with precise timing
        
        Timeline:
        - 9:14:00 - Start pre-market scan
        - 9:14:50 - Prepare order with all parameters
        - 9:15:00 - Execute instantly
        """
        # Initialize with NTP sync
        await self.initialize()
        
        # Wait for 9:14:00 and scan
        await self.timer.wait_until_precise_time(9, 14, 0)
        await self.pre_market_scan(scan_callback)
        
        # Wait for 9:14:50 and prepare
        await self.timer.wait_until_precise_time(9, 14, 50)
        await self.prepare_order(prepare_callback)
        
        # Wait for 9:15:00 and execute
        result = await self.execute_at_9_15(execute_callback)
        
        return result


class ExecutionOptimizer:
    """Optimization techniques for faster execution"""
    
    @staticmethod
    def pre_warm_connection(broker_client):
        """
        Pre-warm broker connection to reduce first-call latency
        Call this during initialization
        """
        try:
            # Make a dummy API call to establish connection
            broker_client.get_profile()
            logger.info("Broker connection pre-warmed")
        except Exception as e:
            logger.error(f"Failed to pre-warm connection: {e}")
    
    @staticmethod
    async def parallel_data_fetch(symbols: list, fetch_func: Callable) -> dict:
        """
        Fetch data for multiple symbols in parallel to save time
        """
        tasks = [fetch_func(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for symbol, result in zip(symbols, results):
            if not isinstance(result, Exception):
                data[symbol] = result
            else:
                logger.error(f"Failed to fetch {symbol}: {result}")
                
        return data
    
    @staticmethod
    def pre_calculate_all_params(market_data: dict) -> dict:
        """
        Pre-calculate all trading parameters to minimize execution time
        """
        params = {
            'calculated_at': datetime.now(),
            'orders_ready': {}
        }
        
        # Pre-calculate for each possible scenario
        for symbol, data in market_data.items():
            params['orders_ready'][symbol] = {
                'symbol': symbol,
                'quantity': data['lot_size'],
                'order_type': 'MARKET',
                'product': 'MIS',
                'exchange': 'NFO',
                'transaction_type': 'BUY',
                'validity': 'DAY',
                # All parameters ready to go
                'prepared_at': datetime.now().isoformat()
            }
            
        return params


# Example usage for testing
async def test_precision_timer():
    """Test the precision timer system"""
    timer = Strategy915Timer()
    
    # Mock callbacks
    async def mock_scan():
        await asyncio.sleep(0.1)  # Simulate API call
        return {
            'top_gainer': 'RELIANCE',
            'pcr': 0.85,
            'entry_price': 2800
        }
    
    async def mock_prepare(data):
        await asyncio.sleep(0.05)  # Simulate preparation
        return {
            'symbol': f"{data['selected_symbol']}2800CE",
            'quantity': 250,
            'order_type': 'MARKET'
        }
    
    async def mock_execute(params):
        await asyncio.sleep(0.02)  # Simulate order placement
        return {
            'order_id': '123456',
            'status': 'COMPLETE',
            'executed_price': 45.50
        }
    
    # Test execution at specific time
    # Modify times for testing (use current time + 1 minute)
    now = datetime.now()
    timer.pre_market_scan_time = dt_time(now.hour, now.minute + 1, 0)
    timer.prepare_time = dt_time(now.hour, now.minute + 1, 10)
    timer.execute_time = dt_time(now.hour, now.minute + 1, 20)
    
    result = await timer.run_complete_sequence(
        mock_scan,
        mock_prepare,
        mock_execute
    )
    
    print(f"Execution result: {result}")
    print(f"Execution metrics: {result.get('execution_metrics')}")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_precision_timer())