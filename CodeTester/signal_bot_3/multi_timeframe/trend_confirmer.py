import pandas as pd
import pandas_ta as ta
from typing import Dict
from signal_bot_3.core.logger import logger

class TrendConfirmer:
    def __init__(self):
        self.ema_period = 200
    
    def confirm_trend(self, df: pd.DataFrame, signal: Dict) -> bool:
        """Confirm if signal aligns with higher timeframe trend"""
        if df.empty or len(df) < self.ema_period:
            return True
        
        df = df.copy()
        df['ema_200'] = ta.ema(df['close'], length=self.ema_period)
        
        last_close = df['close'].iloc[-1]
        ema_200 = df['ema_200'].iloc[-1]
        
        if signal['signal_type'] == 'LONG':
            is_confirmed = last_close > ema_200
        else:
            is_confirmed = last_close < ema_200
        
        logger.info(f"Trend confirmation: {is_confirmed} ({signal['signal_type']}, price: {last_close:.2f}, EMA200: {ema_200:.2f})")
        return is_confirmed
