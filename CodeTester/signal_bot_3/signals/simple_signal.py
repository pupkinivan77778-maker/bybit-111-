import pandas as pd
import pandas_ta as ta
from typing import Dict, Optional
from signal_bot_3.core.logger import logger

class SimpleSignal:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.rsi_period = self.config.get('rsi_period', 14)
        self.rsi_oversold = self.config.get('rsi_oversold', 30)
        self.rsi_overbought = self.config.get('rsi_overbought', 70)
        self.ema_fast = self.config.get('ema_fast', 9)
        self.ema_slow = self.config.get('ema_slow', 21)
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """Generate trading signal from OHLCV data"""
        if df.empty or len(df) < max(self.rsi_period, self.ema_slow):
            return None
        
        df = df.copy()
        
        df['rsi'] = ta.rsi(df['close'], length=self.rsi_period)
        df['ema_fast'] = ta.ema(df['close'], length=self.ema_fast)
        df['ema_slow'] = ta.ema(df['close'], length=self.ema_slow)
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        signal_type = None
        confidence = 0.0
        
        if (last['rsi'] < self.rsi_oversold and 
            last['ema_fast'] > last['ema_slow'] and
            prev['ema_fast'] <= prev['ema_slow']):
            signal_type = 'LONG'
            confidence = 0.6 + (self.rsi_oversold - last['rsi']) / 100
        
        elif (last['rsi'] > self.rsi_overbought and 
              last['ema_fast'] < last['ema_slow'] and
              prev['ema_fast'] >= prev['ema_slow']):
            signal_type = 'SHORT'
            confidence = 0.6 + (last['rsi'] - self.rsi_overbought) / 100
        
        if signal_type:
            atr = ta.atr(df['high'], df['low'], df['close'], length=14).iloc[-1]
            
            signal = {
                'signal_type': signal_type,
                'entry_price': float(last['close']),
                'timestamp': int(last['timestamp']),
                'confidence': min(confidence, 0.95),
                'indicators': {
                    'rsi': float(last['rsi']),
                    'ema_fast': float(last['ema_fast']),
                    'ema_slow': float(last['ema_slow']),
                    'volume': float(last['volume']),
                    'atr': float(atr)
                }
            }
            
            if signal_type == 'LONG':
                signal['stop_loss'] = float(last['close'] - 2 * atr)
                signal['target_price'] = float(last['close'] + 3 * atr)
            else:
                signal['stop_loss'] = float(last['close'] + 2 * atr)
                signal['target_price'] = float(last['close'] - 3 * atr)
            
            logger.info(f"Signal generated: {signal_type} at {last['close']}, confidence: {confidence:.2f}")
            return signal
        
        return None
