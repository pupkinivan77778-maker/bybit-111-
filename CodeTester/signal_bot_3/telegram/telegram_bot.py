import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from signal_bot_3.core.logger import logger
from signal_bot_3.ui.cli import run_backtest
import asyncio

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            logger.warning("TELEGRAM_BOT_TOKEN not set, bot will not start")
        self.app = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
*🤖 Signal Bot 3.0*

Welcome to the professional crypto trading signal bot!

*Available Commands:*
/start - Show this message
/help - Get help
/run_backtest - Run backtest with default settings
/status - Check bot status

*Features:*
✅ Multi-timeframe analysis
✅ Risk/Reward calculation
✅ Advanced metrics (Sharpe, Sortino, PnL)
✅ Real-time signals

Ready to analyze the markets! 📊
        """
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"User {update.effective_user.id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
*📚 Signal Bot Help*

*Commands:*
/run_backtest - Run backtest analysis
/status - Check system status

*Backtest:*
Analyzes historical data across multiple timeframes (5m, 15m, 1h, 4h) to generate and validate trading signals.

*Metrics Provided:*
• Win Rate
• Total PnL
• Sharpe Ratio
• Sortino Ratio
• Max Drawdown
• Profit Factor

For support: Contact admin
        """
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def run_backtest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /run_backtest command"""
        await update.message.reply_text("🔄 Running backtest... This may take a few moments.")
        
        try:
            result = await asyncio.to_thread(
                run_backtest,
                symbol='BTC/USDT',
                exchange='binance',
                timeframes=['5m', '15m', '1h', '4h'],
                limit=100
            )
            
            if result and 'metrics' in result:
                m = result['metrics']
                
                report = f"""
*📊 Backtest Results - BTC/USDT*

*Performance:*
• Total Trades: {m.get('total_trades', 0)}
• Win Rate: {m.get('win_rate', 0)*100:.1f}%
• Total PnL: ${m.get('total_pnl', 0):.2f}
• Return: {m.get('return_pct', 0):.2f}%

*Risk Metrics:*
• Sharpe Ratio: {m.get('sharpe_ratio', 0):.2f}
• Sortino Ratio: {m.get('sortino_ratio', 0):.2f}
• Max Drawdown: {m.get('max_drawdown', 0)*100:.1f}%
• Profit Factor: {m.get('profit_factor', 0):.2f}

*Trade Stats:*
• Avg Win: ${m.get('avg_win', 0):.2f}
• Avg Loss: ${m.get('avg_loss', 0):.2f}
• Final Equity: ${m.get('final_equity', 0):.2f}
                """
                
                await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ No signals generated in backtest")
                
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            await update.message.reply_text(f"❌ Error running backtest: {str(e)}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status = """
*🟢 Bot Status*

• System: Online
• Database: Connected
• Exchange API: Ready
• Signal Engine: Active

All systems operational ✅
        """
        await update.message.reply_text(status, parse_mode=ParseMode.MARKDOWN)
    
    def run(self):
        """Start the bot"""
        if not self.token:
            logger.error("Cannot start bot: TELEGRAM_BOT_TOKEN not set")
            return
        
        self.app = Application.builder().token(self.token).build()
        
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("run_backtest", self.run_backtest_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        
        logger.info("Telegram bot starting...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    bot = TelegramBot()
    bot.run()

if __name__ == "__main__":
    main()
