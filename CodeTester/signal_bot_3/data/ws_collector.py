import asyncio
import websockets
import json
from typing import Callable, Optional
from signal_bot_3.core.logger import logger
import ccxt

class WebSocketCollector:
    def __init__(self, exchange_name: str = 'binance'):
        self.exchange_name = exchange_name
        self.ws_url = self._get_ws_url(exchange_name)
        self.ws = None
        self.running = False
        self.reconnect_delay = 5
        self.max_reconnect_attempts = 10
    
    def _get_ws_url(self, exchange: str) -> str:
        """Get WebSocket URL for exchange"""
        urls = {
            'binance': 'wss://stream.binance.com:9443/ws',
            'bybit': 'wss://stream.bybit.com/v5/public/linear'
        }
        return urls.get(exchange, urls['binance'])
    
    async def connect(self):
        """Connect to WebSocket"""
        try:
            self.ws = await websockets.connect(self.ws_url)
            self.running = True
            logger.info(f"WebSocket connected to {self.exchange_name}")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            raise
    
    async def subscribe_trades(self, symbol: str, callback: Callable):
        """Subscribe to trade stream"""
        if not self.ws:
            await self.connect()
        
        symbol_lower = symbol.lower().replace('/', '')
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol_lower}@trade"],
            "id": 1
        }
        
        await self.ws.send(json.dumps(subscribe_message))
        logger.info(f"Subscribed to trades for {symbol}")
        
        await self._listen(callback)
    
    async def subscribe_kline(self, symbol: str, interval: str, callback: Callable):
        """Subscribe to kline/candlestick stream"""
        if not self.ws:
            await self.connect()
        
        symbol_lower = symbol.lower().replace('/', '')
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol_lower}@kline_{interval}"],
            "id": 1
        }
        
        await self.ws.send(json.dumps(subscribe_message))
        logger.info(f"Subscribed to {interval} klines for {symbol}")
        
        await self._listen(callback)
    
    async def _listen(self, callback: Callable):
        """Listen to WebSocket messages"""
        reconnect_count = 0
        
        while self.running and reconnect_count < self.max_reconnect_attempts:
            try:
                async for message in self.ws:
                    data = json.loads(message)
                    
                    if 'e' in data:
                        await callback(data)
                    
                    reconnect_count = 0
                    
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed, attempting reconnect...")
                reconnect_count += 1
                await asyncio.sleep(self.reconnect_delay)
                
                try:
                    await self.connect()
                except Exception as e:
                    logger.error(f"Reconnection failed: {e}")
            
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
        
        if reconnect_count >= self.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")
    
    async def close(self):
        """Close WebSocket connection"""
        self.running = False
        if self.ws:
            await self.ws.close()
            logger.info("WebSocket closed")
