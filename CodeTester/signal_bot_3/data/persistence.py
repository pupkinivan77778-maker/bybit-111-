import sqlite3
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
import os
from signal_bot_3.core.logger import logger

class MarketDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv("DATABASE_PATH", "signal_bot_3/data/market.db")
        
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.initialize()
    
    def initialize(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS ohlcv (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                UNIQUE(exchange, symbol, timeframe, timestamp)
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                entry_price REAL,
                target_price REAL,
                stop_loss REAL,
                confidence REAL,
                status TEXT DEFAULT 'active',
                pnl REAL DEFAULT 0,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_ohlcv_lookup 
            ON ohlcv(exchange, symbol, timeframe, timestamp)
        ''')
        
        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def insert_ohlcv(self, exchange: str, symbol: str, timeframe: str, data: pd.DataFrame):
        """Bulk insert OHLCV data"""
        try:
            records = []
            for idx, row in data.iterrows():
                records.append((
                    exchange, symbol, timeframe,
                    int(row['timestamp']),
                    float(row['open']),
                    float(row['high']),
                    float(row['low']),
                    float(row['close']),
                    float(row['volume'])
                ))
            
            self.conn.executemany('''
                INSERT OR REPLACE INTO ohlcv 
                (exchange, symbol, timeframe, timestamp, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', records)
            
            self.conn.commit()
            logger.debug(f"Inserted {len(records)} OHLCV records for {symbol} on {exchange}")
            
        except Exception as e:
            logger.error(f"Error inserting OHLCV data: {e}")
            self.conn.rollback()
    
    def get_ohlcv(self, exchange: str, symbol: str, timeframe: str, limit: int = 1000) -> pd.DataFrame:
        """Retrieve OHLCV data"""
        query = '''
            SELECT timestamp, open, high, low, close, volume
            FROM ohlcv
            WHERE exchange = ? AND symbol = ? AND timeframe = ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, self.conn, params=(exchange, symbol, timeframe, limit))
        return df.sort_values('timestamp')
    
    def insert_signal(self, signal_data: Dict):
        """Insert trading signal"""
        try:
            self.conn.execute('''
                INSERT INTO signals 
                (exchange, symbol, signal_type, timestamp, entry_price, target_price, stop_loss, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_data['exchange'],
                signal_data['symbol'],
                signal_data['signal_type'],
                signal_data['timestamp'],
                signal_data['entry_price'],
                signal_data.get('target_price'),
                signal_data.get('stop_loss'),
                signal_data.get('confidence', 0.5)
            ))
            
            self.conn.commit()
            logger.info(f"Signal inserted: {signal_data['signal_type']} for {signal_data['symbol']}")
            
        except Exception as e:
            logger.error(f"Error inserting signal: {e}")
            self.conn.rollback()
    
    def get_signals(self, status: str = 'active', limit: int = 100) -> List[Dict]:
        """Retrieve signals"""
        query = '''
            SELECT * FROM signals
            WHERE status = ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        cursor = self.conn.execute(query, (status, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
