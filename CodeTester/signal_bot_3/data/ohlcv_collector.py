import ccxt
import pandas as pd
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
from signal_bot_3.core.logger import logger
from signal_bot_3.data.persistence import MarketDatabase
import os

class OHLCVCollector:
    def __init__(self, exchange_name: str = 'binance'):
        self.exchange_name = exchange_name
        self.exchange = self._init_exchange(exchange_name)
        self.db = MarketDatabase()
    
    def _init_exchange(self, name: str):
        """Initialize exchange connection"""
        exchange_class = getattr(ccxt, name)
        
        api_key = os.getenv(f"{name.upper()}_API_KEY")
        api_secret = os.getenv(f"{name.upper()}_API_SECRET")
        
        config = {
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        }
        
        if api_key and api_secret:
            config['apiKey'] = api_key
            config['secret'] = api_secret
        
        exchange = exchange_class(config)
        logger.info(f"Initialized {name} exchange")
        return exchange
    
    async def fetch_ohlcv(
        self, 
        symbol: str, 
        timeframe: str = '1h', 
        limit: int = 500,
        since: Optional[int] = None
    ) -> pd.DataFrame:
        """Fetch OHLCV data from exchange"""
        try:
            logger.info(f"Fetching {timeframe} OHLCV for {symbol} from {self.exchange_name}")
            
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv,
                symbol,
                timeframe,
                since=since,
                limit=limit
            )
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = df['timestamp'].astype(int) // 1000
            
            self.db.insert_ohlcv(self.exchange_name, symbol, timeframe, df)
            
            logger.info(f"Fetched {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_multiple_timeframes(
        self, 
        symbol: str, 
        timeframes: List[str]
    ) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple timeframes"""
        tasks = [
            self.fetch_ohlcv(symbol, tf)
            for tf in timeframes
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            tf: result if isinstance(result, pd.DataFrame) else pd.DataFrame()
            for tf, result in zip(timeframes, results)
        }
    
    def get_cached_data(
        self, 
        symbol: str, 
        timeframe: str, 
        limit: int = 500
    ) -> pd.DataFrame:
        """Get cached OHLCV data from database"""
        return self.db.get_ohlcv(self.exchange_name, symbol, timeframe, limit)
