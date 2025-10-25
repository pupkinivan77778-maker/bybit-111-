import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from signal_bot_3.core.bot_controller import BotController
from signal_bot_3.core.logger import logger

load_dotenv()

async def main():
    """Main entry point"""
    logger.info("="*50)
    logger.info("Signal Bot 3.0 - Starting...")
    logger.info("="*50)
    
    controller = BotController()
    
    try:
        await controller.start()
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    except Exception as e:
        logger.error(f"Critical error: {e}")
    finally:
        await controller.stop()
        logger.info("Signal Bot 3.0 - Stopped")

if __name__ == "__main__":
    asyncio.run(main())
