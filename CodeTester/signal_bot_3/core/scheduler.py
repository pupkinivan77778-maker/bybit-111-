import asyncio
from datetime import datetime
from signal_bot_3.core.logger import logger

class Scheduler:
    def __init__(self):
        self.tasks = []
        self.running = False
    
    def add_task(self, coro, interval: int):
        """Add periodic task"""
        self.tasks.append({'coro': coro, 'interval': interval})
        logger.info(f"Task scheduled with interval {interval}s")
    
    async def run(self):
        """Run scheduler"""
        self.running = True
        logger.info("Scheduler started")
        
        while self.running:
            for task in self.tasks:
                asyncio.create_task(task['coro']())
                await asyncio.sleep(task['interval'])
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
        logger.info("Scheduler stopped")
