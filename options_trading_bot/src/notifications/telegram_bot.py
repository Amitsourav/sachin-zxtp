"""
Telegram Bot for Trading Notifications and Control
Simple commands for non-technical users
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from datetime import datetime
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

class TradingTelegramBot:
    """Telegram bot for trading notifications and control"""
    
    def __init__(self, token: str, chat_id: str, trading_system=None):
        self.token = token
        self.authorized_chat_id = chat_id
        self.trading_system = trading_system  # Will connect to actual trading engine
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        
        # Security check
        if str(chat_id) != self.authorized_chat_id:
            await update.message.reply_text("⛔ Unauthorized access!")
            return
        
        welcome_message = """
🤖 *9:15 Trading Bot Active!*

I'll help you manage your automated trading with simple commands.

*Available Commands:*
/status - Check current status
/start_trading - Begin automated trading
/stop_trading - Stop all trading
/pause - Pause temporarily
/positions - View open positions
/pnl - Today's profit/loss
/settings - View current settings
/help - Get help

*Quick Actions:*
Just tap the buttons below for easy control!
        """
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("▶️ Start Trading", callback_data='start_trading'),
                InlineKeyboardButton("⏹️ Stop Trading", callback_data='stop_trading')
            ],
            [
                InlineKeyboardButton("📊 Status", callback_data='status'),
                InlineKeyboardButton("💰 P&L", callback_data='pnl')
            ],
            [
                InlineKeyboardButton("📈 Positions", callback_data='positions'),
                InlineKeyboardButton("⚙️ Settings", callback_data='settings')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self._is_authorized(update):
            return
        
        # Get status from trading system (mock for now)
        status_text = """
📊 *System Status*
━━━━━━━━━━━━━━━━
🟢 Bot Status: *RUNNING*
💼 Capital: ₹1,00,000
💰 Current Value: ₹1,02,450
📈 Today's P&L: +₹2,450 (+2.45%)
📊 Open Positions: 1
⏰ Last Update: 11:15 AM

