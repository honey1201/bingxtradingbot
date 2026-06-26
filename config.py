"""
Configuration module for BingX Trading Bot
Loads and manages environment variables and trading parameters
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# BingX API Configuration
BINGX_API_KEY=hMJEMJvUcVpF9TFrv3aifan4L6IEcnAxge7dT5jL9dGeWiriK7qAKlfBhStufuhve5wDT3ihqTtQ1wke9u3cg('BINGX_API_KEY', '')
BINGX_SECRET_KEY=65iRa9e51QQriDkJXudtE9naY04wyjfhVdcTODWcmwUH7EylBsQ8B3g4JWpaF1cZD6o3cvZ1fw9z29nXQ('BINGX_SECRET_KEY', '')
BINGX_BASE_URL = 'https://open-api.bingx.com'

# Trading Configuration
TRADING_PAIR = os.getenv('TRADING_PAIR', 'SOLUSDT')
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 30))
TIMEFRAME = '15m'  # 15-minute candles

# Moving Average Periods
MA_SHORT_PERIOD = int(os.getenv('MA_SHORT_PERIOD', 15))  # 15 x 15-min = 225 minutes
MA_LONG_PERIOD = int(os.getenv('MA_LONG_PERIOD', 60))    # 60 x 15-min = 900 minutes (15 hours)

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'trading_bot.log'

# Trading Rules
MIN_TRADE_AMOUNT = 10  # Minimum USD value per trade
POSITION_SIZE = 0.1  # 10% of capital per trade
STOP_LOSS_PERCENT = 2  # 2% stop loss
TAKE_PROFIT_PERCENT = 5  # 5% take profit

def validate_config():
    """Validate critical configuration parameters"""
    if not BINGX_API_KEY or not BINGX_SECRET_KEY:
        raise ValueError("BINGX_API_KEY and BINGX_SECRET_KEY must be set in environment variables")
    
    if MA_SHORT_PERIOD >= MA_LONG_PERIOD:
        raise ValueError("MA_SHORT_PERIOD must be less than MA_LONG_PERIOD")
    
    if POSITION_SIZE <= 0 or POSITION_SIZE > 1:
        raise ValueError("POSITION_SIZE must be between 0 and 1")
    
    return True
