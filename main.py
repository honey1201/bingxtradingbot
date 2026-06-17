"""
BingX Trading Bot - Main Entry Point
15-minute and 1-hour moving average-based trading bot
"""

import logging
import time
import sys
from config import (
    TRADING_PAIR, TIMEFRAME, LOG_LEVEL, LOG_FILE,
    validate_config, INITIAL_CAPITAL, POSITION_SIZE
)
from bingx_api import api_client
from strategy import MovingAverageStrategy

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, trading_pair=TRADING_PAIR, timeframe=TIMEFRAME):
        self.trading_pair = trading_pair
        self.timeframe = timeframe
        self.strategy = MovingAverageStrategy()
        self.last_signal = None
        self.position_open = False
        self.entry_price = None
        
        logger.info(f"Trading Bot initialized for {trading_pair} on {timeframe}")
    
    def fetch_market_data(self, limit=100):
        """Fetch latest klines data"""
        try:
            response = api_client.get_klines(self.trading_pair, self.timeframe, limit=limit)
            
            if 'data' in response:
                return response['data']
            else:
                logger.error(f"Unexpected API response: {response}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return None
    
    def check_signal(self):
        """Check for trading signals"""
        klines = self.fetch_market_data(limit=100)
        
        if not klines:
            logger.warning("No market data available")
            return None
        
        signal_data = self.strategy.generate_signal(klines)
        
        logger.info(
            f"Signal Check - {self.trading_pair}: "
            f"Price=${signal_data['current_price']}, "
            f"Short MA=${signal_data['short_ma']}, "
            f"Long MA=${signal_data['long_ma']}, "
            f"Signal={signal_data['signal']}, "
            f"Confidence={signal_data['confidence']}"
        )
        
        return signal_data
    
    def execute_trade(self, signal_data):
        """Execute trades based on signals"""
        signal = signal_data['signal']
        confidence = signal_data['confidence']
        
        # Only trade if confidence is above threshold
        if confidence < 0.3:
            logger.debug(f"Signal confidence too low ({confidence}), skipping trade")
            return
        
        # Avoid duplicate signals
        if self.last_signal == signal:
            logger.debug(f"Duplicate signal, skipping")
            return
        
        try:
            if signal == 'BUY' and not self.position_open:
                self._execute_buy(signal_data)
            elif signal == 'SELL' and self.position_open:
                self._execute_sell(signal_data)
        
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
        
        self.last_signal = signal
    
    def _execute_buy(self, signal_data):
        """Execute buy order"""
        logger.info(
            f"BUY SIGNAL - {self.trading_pair} at ${signal_data['current_price']} "
            f"(Confidence: {signal_data['confidence']})"
        )
        
        # Calculate order quantity based on position size
        quantity = (INITIAL_CAPITAL * POSITION_SIZE) / signal_data['current_price']
        
        logger.info(f"Placing BUY order: {quantity} {self.trading_pair}")
        
        # Uncomment to enable live trading:
        # try:
        #     order = api_client.place_order(
        #         self.trading_pair,
        #         'BUY',
        #         quantity,
        #         price=signal_data['current_price'],
        #         order_type='LIMIT'
        #     )
        #     logger.info(f"BUY Order placed: {order}")
        #     self.position_open = True
        #     self.entry_price = signal_data['current_price']
        # except Exception as e:
        #     logger.error(f"Failed to place BUY order: {e}")
    
    def _execute_sell(self, signal_data):
        """Execute sell order"""
        logger.info(
            f"SELL SIGNAL - {self.trading_pair} at ${signal_data['current_price']} "
            f"(Confidence: {signal_data['confidence']})"
        )
        
        # Calculate order quantity (sell entire position)
        quantity = (INITIAL_CAPITAL * POSITION_SIZE) / self.entry_price if self.entry_price else 0
        
        logger.info(f"Placing SELL order: {quantity} {self.trading_pair}")
        
        # Uncomment to enable live trading:
        # try:
        #     order = api_client.place_order(
        #         self.trading_pair,
        #         'SELL',
        #         quantity,
        #         price=signal_data['current_price'],
        #         order_type='LIMIT'
        #     )
        #     logger.info(f"SELL Order placed: {order}")
        #     self.position_open = False
        #     self.entry_price = None
        # except Exception as e:
        #     logger.error(f"Failed to place SELL order: {e}")
    
    def run(self, check_interval=300):
        """
        Run the trading bot
        
        Args:
            check_interval: Seconds between checks (default: 300 = 5 minutes)
        """
        logger.info(f"Starting Trading Bot - Check interval: {check_interval} seconds")
        
        try:
            while True:
                logger.debug("Checking for trading signals...")
                signal_data = self.check_signal()
                
                if signal_data:
                    self.execute_trade(signal_data)
                
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            logger.info("Trading bot shutdown complete")

def main():
    """Main entry point"""
    try:
        # Validate configuration
        validate_config()
        logger.info("Configuration validated successfully")
        
        # Initialize and run bot
        bot = TradingBot()
        
        # Run bot with 5-minute check interval
        # This aligns well with 15-minute candles
        bot.run(check_interval=300)
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
