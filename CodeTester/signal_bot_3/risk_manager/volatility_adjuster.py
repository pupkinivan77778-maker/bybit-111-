import pandas as pd
import pandas_ta as ta
from typing import Dict
from signal_bot_3.core.logger import logger

class VolatilityAdjuster:
    def __init__(self, atr_multiplier: float = 2.0):
        self.atr_multiplier = atr_multiplier
    
    def adjust_stops(self, signal: Dict, df: pd.DataFrame) -> Dict:
        """Adjust stop loss and target based on ATR"""
        atr = ta.atr(df['high'], df['low'], df['close'], length=14).iloc[-1]
        entry = signal['entry_price']
        
        if signal['signal_type'] == 'LONG':
            signal['stop_loss'] = entry - (self.atr_multiplier * atr)
            signal['target_price'] = entry + (self.atr_multiplier * 1.5 * atr)
        else:
            signal['stop_loss'] = entry + (self.atr_multiplier * atr)
            signal['target_price'] = entry - (self.atr_multiplier * 1.5 * atr)
        
        logger.info(f"ATR-adjusted stops: SL={signal['stop_loss']:.4f}, TP={signal['target_price']:.4f}")
        return signal
