"""
Trading Strategy Module
Implements moving average-based trading signals
"""

import logging
import pandas as pd
import numpy as np
from config import MA_SHORT_PERIOD, MA_LONG_PERIOD

logger = logging.getLogger(__name__)

class MovingAverageStrategy:
    """
    Moving Average Trading Strategy
    Generates buy/sell signals based on 15-minute and 1-hour moving averages
    """
    
    def __init__(self, short_period=MA_SHORT_PERIOD, long_period=MA_LONG_PERIOD):
        """
        Initialize strategy
        
        Args:
            short_period: Period for short MA (15-minute candles)
            long_period: Period for long MA (15-minute candles)
        """
        self.short_period = short_period
        self.long_period = long_period
    
    def calculate_moving_averages(self, prices):
        """
        Calculate short and long moving averages
        
        Args:
            prices: Array or Series of closing prices
        
        Returns:
            Tuple of (short_ma, long_ma)
        """
        if isinstance(prices, list):
            prices = pd.Series(prices)
        
        short_ma = prices.rolling(window=self.short_period).mean()
        long_ma = prices.rolling(window=self.long_period).mean()
        
        return short_ma, long_ma
    
    def generate_signal(self, klines_data):
        """
        Generate trading signal based on moving averages
        
        Args:
            klines_data: List of kline data from BingX API
                        Each kline: [open_time, open, high, low, close, volume, ...]
        
        Returns:
            Dict with signal information:
            {
                'signal': 'BUY' | 'SELL' | 'HOLD',
                'short_ma': float,
                'long_ma': float,
                'current_price': float,
                'confidence': float (0-1)
            }
        """
        if not klines_data or len(klines_data) < self.long_period:
            logger.warning(f"Insufficient data. Need {self.long_period} candles, got {len(klines_data) if klines_data else 0}")
            return {
                'signal': 'HOLD',
                'short_ma': None,
                'long_ma': None,
                'current_price': None,
                'confidence': 0
            }
        
        # Extract closing prices
        closing_prices = [float(candle[4]) for candle in klines_data]
        
        # Calculate moving averages
        short_ma, long_ma = self.calculate_moving_averages(closing_prices)
        
        # Get latest values
        current_short_ma = short_ma.iloc[-1]
        current_long_ma = long_ma.iloc[-1]
        current_price = closing_prices[-1]
        previous_short_ma = short_ma.iloc[-2] if len(short_ma) > 1 else current_short_ma
        previous_long_ma = long_ma.iloc[-2] if len(long_ma) > 1 else current_long_ma
        
        # Skip if MAs are NaN
        if pd.isna(current_short_ma) or pd.isna(current_long_ma):
            return {
                'signal': 'HOLD',
                'short_ma': None,
                'long_ma': None,
                'current_price': current_price,
                'confidence': 0
            }
        
        # Generate signal
        signal = self._determine_signal(
            current_price,
            current_short_ma,
            current_long_ma,
            previous_short_ma,
            previous_long_ma
        )
        
        # Calculate confidence (how far price is from MAs)
        confidence = self._calculate_confidence(current_price, current_short_ma, current_long_ma)
        
        return {
            'signal': signal,
            'short_ma': round(current_short_ma, 2),
            'long_ma': round(current_long_ma, 2),
            'current_price': round(current_price, 2),
            'confidence': round(confidence, 2)
        }
    
    def _determine_signal(self, price, short_ma, long_ma, prev_short_ma, prev_long_ma):
        """
        Determine BUY/SELL/HOLD signal
        
        BUY: Short MA crosses above Long MA (Golden Cross)
        SELL: Short MA crosses below Long MA (Death Cross)
        """
        # Golden Cross: Short MA crosses above Long MA
        if prev_short_ma <= prev_long_ma and short_ma > long_ma:
            return 'BUY'
        
        # Death Cross: Short MA crosses below Long MA
        elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
            return 'SELL'
        
        # Trending Up: Price above both MAs
        elif price > short_ma > long_ma:
            return 'BUY'
        
        # Trending Down: Price below both MAs
        elif price < short_ma < long_ma:
            return 'SELL'
        
        return 'HOLD'
    
    def _calculate_confidence(self, price, short_ma, long_ma):
        """
        Calculate signal confidence based on position relative to MAs
        
        Returns:
            Confidence score 0-1 (1 = most confident)
        """
        if short_ma == 0 or long_ma == 0:
            return 0
        
        # Distance from short MA as percentage
        distance_short = abs(price - short_ma) / short_ma
        
        # Distance between MAs
        distance_mas = abs(short_ma - long_ma) / long_ma
        
        # Confidence increases with distance from short MA and distance between MAs
        confidence = min(distance_short * distance_mas, 1.0)
        
        return confidence
