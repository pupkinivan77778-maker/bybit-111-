from typing import Dict
from signal_bot_3.core.logger import logger

class RewardCalculator:
    def __init__(self, min_risk_reward: float = 1.5):
        self.min_risk_reward = min_risk_reward
    
    def calculate_risk_reward(self, signal: Dict) -> float:
        """Calculate risk/reward ratio for signal"""
        entry = signal['entry_price']
        target = signal.get('target_price', entry)
        stop = signal.get('stop_loss', entry)
        
        if signal['signal_type'] == 'LONG':
            risk = entry - stop
            reward = target - entry
        else:
            risk = stop - entry
            reward = entry - target
        
        if risk <= 0:
            return 0.0
        
        rr_ratio = reward / risk
        logger.debug(f"Risk/Reward: {rr_ratio:.2f} (Risk: {risk:.4f}, Reward: {reward:.4f})")
        return rr_ratio
    
    def is_valid_signal(self, signal: Dict) -> bool:
        """Check if signal meets risk/reward criteria"""
        rr = self.calculate_risk_reward(signal)
        is_valid = rr >= self.min_risk_reward
        
        if not is_valid:
            logger.info(f"Signal rejected: R/R {rr:.2f} < {self.min_risk_reward}")
        
        return is_valid
