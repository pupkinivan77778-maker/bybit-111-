import pandas as pd
from typing import Dict, List
from signal_bot_3.core.logger import logger

class TimeframeSync:
    def __init__(self, timeframes: List[str] = None):
        self.timeframes = timeframes or ['5m', '15m', '1h', '4h']
    
    def sync_signals(self, tf_signals: Dict[str, Dict]) -> Dict:
        """Sync signals across timeframes for confirmation"""
        if not tf_signals:
            return None
        
        primary_tf = self.timeframes[-1]
        primary_signal = tf_signals.get(primary_tf)
        
        if not primary_signal:
            return None
        
        confirmation_count = 0
        total_confidence = primary_signal.get('confidence', 0)
        
        for tf in self.timeframes[:-1]:
            if tf in tf_signals:
                signal = tf_signals[tf]
                if signal['signal_type'] == primary_signal['signal_type']:
                    confirmation_count += 1
                    total_confidence += signal.get('confidence', 0)
        
        confirmation_score = confirmation_count / len(self.timeframes)
        avg_confidence = total_confidence / (confirmation_count + 1)
        
        primary_signal['confirmation_score'] = confirmation_score
        primary_signal['avg_confidence'] = avg_confidence
        primary_signal['confirmed_timeframes'] = confirmation_count + 1
        
        logger.info(f"Timeframe sync: {confirmation_count + 1}/{len(self.timeframes)} confirmed, score: {confirmation_score:.2f}")
        return primary_signal
