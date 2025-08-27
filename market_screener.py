"""
Market Screener
===============
Find opportunities. Beat the market.
"""

import asyncio
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

from data_fetcher import DataFetcher, MarketData
from ai_analyzer import StockAnalyzer

@dataclass
class ScreenResult:
    symbol: str
    price: float
    change_percent: float
    rsi: float
    trend: str
    momentum: float
    volume: int
    signal: str
    reason: str
    
class MarketScreener:
    def __init__(self, fetcher: DataFetcher, analyzer: StockAnalyzer):
        self.fetcher = fetcher
        self.analyzer = analyzer
        
        # Load screening universe
        with open('screener_list.json', 'r') as f:
            self.universe = json.load(f)
            
    async def screen_symbol(self, symbol: str) -> Optional[ScreenResult]:
        """Screen a single symbol"""
        try:
            # Fetch current quote
            data = await self.fetcher.fetch_quote(symbol)
            if not data:
                return None
                
            # Fetch historical prices (will use cache)
            prices = await self.fetcher.fetch_historical_prices(symbol)
            if not prices or len(prices) < 20:
                return None
                
            # Calculate technicals
            technicals = self.analyzer.quick_technicals(prices)
            
            # Get basic prediction
            prediction = self.analyzer._simple_predict(symbol, technicals)
            
            return ScreenResult(
                symbol=symbol,
                price=data.price,
                change_percent=data.change_percent,
                rsi=technicals.get('rsi', 50),
                trend=technicals.get('trend', 'UNKNOWN'),
                momentum=technicals.get('momentum', 0),
                volume=data.volume,
                signal=prediction.get('signal', 'HOLD'),
                reason=prediction.get('reason', '')
            )
            
        except Exception:
            return None
            
    async def screen_oversold(self, symbols: Optional[List[str]] = None) -> List[ScreenResult]:
        """Find oversold stocks (RSI < 30)"""
        if not symbols:
            symbols = self.universe['nasdaq_100'][:50]  # Top 50 for speed
            
        tasks = [self.screen_symbol(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        # Filter for oversold
        oversold = [
            r for r in results 
            if r and r.rsi < 30 and r.rsi > 0
        ]
        
        # Sort by RSI (most oversold first)
        return sorted(oversold, key=lambda x: x.rsi)
        
    async def screen_momentum(self, symbols: Optional[List[str]] = None) -> List[ScreenResult]:
        """Find momentum plays (uptrend + high momentum)"""
        if not symbols:
            symbols = self.universe['nasdaq_100'][:50]
            
        tasks = [self.screen_symbol(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        # Filter for momentum
        momentum_plays = [
            r for r in results
            if r and r.trend == 'UP' and r.momentum > 5
        ]
        
        # Sort by momentum (highest first)
        return sorted(momentum_plays, key=lambda x: x.momentum, reverse=True)
        
    async def screen_breakout(self, symbols: Optional[List[str]] = None) -> List[ScreenResult]:
        """Find potential breakouts (high volume + positive momentum)"""
        if not symbols:
            symbols = self.universe['nasdaq_100'][:50]
            
        tasks = [self.screen_symbol(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        # Calculate average volumes
        avg_volumes = {}
        for r in results:
            if r:
                avg_volumes[r.symbol] = r.volume
                
        # Filter for breakouts
        breakouts = []
        for r in results:
            if r and r.momentum > 2 and r.change_percent > 1:
                # Simple volume spike detection
                if r.volume > avg_volumes.get(r.symbol, 0) * 1.5:
                    breakouts.append(r)
                    
        # Sort by change percent
        return sorted(breakouts, key=lambda x: x.change_percent, reverse=True)
        
    async def screen_custom(self, symbols: List[str], 
                          min_rsi: float = 0, max_rsi: float = 100,
                          min_momentum: float = -100, max_momentum: float = 100,
                          trend_filter: Optional[str] = None,
                          signal_filter: Optional[str] = None) -> List[ScreenResult]:
        """Custom screening with user-defined criteria"""
        tasks = [self.screen_symbol(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        # Apply filters
        filtered = []
        for r in results:
            if not r:
                continue
                
            # RSI filter
            if r.rsi < min_rsi or r.rsi > max_rsi:
                continue
                
            # Momentum filter
            if r.momentum < min_momentum or r.momentum > max_momentum:
                continue
                
            # Trend filter
            if trend_filter and r.trend != trend_filter:
                continue
                
            # Signal filter
            if signal_filter and r.signal != signal_filter:
                continue
                
            filtered.append(r)
            
        # Sort by change percent
        return sorted(filtered, key=lambda x: x.change_percent, reverse=True)
        
    def get_sector_symbols(self, sector: str) -> List[str]:
        """Get symbols for a specific sector"""
        return self.universe['sectors'].get(sector, [])