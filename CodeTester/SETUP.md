# Signal Bot 3.0 - Инструкция по запуску

## Быстрый старт

### 1. Добавьте API ключи

Создайте файл `.env` и добавьте ваши ключи:

```bash
# Telegram Bot (обязательно)
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Binance API (опционально, для реальных данных)
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# Bybit API (опционально)
BYBIT_API_KEY=your_bybit_api_key
BYBIT_API_SECRET=your_bybit_api_secret
```

**Как получить Telegram Bot Token:**
1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot` или `/token` (если бот уже создан)
3. Скопируйте токен и добавьте в `.env`

### 2. Запустите бота

```bash
python main.py
```

### 3. Используйте бота в Telegram

Найдите вашего бота в Telegram и отправьте:
- `/start` - Начать работу
- `/help` - Справка
- `/run_backtest` - Запустить бэктест BTC/USDT
- `/status` - Проверить статус

## CLI Использование

Запуск бэктеста через командную строку:

```bash
python run_cli.py --symbol BTC/USDT --exchange binance --timeframes 5m 15m 1h 4h --limit 100
```

## Структура проекта

```
signal_bot_3/
├── core/              # Управление ботом и логирование
├── data/              # Сбор данных (REST/WebSocket)
├── signals/           # Генерация сигналов
├── risk_manager/      # Управление рисками
├── multi_timeframe/   # Анализ по таймфреймам
├── metrics/           # Метрики производительности
├── telegram/          # Telegram бот
└── ui/                # CLI интерфейс
```

## Функциональность Phase 1 (MVP)

✅ REST + WebSocket коллекторы (Binance, Bybit)
✅ SQLite persistence
✅ Генерация сигналов с мультитаймфрейм подтверждением
✅ Risk/Reward расчет и position sizing
✅ Performance метрики (Sharpe, Sortino, Win Rate, PnL)
✅ Telegram бот с async обработкой
✅ CLI с прогресс-баром
✅ Заглушка для AI-движка (готовность к Phase 3)

## Следующие шаги (Phase 2)

- Inline кнопки в Telegram
- Экспорт результатов в CSV/JSON
- Графики Equity и Drawdown
- Корреляционный анализ

## Поддержка

Все логи сохраняются в `logs/signal_bot.log`
База данных: `signal_bot_3/data/market.db`
