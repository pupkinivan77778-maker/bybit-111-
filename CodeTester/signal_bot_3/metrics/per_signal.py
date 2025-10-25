from typing import Dict, List
from signal_bot_3.core.logger import logger

class PerSignalMetrics:
    def __init__(self, commission: float = 0.001, slippage: float = 0.0005):
        self.commission = commission
        self.slippage = slippage
    
    def calculate_trade_result(self, signal: Dict, exit_price: float) -> Dict:
        """Calculate PnL and metrics for a single trade"""
        entry = signal['entry_price']
        position_size = signal.get('position_size', 1.0)
        
        if signal['signal_type'] == 'LONG':
            gross_pnl = (exit_price - entry) * position_size
        else:
            gross_pnl = (entry - exit_price) * position_size
        
        entry_cost = entry * position_size * (self.commission + self.slippage)
        exit_cost = exit_price * position_size * (self.commission + self.slippage)
        
        net_pnl = gross_pnl - entry_cost - exit_cost
        
        return_pct = (net_pnl / (entry * position_size)) * 100
        
        result = {
            'entry_price': entry,
            'exit_price': exit_price,
            'signal_type': signal['signal_type'],
            'position_size': position_size,
            'gross_pnl': gross_pnl,
            'costs': entry_cost + exit_cost,
            'net_pnl': net_pnl,
            'return_pct': return_pct,
            'timestamp': signal.get('timestamp'),
            'timeframe': signal.get('timeframe')
        }
        
        logger.debug(f"Trade result: PnL=${net_pnl:.2f} ({return_pct:.2f}%)")
        return result
    
    def simulate_exit(self, signal: Dict, df) -> float:
        """Simulate exit based on stop loss or target"""
        if df.empty:
            return signal['entry_price']
        
        target = signal.get('target_price', signal['entry_price'])
        stop = signal.get('stop_loss', signal['entry_price'])
        
        for _, row in df.iterrows():
            if signal['signal_type'] == 'LONG':
                if row['high'] >= target:
                    return target
                if row['low'] <= stop:
                    return stop
            else:
                if row['low'] <= target:
                    return target
                if row['high'] >= stop:
                    return stop
        
        return df['close'].iloc[-1] if not df.empty else signal['entry_price']
