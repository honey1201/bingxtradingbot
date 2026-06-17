# BingX Trading Bot

An automated trading bot for BingX that uses 15-minute and 1-hour moving averages to generate buy/sell signals.

## Features

- **Moving Average Strategy**: Combines 15-minute and 1-hour moving averages for signal generation
- **Golden/Death Cross Detection**: Automatically detects moving average crossovers
- **Secure API Integration**: HMAC-SHA256 authenticated requests to BingX
- **Configurable Parameters**: Easy environment-based configuration
- **Comprehensive Logging**: File and console logging for debugging and monitoring

## Architecture

```
bingxtradingbot/
├── main.py              # Bot main loop and trade execution
├── strategy.py          # Moving average trading strategy
├── bingx_api.py         # BingX API client
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your BingX API credentials:

```bash
BINGX_API_KEY=your_api_key_here
BINGX_SECRET_KEY=your_secret_key_here
TRADING_PAIR=BTCUSDT
INITIAL_CAPITAL=1000
MA_SHORT_PERIOD=15
MA_LONG_PERIOD=60
LOG_LEVEL=INFO
```

### 3. Obtain BingX API Credentials

1. Go to [BingX API Management](https://www.bingx.com/en/account/apimanagement)
2. Create a new API key
3. Copy your API Key and Secret Key
4. **Security**: Use a sub-account with limited trading permissions for live trading

## Strategy Explanation

### Moving Averages

- **Short MA (15 periods)**: 15 × 15-minute candles = 225 minutes (~3.75 hours)
- **Long MA (60 periods)**: 60 × 15-minute candles = 900 minutes (~15 hours)

### Signal Generation

| Condition | Signal | Description |
|-----------|--------|-------------|
| Short MA crosses above Long MA | BUY | Golden Cross - Uptrend signal |
| Short MA crosses below Long MA | SELL | Death Cross - Downtrend signal |
| Price > Short MA > Long MA | BUY | Continuation of uptrend |
| Price < Short MA < Long MA | SELL | Continuation of downtrend |
| Other | HOLD | Uncertain market conditions |

### Confidence Scoring

The bot calculates a confidence score (0-1) based on:
- Distance of price from short MA
- Distance between short and long MAs

Only trades with confidence > 0.3 are executed.

## Running the Bot

### Dry Run Mode (Default)

The bot is configured for **dry run mode** by default - it logs signals but doesn't execute real trades.

```bash
python main.py
```

Monitor the output and check `trading_bot.log` for signals.

### Live Trading Mode

To enable live trading, uncomment the trade execution code in `main.py`:

1. Edit `main.py`
2. Uncomment the `api_client.place_order()` calls in `_execute_buy()` and `_execute_sell()`
3. Run: `python main.py`

**⚠️ Warning**: Only enable live trading after thoroughly testing in dry run mode.

## Configuration Parameters

### Trading Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TRADING_PAIR` | BTCUSDT | Trading pair (symbol) |
| `INITIAL_CAPITAL` | 1000 | Initial trading capital (USD) |
| `TIMEFRAME` | 15m | Candlestick timeframe |
| `POSITION_SIZE` | 0.1 | Risk per trade (10% of capital) |

### Stop Loss & Take Profit

| Parameter | Default | Description |
|-----------|---------|-------------|
| `STOP_LOSS_PERCENT` | 2 | Stop loss level (%) |
| `TAKE_PROFIT_PERCENT` | 5 | Take profit level (%) |

## Monitoring & Logging

Logs are written to both console and `trading_bot.log`:

```
2026-06-17 10:30:45,123 - main - INFO - Signal Check - BTCUSDT: Price=$45000, Short MA=$44500, Long MA=$44000, Signal=BUY, Confidence=0.65
```

Log levels:
- `DEBUG`: Detailed information (skip trades, etc.)
- `INFO`: General trading information (signals, orders)
- `WARNING`: Warnings (insufficient data)
- `ERROR`: Errors (API failures, trade failures)

## API Reference

See `bingx_api.py` for available methods:

- `get_klines()`: Fetch candlestick data
- `get_account_info()`: Get account balance
- `place_order()`: Place buy/sell orders
- `cancel_order()`: Cancel orders
- `get_order()`: Get order status

## Risk Management

⚠️ **Important**:

1. **Start Small**: Test with minimal capital first
2. **Use Sub-Accounts**: Never give main account API access
3. **API Key Permissions**: Limit to spot trading only
4. **Monitor Regularly**: Check logs and performance daily
5. **Risk Per Trade**: Default is 10% of capital - adjust in config
6. **Slippage**: Add margin to entry/exit prices in live trading
7. **Network Issues**: Implement circuit breakers for connection failures

## Troubleshooting

### "API request failed"

- Check API credentials in `.env`
- Verify BingX API key permissions
- Check network connectivity
- Check BingX API status

### "Insufficient data"

- Wait for more candles to load
- Increase `limit` parameter in `fetch_market_data()`

### "Configuration error"

- Verify all required environment variables are set
- Check that `MA_SHORT_PERIOD < MA_LONG_PERIOD`

## Future Enhancements

- [ ] RSI and MACD indicators
- [ ] Dynamic position sizing
- [ ] Trailing stop losses
- [ ] Multiple trading pairs
- [ ] WebSocket real-time data
- [ ] Performance analytics dashboard
- [ ] Backtesting engine

## Support

For issues or questions:
1. Check the logs in `trading_bot.log`
2. Review the configuration in `.env`
3. Test API connectivity manually using `bingx_api.py`

## License

This project is provided as-is for educational purposes.

## Disclaimer

⚠️ **Trading involves risk**. Past performance does not guarantee future results. Use this bot at your own risk. The authors are not responsible for any financial losses incurred through the use of this software.
