# Signal Bot 3.0

## Overview

Signal Bot 3.0 is a professional cryptocurrency market analysis bot designed to generate trading signals with probability-based predictions and comprehensive risk management. The system supports multiple exchanges (Binance, Bybit), performs multi-timeframe analysis, and provides backtesting capabilities through both CLI and Telegram interfaces.

### Core Purpose
- Generate crypto trading signals with probability scores and risk/reward ratios
- Analyze markets across multiple timeframes (5m, 15m, 1h, 4h) for confirmation
- Provide backtesting capabilities with detailed performance metrics
- Support real-time data collection via REST and WebSocket APIs
- Deliver signals through Telegram bot and command-line interface

### Current Phase: MVP (Phase 1) - ✅ COMPLETED
Phase 1 MVP is fully implemented and tested. All core functionality is operational:
- ✅ REST + WebSocket collectors for Binance and Bybit
- ✅ SQLite persistence with optimized queries
- ✅ Multi-timeframe signal generation (5m, 15m, 1h, 4h)
- ✅ Risk management (R/R, position sizing, ATR-based stops)
- ✅ Performance metrics (Sharpe, Sortino, Win Rate, PnL, Drawdown)
- ✅ Telegram bot with async handling (/start, /help, /run_backtest, /status)
- ✅ CLI with progress bars for backtesting
- ✅ Placeholder adaptive engine ready for Phase 3 ML enhancement

**Last Updated**: October 8, 2025
**Status**: Ready for deployment - requires API keys (see SETUP.md)

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### 1. Data Collection Layer
**Problem**: Need reliable, real-time market data from multiple exchanges
**Solution**: Dual REST + WebSocket architecture using CCXT library
- `OHLCVCollector`: Fetches historical OHLCV (Open, High, Low, Close, Volume) data via REST
- `WebSocketCollector`: Streams real-time trade data for live analysis
- Supports Binance and Bybit exchanges with configurable rate limiting
- Async/await pattern for non-blocking data operations

**Design Rationale**: CCXT provides unified API access across exchanges, reducing integration complexity. WebSocket streaming enables real-time updates while REST handles historical data bulk fetches.

### 2. Data Persistence
**Problem**: Store market data and signals for backtesting and analysis
**Solution**: SQLite database with structured schemas
- `MarketDatabase`: Manages two core tables (ohlcv, signals)
- Unique constraints prevent duplicate entries
- Thread-safe connection handling with row factory for dict-like access
- Database path configurable via environment variable

**Design Rationale**: SQLite chosen for simplicity and portability in MVP phase. No external database server required, suitable for single-instance deployment.

### 3. Signal Generation
**Problem**: Generate reliable trading signals with confidence scoring
**Solution**: Multi-layer signal engine with placeholder for ML
- `SimpleSignal`: Technical indicator-based signals (RSI, EMA crossovers, volume)
- `AdaptiveSignalEngine`: Placeholder stub returning random probabilities (prepared for Phase 3 ML integration)
- `SignalEngine`: Orchestrates signal generation across timeframes

**Technical Indicators Used**:
- RSI (Relative Strength Index) for overbought/oversold conditions
- EMA (Exponential Moving Average) crossovers for trend detection
- Volume analysis for confirmation
- ATR (Average True Range) for volatility-adjusted stops

**Design Rationale**: Simple indicators provide baseline functionality while adaptive engine architecture is prepared for future ML models without requiring system redesign.

### 4. Multi-Timeframe Analysis
**Problem**: Increase signal reliability through cross-timeframe confirmation
**Solution**: Synchronization and trend confirmation system
- `TimeframeSync`: Aggregates signals across 4 timeframes, calculates confirmation scores
- `TrendConfirmer`: Validates signals against higher timeframe trends (200 EMA)
- Weighted confidence scoring based on number of confirming timeframes

**Design Rationale**: Multi-timeframe confirmation reduces false signals. Primary signal comes from highest timeframe (4h), confirmed by lower timeframes.

### 5. Risk Management
**Problem**: Control trade risk and ensure favorable risk/reward ratios
**Solution**: Three-component risk system
- `RewardCalculator`: Validates minimum risk/reward ratio (default 1.5:1)
- `PositionSizer`: Calculates position size based on account risk percentage (default 2%)
- `VolatilityAdjuster`: Sets ATR-based dynamic stop losses and targets

**Design Rationale**: Separates concerns into focused modules. ATR-based stops adapt to market volatility automatically, preventing tight stops in volatile markets.

