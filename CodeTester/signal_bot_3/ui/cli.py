import asyncio
from typing import List, Dict
from tqdm import tqdm
from signal_bot_3.data.ohlcv_collector import OHLCVCollector
from signal_bot_3.signals.signal_engine import SignalEngine
from signal_bot_3.multi_timeframe.timeframe_sync import TimeframeSync
from signal_bot_3.risk_manager.reward_calculator import RewardCalculator
from signal_bot_3.risk_manager.position_sizer import PositionSizer
from signal_bot_3.metrics.performance import PerformanceMetrics
from signal_bot_3.metrics.per_signal import PerSignalMetrics
from signal_bot_3.core.logger import logger
import json

def run_backtest(
    symbol: str = 'BTC/USDT',
    exchange: str = 'binance',
    timeframes: List[str] = None,
    limit: int = 100
) -> Dict:
    """Run backtest with progress bar"""
    
    if timeframes is None:
        timeframes = ['5m', '15m', '1h', '4h']
    
    logger.info(f"Starting backtest for {symbol} on {exchange}")
    
    collector = OHLCVCollector(exchange)
    signal_engine = SignalEngine({'min_confirmation_score': 0.6})
    tf_sync = TimeframeSync(timeframes)
    rr_calc = RewardCalculator(min_risk_reward=1.5)
    pos_sizer = PositionSizer(max_risk_per_trade=0.02)
    perf_metrics = PerformanceMetrics(initial_capital=10000)
    signal_metrics = PerSignalMetrics()
    
    multi_tf_data = {}
    
    print(f"\n📊 Fetching data for {symbol}...")
    with tqdm(total=len(timeframes), desc="Downloading OHLCV") as pbar:
        for tf in timeframes:
            df = asyncio.run(collector.fetch_ohlcv(symbol, tf, limit))
            multi_tf_data[tf] = df
            pbar.update(1)
    
    print("\n🔍 Generating signals...")
    signals = signal_engine.generate_signals(multi_tf_data)
    
    if not signals:
        logger.warning("No signals generated")
        return {'signals': [], 'metrics': {}}
    
    print(f"\n✅ Generated {len(signals)} signals")
    
    trades = []
    account_balance = 10000
    
    print("\n💹 Simulating trades...")
    with tqdm(total=len(signals), desc="Backtesting") as pbar:
        for signal in signals:
            if rr_calc.is_valid_signal(signal):
                signal['position_size'] = pos_sizer.calculate_position_size(signal, account_balance)
                
                tf = signal.get('timeframe', timeframes[0])
                exit_df = multi_tf_data[tf].iloc[-10:]
                
                exit_price = signal_metrics.simulate_exit(signal, exit_df)
                trade_result = signal_metrics.calculate_trade_result(signal, exit_price)
                
                trades.append(trade_result)
                account_balance += trade_result['net_pnl']
            
            pbar.update(1)
    
    metrics = perf_metrics.calculate_metrics(trades)
    
    print("\n" + "="*50)
    print("📈 BACKTEST RESULTS")
    print("="*50)
    print(f"Total Trades: {metrics.get('total_trades', 0)}")
    print(f"Win Rate: {metrics.get('win_rate', 0)*100:.1f}%")
    print(f"Total PnL: ${metrics.get('total_pnl', 0):.2f}")
    print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"Max Drawdown: {metrics.get('max_drawdown', 0)*100:.1f}%")
    print("="*50 + "\n")
    
    return {
        'signals': signals,
        'trades': trades,
        'metrics': metrics
    }

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Signal Bot 3.0 - Crypto Trading Signals')
    parser.add_argument('--symbol', default='BTC/USDT', help='Trading pair')
    parser.add_argument('--exchange', default='binance', help='Exchange name')
    parser.add_argument('--timeframes', nargs='+', default=['5m', '15m', '1h', '4h'], help='Timeframes')
    parser.add_argument('--limit', type=int, default=100, help='Number of candles')
    
    args = parser.parse_args()
    
    result = run_backtest(
        symbol=args.symbol,
        exchange=args.exchange,
        timeframes=args.timeframes,
        limit=args.limit
    )
    
    with open('backtest_result.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print("📁 Results saved to backtest_result.json")

if __name__ == "__main__":
    main()
