"""
Notification system for Telegram and Email alerts
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages notifications via Telegram and Email"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.telegram_config = config.get('notifications', {}).get('telegram', {})
        self.email_config = config.get('notifications', {}).get('email', {})
        
        self.telegram_enabled = self.telegram_config.get('enabled', False)
        self.email_enabled = self.email_config.get('enabled', False)
        
    def send_message(self, message: str, urgent: bool = False):
        """Send notification via enabled channels"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        logger.info(f"Sending notification: {message}")
        
        if self.telegram_enabled:
            self._send_telegram(formatted_message, urgent)
        
        if self.email_enabled:
            self._send_email(formatted_message, urgent)
    
    def _send_telegram(self, message: str, urgent: bool = False):
        """Send message via Telegram bot"""
        try:
            bot_token = self.telegram_config.get('bot_token')
            chat_id = self.telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                logger.warning("Telegram credentials not configured")
                return False
            
            # Add urgency indicator
            if urgent:
                message = f"🚨 URGENT 🚨\n{message}"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def _send_email(self, message: str, urgent: bool = False):
        """Send message via email"""
        try:
            smtp_server = self.email_config.get('smtp_server')
            smtp_port = self.email_config.get('smtp_port', 587)
            email = self.email_config.get('email')
            password = self.email_config.get('password')
            recipient = self.email_config.get('recipient')
            
            if not all([smtp_server, email, password, recipient]):
                logger.warning("Email credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = recipient
            
            if urgent:
                msg['Subject'] = "🚨 URGENT - 9:15 Strategy Alert"
            else:
                msg['Subject'] = "9:15 Strategy Notification"
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email, password)
            text = msg.as_string()
            server.sendmail(email, recipient, text)
            server.quit()
            
            logger.info("Email sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_daily_summary(self, summary_data: Dict):
        """Send daily trading summary"""
        try:
            message = self._format_daily_summary(summary_data)
            self.send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {e}")
    
    def _format_daily_summary(self, data: Dict) -> str:
        """Format daily summary message"""
        summary = "📊 Daily Trading Summary\n"
        summary += "=" * 25 + "\n\n"
        
        if data.get('trade_executed'):
            summary += f"✅ Trade Executed: {data.get('symbol', 'N/A')}\n"
            summary += f"📈 Entry Price: ₹{data.get('entry_price', 0):.2f}\n"
            summary += f"📊 Exit Price: ₹{data.get('exit_price', 0):.2f}\n"
            summary += f"💰 PnL: ₹{data.get('pnl', 0):.2f} ({data.get('pnl_percent', 0):.2f}%)\n"
            summary += f"⏱️ Duration: {data.get('duration', 'N/A')}\n"
        else:
            summary += "❌ No trades executed today\n"
            reason = data.get('no_trade_reason', 'No suitable opportunity found')
            summary += f"Reason: {reason}\n"
        
        summary += f"\n📊 Market Info:\n"
        summary += f"VIX: {data.get('vix', 'N/A')}\n"
        summary += f"Top Gainer: {data.get('top_gainer', 'N/A')}\n"
        
        return summary
    
    def send_error_alert(self, error_message: str, error_type: str = "General"):
        """Send error alert"""
        message = f"❌ Error Alert - {error_type}\n\n{error_message}"
        self.send_message(message, urgent=True)
    
    def test_notifications(self) -> Dict:
        """Test all notification channels"""
        results = {}
        
        test_message = "🧪 Test notification from 9:15 Strategy system"
        
        if self.telegram_enabled:
            results['telegram'] = self._send_telegram(test_message)
        
        if self.email_enabled:
            results['email'] = self._send_email(test_message)
        
        return results

class TelegramBot:
    """Dedicated Telegram bot for more advanced features"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send text message"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
    
    def send_photo(self, photo_path: str, caption: str = "") -> bool:
        """Send photo with caption"""
        try:
            url = f"{self.base_url}/sendPhoto"
            
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Telegram photo send error: {e}")
            return False
    
    def send_document(self, document_path: str, caption: str = "") -> bool:
        """Send document with caption"""
        try:
            url = f"{self.base_url}/sendDocument"
            
            with open(document_path, 'rb') as document:
                files = {'document': document}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Telegram document send error: {e}")
            return False