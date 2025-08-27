"""
Stock Data Fetcher
==================
Fast. Reliable. No bloat.
"""

import aiohttp
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
import os
from dataclasses import dataclass
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cache_manager import CacheManager

@dataclass
class MarketData:
    symbol: str
    price: float
    change_percent: float
    volume: int
    high: float
    low: float
    timestamp: datetime

class DataFetcher:
    """Lean and mean data fetching"""
    
    def __init__(self):
        # Free tier APIs with good limits
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', '')
        self.polygon_key = os.getenv('POLYGON_API_KEY', '')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY', '')
        
        self.base_urls = {
            'finnhub': 'https://finnhub.io/api/v1',
            'polygon': 'https://api.polygon.io',
            'alpha_vantage': 'https://www.alphavantage.co/query'
        }
        
        # Initialize cache manager
        self.cache = CacheManager(cache_dir="cache", ttl_hours=4)
        
    async def fetch_quote(self, symbol: str) -> Optional[MarketData]:
        """Get real-time quote. Fast."""
        # Try Finnhub first (best free tier)
        if self.finnhub_key:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.base_urls['finnhub']}/quote"
                    params = {'symbol': symbol, 'token': self.finnhub_key}
                    
                    async with session.get(url, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return MarketData(
                                symbol=symbol,
                                price=data['c'],  # current price
                                change_percent=data['dp'],  # percent change
                                volume=data.get('v', 0),
                                high=data['h'],
                                low=data['l'],
                                timestamp=datetime.fromtimestamp(data['t'])
                            )
            except Exception as e:
                pass  # Fail silently, try next source
                
        # Fallback to Polygon
        if self.polygon_key:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.base_urls['polygon']}/v2/aggs/ticker/{symbol}/prev"
                    params = {'apiKey': self.polygon_key}
                    
                    async with session.get(url, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data['status'] == 'OK' and data['results']:
                                result = data['results'][0]
                                return MarketData(
                                    symbol=symbol,
                                    price=result['c'],
                                    change_percent=((result['c'] - result['o']) / result['o']) * 100,
                                    volume=result['v'],
                                    high=result['h'],
                                    low=result['l'],
                                    timestamp=datetime.fromtimestamp(result['t'] / 1000)
                                )
            except:
                pass
                
        return None
        
    async def fetch_batch(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Fetch multiple symbols efficiently"""
        tasks = [self.fetch_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        return {
            symbol: data 
            for symbol, data in zip(symbols, results) 
            if data is not None
        }
        
    async def fetch_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """Get market-moving news. Fast."""
        news = []
        
        if self.finnhub_key:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.base_urls['finnhub']}/company-news"
                    today = datetime.now().strftime('%Y-%m-%d')
                    params = {
                        'symbol': symbol,
                        'from': today,
                        'to': today,
                        'token': self.finnhub_key
                    }
                    
                    async with session.get(url, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            news = data[:limit]
            except:
                pass
                
        return news
                
    async def fetch_historical_prices(self, symbol: str, days: int = 100) -> List[float]:
        """Fetch historical daily closing prices with caching"""
        from datetime import timedelta
        
        # Check cache first
        cached_prices = self.cache.get_historical_prices(symbol)
        if cached_prices:
            return cached_prices
            
        prices = []
        
        # Try Finnhub candle data
        if self.finnhub_key:
            try:
                async with aiohttp.ClientSession() as session:
                    # Calculate timestamps
                    to_ts = int(datetime.now().timestamp())
                    from_ts = to_ts - (days * 24 * 60 * 60)
                    
                    url = f"{self.base_urls['finnhub']}/stock/candle"
                    params = {
                        'symbol': symbol,
                        'resolution': 'D',  # Daily
                        'from': from_ts,
                        'to': to_ts,
                        'token': self.finnhub_key
                    }
                    
                    async with session.get(url, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get('s') == 'ok' and 'c' in data:
                                prices = data['c']  # Closing prices
                                return prices
            except:
                pass
                
        # Try Polygon
        if self.polygon_key and not prices:
            try:
                async with aiohttp.ClientSession() as session:
                    # Get aggregates for the last 100 days
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                    
                    url = f"{self.base_urls['polygon']}/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
                    params = {'apiKey': self.polygon_key}
                    
                    async with session.get(url, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data['status'] == 'OK' and 'results' in data:
                                prices = [bar['c'] for bar in data['results']]
                                return prices
            except:
                pass
                
        # Try Alpha Vantage
        if self.alpha_vantage_key and not prices:
            try:
                async with aiohttp.ClientSession() as session:
                    url = self.base_urls['alpha_vantage']
                    params = {
                        'function': 'TIME_SERIES_DAILY',
                        'symbol': symbol,
                        'apikey': self.alpha_vantage_key,
                        'outputsize': 'compact'  # Last 100 days
                    }
                    
                    async with session.get(url, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if 'Time Series (Daily)' in data:
                                time_series = data['Time Series (Daily)']
                                # Extract closing prices in chronological order
                                dates = sorted(time_series.keys())
                                prices = [float(time_series[date]['4. close']) for date in dates]
                                return prices
            except:
                pass
                
        # Cache successful results
        if prices:
            self.cache.set_historical_prices(symbol, prices)
            
        return prices