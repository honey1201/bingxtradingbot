"""
BingX API Client
Handles authentication and API requests to BingX
"""

import hmac
import hashlib
import time
import json
import logging
import requests
from urllib.parse import urlencode
from config import BINGX_API_KEY, BINGX_SECRET_KEY, BINGX_BASE_URL

logger = logging.getLogger(__name__)

class BingXAPIClient:
    """Client for BingX API interactions"""
    
    def __init__(self, api_key, secret_key, base_url=BINGX_BASE_URL):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.session = requests.Session()
    
    def _generate_signature(self, params_str):
        """Generate HMAC SHA256 signature for request"""
        signature = hmac.new(
            self.secret_key.encode(),
            params_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _send_request(self, method, endpoint, params=None, is_private=False):
        """Send HTTP request to BingX API"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if is_private:
            headers['X-BingX-API-Key'] = self.api_key
            
            if params is None:
                params = {}
            
            params['timestamp'] = int(time.time() * 1000)
            params_str = urlencode(params)
            signature = self._generate_signature(params_str)
            params['signature'] = signature
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, params=params, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_klines(self, symbol, timeframe, limit=100):
        """
        Get candlestick data (klines) for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            timeframe: Timeframe (e.g., '15m', '1h')
            limit: Number of candles to fetch (default: 100)
        
        Returns:
            List of klines data
        """
        endpoint = '/openApi/spot/v1/market/klines'
        params = {
            'symbol': symbol,
            'interval': timeframe,
            'limit': limit
        }
        
        return self._send_request('GET', endpoint, params, is_private=False)
    
    def get_account_info(self):
        """Get account information"""
        endpoint = '/openApi/spot/v1/account/getBalance'
        return self._send_request('GET', endpoint, is_private=True)
    
    def get_order(self, symbol, order_id):
        """Get order details"""
        endpoint = '/openApi/spot/v1/trade/query'
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._send_request('GET', endpoint, params, is_private=True)
    
    def place_order(self, symbol, side, quantity, price=None, order_type='LIMIT'):
        """
        Place an order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            order_type: 'LIMIT' or 'MARKET'
        
        Returns:
            Order response
        """
        endpoint = '/openApi/spot/v1/trade/order'
        params = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'type': order_type
        }
        
        if price and order_type == 'LIMIT':
            params['price'] = price
        
        return self._send_request('POST', endpoint, params, is_private=True)
    
    def cancel_order(self, symbol, order_id):
        """Cancel an order"""
        endpoint = '/openApi/spot/v1/trade/cancel'
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._send_request('POST', endpoint, params, is_private=True)

# Create default client instance
api_client = BingXAPIClient(BINGX_API_KEY, BINGX_SECRET_KEY)
