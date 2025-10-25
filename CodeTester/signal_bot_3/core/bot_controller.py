import asyncio
from signal_bot_3.telegram.telegram_bot import TelegramBot
from signal_bot_3.core.logger import logger

class BotController:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.running = False
    
    async def start(self):
        """Start bot controller"""
        logger.info("Starting Bot Controller...")
        self.running = True
        
        try:
            await asyncio.to_thread(self.telegram_bot.run)
        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
            await self.stop()
        except Exception as e:
            logger.error(f"Bot controller error: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop bot controller"""
        self.running = False
        logger.info("Bot Controller stopped")
