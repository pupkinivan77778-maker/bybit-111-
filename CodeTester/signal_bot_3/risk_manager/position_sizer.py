from typing import Dict
from signal_bot_3.core.logger import logger

class PositionSizer:
    def __init__(self, max_risk_per_trade: float = 0.02):
        self.max_risk_per_trade = max_risk_per_trade
    
    def calculate_position_size(
        self, 
        signal: Dict, 
        account_balance: float
    ) -> float:
        """Calculate position size based on risk"""
        entry = signal['entry_price']
        stop = signal.get('stop_loss', entry)
        
        if signal['signal_type'] == 'LONG':
            risk_per_unit = entry - stop
        else:
            risk_per_unit = stop - entry
        
        if risk_per_unit <= 0:
            return 0.0
        
        max_risk_amount = account_balance * self.max_risk_per_trade
        position_size = max_risk_amount / risk_per_unit
        
        logger.info(f"Position size: {position_size:.4f} units (Risk: ${max_risk_amount:.2f})")
        return position_size