*Market Status:*
NSE: Open ✅
Current Time: 11:15 AM
Trading Hours: 9:15 AM - 3:30 PM
        """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def start_trading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start_trading command"""
        if not self._is_authorized(update):
            return
        
        # Confirmation keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm Start", callback_data='confirm_start'),
                InlineKeyboardButton("❌ Cancel", callback_data='cancel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ *Confirm Action*\n\nStart automated trading with current settings?\n\n"
            "Risk Level: Medium\n"
            "Mode: Paper Trading\n"
            "Max Daily Loss: 2%",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def stop_trading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop_trading command"""
        if not self._is_authorized(update):
            return
        
        keyboard = [
            [
                InlineKeyboardButton("🛑 Stop Now", callback_data='confirm_stop'),
                InlineKeyboardButton("❌ Cancel", callback_data='cancel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ *Confirm Stop*\n\nStop all trading and close positions?",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def positions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /positions command"""
        if not self._is_authorized(update):
            return
        
        positions_text = """
📈 *Open Positions*
━━━━━━━━━━━━━━━━

*RELIANCE 2800 CE*
Entry: ₹45.50
Current: ₹49.20
Quantity: 250
P&L: +₹925 (+8.13%)
        """
        
        await update.message.reply_text(positions_text, parse_mode='Markdown')
    
    async def pnl_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pnl command"""
        if not self._is_authorized(update):
            return
        
        pnl_text = """
💰 *Today's Performance*
━━━━━━━━━━━━━━━━━━

Realized P&L: +₹1,525
Unrealized P&L: +₹925
*Total P&L: +₹2,450*

Win Rate: 66.7% (2/3)
Best Trade: +₹1,200
Worst Trade: -₹450

📊 *Weekly Summary*
Mon: +₹2,100
Tue: -₹850
Wed: +₹1,750
Thu: +₹3,200
*Fri: +₹2,450*

Week Total: *+₹8,650*
        """
        
        await update.message.reply_text(pnl_text, parse_mode='Markdown')
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        if not self._is_authorized(update):
            return
        
        settings_text = """
⚙️ *Current Settings*
━━━━━━━━━━━━━━━━━

📊 *Strategy Settings:*
• PCR Range: 0.7 - 1.5
• Profit Target: 8%
• Stop Loss: 30%
• Execution Time: 9:15 AM

⚠️ *Risk Settings:*
• Risk Level: Medium
• Max Daily Loss: 2%
• Max Trades/Day: 2
• Position Size: 5%

🔔 *Notifications:*
• Telegram: ✅ Enabled
• Email: ❌ Disabled
• Trade Alerts: ✅
• Daily Summary: ✅

💼 *Trading Mode:*
• Paper Trading: ✅
• Live Trading: ❌
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Change Risk Level", callback_data='change_risk'),
                InlineKeyboardButton("📝 Edit Settings", callback_data='edit_settings')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 *Help Guide*
━━━━━━━━━━━━━

*Basic Commands:*
• /start - Initialize bot
• /status - System status
• /pnl - Profit & loss
• /positions - Open trades

*Control Commands:*
• /start_trading - Begin trading
• /stop_trading - Stop all trades
• /pause - Pause temporarily

*Settings:*
• /settings - View settings
• /risk low/medium/high - Set risk

*Information:*
• /help - This help message
• /about - About the bot

*Quick Tips:*
1️⃣ Always check /status before starting
2️⃣ Start with paper trading
3️⃣ Monitor /pnl regularly
4️⃣ Use /stop_trading in emergency

*Need Help?*
Contact: @your_support
Docs: www.yourbot.com/docs
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'start_trading':
            await self._handle_start_trading(query)
        elif query.data == 'stop_trading':
            await self._handle_stop_trading(query)
        elif query.data == 'status':
            await self._handle_status(query)
        elif query.data == 'pnl':
            await self._handle_pnl(query)
        elif query.data == 'positions':
            await self._handle_positions(query)
        elif query.data == 'confirm_start':
            await query.edit_message_text("✅ *Trading Started Successfully!*\n\nBot is now actively trading.", parse_mode='Markdown')
        elif query.data == 'confirm_stop':
            await query.edit_message_text("🛑 *Trading Stopped!*\n\nAll positions closed.", parse_mode='Markdown')
        elif query.data == 'cancel':
            await query.edit_message_text("❌ Action cancelled.")
    
    async def _handle_start_trading(self, query):
        """Handle start trading button"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data='confirm_start'),
                InlineKeyboardButton("❌ Cancel", callback_data='cancel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚠️ Start automated trading?",
            reply_markup=reply_markup
        )
    
    async def _handle_stop_trading(self, query):
        """Handle stop trading button"""
        keyboard = [
            [
                InlineKeyboardButton("🛑 Confirm Stop", callback_data='confirm_stop'),
                InlineKeyboardButton("❌ Cancel", callback_data='cancel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚠️ Stop all trading?",
            reply_markup=reply_markup
        )
    
    async def _handle_status(self, query):
        """Handle status button"""
        status_text = "📊 *Current Status*\n\n🟢 Bot: Running\n💰 Capital: ₹1,00,000\n📈 P&L: +₹2,450"
        await query.edit_message_text(status_text, parse_mode='Markdown')
    
    async def _handle_pnl(self, query):
        """Handle P&L button"""
        pnl_text = "💰 *Today's P&L*\n\n+₹2,450 (+2.45%)\nWin Rate: 66.7%"
        await query.edit_message_text(pnl_text, parse_mode='Markdown')
    
    async def _handle_positions(self, query):
        """Handle positions button"""
        positions_text = "📈 *Positions*\n\nRELIANCE 2800 CE\nP&L: +₹925 (+8.13%)"
        await query.edit_message_text(positions_text, parse_mode='Markdown')
    
    def _is_authorized(self, update: Update) -> bool:
        """Check if user is authorized"""
        chat_id = update.effective_chat.id
        if str(chat_id) != self.authorized_chat_id:
            update.message.reply_text("⛔ Unauthorized access!")
            return False
        return True
    
    # Notification methods (called by trading system)
    
    async def send_trade_alert(self, message: str):
        """Send trade execution alert"""
        formatted_message = f"🔔 *Trade Alert*\n\n{message}"
        await self.application.bot.send_message(
            chat_id=self.authorized_chat_id,
            text=formatted_message,
            parse_mode='Markdown'
        )
    
    async def send_pnl_update(self, pnl: float, percent: float):
        """Send P&L update"""
        emoji = "📈" if pnl >= 0 else "📉"
        sign = "+" if pnl >= 0 else ""
        
        message = f"{emoji} *P&L Update*\n\n{sign}₹{abs(pnl):,.0f} ({sign}{percent:.2f}%)"
        await self.application.bot.send_message(
            chat_id=self.authorized_chat_id,
            text=message,
            parse_mode='Markdown'
        )
    
    async def send_error_alert(self, error_msg: str):
        """Send error alert"""
        message = f"🚨 *ERROR*\n\n{error_msg}\n\nPlease check the system!"
        await self.application.bot.send_message(
            chat_id=self.authorized_chat_id,
            text=message,
            parse_mode='Markdown'
        )
    
    async def send_daily_summary(self, summary: dict):
        """Send daily trading summary"""
        message = f"""
📊 *Daily Summary - {datetime.now().strftime('%d %b %Y')}*
━━━━━━━━━━━━━━━━━━━━━

💰 *Performance:*
• Total P&L: {summary.get('total_pnl', 0):+,.0f}
• Win Rate: {summary.get('win_rate', 0):.1f}%
• Trades: {summary.get('total_trades', 0)}

📈 *Best Trade:* +₹{summary.get('best_trade', 0):,.0f}
📉 *Worst Trade:* -₹{abs(summary.get('worst_trade', 0)):,.0f}

💼 *Account:*
• Starting: ₹{summary.get('start_capital', 0):,.0f}
• Ending: ₹{summary.get('end_capital', 0):,.0f}
• Change: {summary.get('change_percent', 0):+.2f}%

Have a great evening! 🌙
        """
        
        await self.application.bot.send_message(
            chat_id=self.authorized_chat_id,
            text=message,
            parse_mode='Markdown'
        )
    
    async def run(self):
        """Run the telegram bot"""
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("start_trading", self.start_trading_command))
        self.application.add_handler(CommandHandler("stop_trading", self.stop_trading_command))
        self.application.add_handler(CommandHandler("positions", self.positions_command))
        self.application.add_handler(CommandHandler("pnl", self.pnl_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Add button handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Start bot
        await self.application.run_polling()


# Alias for backward compatibility
TelegramNotifier = TradingTelegramBot


# Example usage
if __name__ == "__main__":
    # Test bot (replace with your credentials)
    bot = TradingTelegramBot(
        token="YOUR_BOT_TOKEN",
        chat_id="YOUR_CHAT_ID"
    )
    
    # Run bot
    asyncio.run(bot.run())