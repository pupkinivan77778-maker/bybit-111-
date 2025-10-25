import pandas as pd
import numpy as np
from typing import List, Dict
from signal_bot_3.core.logger import logger

class PerformanceMetrics:
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
    
    def calculate_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate comprehensive backtest metrics"""
        if not trades:
            return {}
        
        df = pd.DataFrame(trades)
        
        total_trades = len(df)
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] < 0])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl = df['pnl'].sum()
        avg_win = df[df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        
        profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 and avg_loss != 0 else 0
        
        df['cumulative_pnl'] = df['pnl'].cumsum()
        df['equity'] = self.initial_capital + df['cumulative_pnl']
        
        peak = df['equity'].expanding().max()
        drawdown = (df['equity'] - peak) / peak
        max_drawdown = drawdown.min()
        
        returns = df['equity'].pct_change().dropna()
        sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std()) if len(returns) > 0 and returns.std() > 0 else 0
        
        downside_returns = returns[returns < 0]
        sortino_ratio = np.sqrt(252) * (returns.mean() / downside_returns.std()) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
        
        metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'final_equity': df['equity'].iloc[-1] if len(df) > 0 else self.initial_capital,
            'return_pct': (df['equity'].iloc[-1] / self.initial_capital - 1) * 100 if len(df) > 0 else 0
        }
        
        logger.info(f"Performance: WinRate={win_rate:.2%}, PnL=${total_pnl:.2f}, Sharpe={sharpe_ratio:.2f}")
        return metrics