### 6. Performance Metrics
**Problem**: Evaluate strategy effectiveness comprehensively
**Solution**: Dual metrics system
- `PerSignalMetrics`: Calculates individual trade PnL including commissions and slippage
- `PerformanceMetrics`: Aggregates portfolio metrics (Sharpe ratio, Sortino ratio, max drawdown, win rate, profit factor)

**Metrics Calculated**:
- Win rate and profit factor
- Risk-adjusted returns (Sharpe, Sortino)
- Maximum drawdown
- Average win/loss amounts
- Cumulative PnL and equity curves

**Design Rationale**: Professional-grade metrics enable objective strategy evaluation. Sharpe and Sortino ratios account for risk, not just returns.

### 7. User Interfaces
**Problem**: Provide accessible interfaces for different use cases
**Solution**: Dual interface approach
- CLI (`cli.py`): Command-line backtesting with progress bars (tqdm)
- Telegram Bot (`telegram_bot.py`): Conversational interface with Markdown formatting

**CLI Features**:
- Progress bars for data fetching and signal generation
- Formatted output with results summary
- Async execution for responsive experience

**Telegram Features**:
- Commands: /start, /help, /run_backtest, /status
- Markdown-formatted responses
- Async handlers for concurrent user support

**Design Rationale**: CLI serves developers/analysts, Telegram serves end users. Both share core logic through service modules.

### 8. Bot Control & Scheduling
**Problem**: Manage bot lifecycle and periodic tasks
**Solution**: Controller pattern with async scheduler
- `BotController`: Manages bot startup/shutdown lifecycle
- `Scheduler`: Handles periodic task execution (prepared for live trading)

**Design Rationale**: Separation allows independent scaling of components. Scheduler prepared for future real-time signal generation.

### 9. Configuration Management
**Problem**: Flexible configuration without code changes
**Solution**: Hybrid config approach
- JSON config file (`config.json`) for static settings
- Environment variables (.env) for secrets and paths
- Defaults in code as fallbacks

**Configurable Elements**:
- Exchange endpoints and rate limits
- Timeframe selections
- Signal engine thresholds
- Risk management parameters
- Backtesting settings

**Design Rationale**: JSON for structured settings, env vars for secrets follows security best practices. Layered defaults prevent startup failures.

### 10. Logging System
**Problem**: Debug issues and monitor operations
**Solution**: Structured logging with dual output
- Console handler: INFO level for user feedback
- File handler: DEBUG level with rotation (10MB max, 5 backups)
- Configurable via environment variables

**Design Rationale**: Rotating file handler prevents disk space issues. Dual output allows real-time monitoring while preserving detailed logs.

## External Dependencies

### Cryptocurrency Exchange APIs
- **Binance API** (REST + WebSocket)
  - REST: `https://api.binance.com`
  - WebSocket: `wss://stream.binance.com:9443`
  - Used for: OHLCV data, real-time trades
  - Authentication: Optional (API key/secret via env vars)

- **Bybit API** (REST + WebSocket)
  - REST: `https://api.bybit.com`
  - WebSocket: `wss://stream.bybit.com/v5/public/linear`
  - Used for: OHLCV data, real-time trades
  - Authentication: Optional (API key/secret via env vars)

### Python Libraries
- **ccxt**: Unified cryptocurrency exchange API library (handles REST calls)
- **websockets**: WebSocket client for real-time data streaming
- **pandas**: Data manipulation and analysis framework
- **pandas_ta**: Technical analysis indicators library
- **python-telegram-bot**: Telegram Bot API wrapper
- **tqdm**: Progress bar library for CLI
- **python-dotenv**: Environment variable management

### Database
- **SQLite**: Embedded relational database (no external server required)
  - Database file: `signal_bot_3/data/market.db` (configurable)
  - Used for: Storing OHLCV data and generated signals

### Environment Variables Required
```
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
BINANCE_API_KEY=<optional>
BINANCE_API_SECRET=<optional>
BYBIT_API_KEY=<optional>
BYBIT_API_SECRET=<optional>
LOG_LEVEL=INFO
LOG_FILE=logs/signal_bot.log
DATABASE_PATH=signal_bot_3/data/market.db
```

### Future Dependencies (Prepared Architecture)
- Machine learning framework (TensorFlow/PyTorch) for adaptive signal engine
- Additional technical indicator libraries
- Advanced correlation analysis tools