"""
AI Stock Analyzer
=================
Smart. Fast. No fluff.
"""

import asyncio
from typing import Dict, List, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta
import anthropic
import os
import aiohttp
import json

class StockAnalyzer:
    """Lean AI-powered analysis"""
    
    def __init__(self):
        self.claude_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.client = anthropic.Anthropic(api_key=self.claude_key) if self.claude_key else None
        self.tavily_key = os.getenv('TAVILY_API_KEY', '')
        self.web_search_enabled = bool(self.tavily_key)
        
    def quick_technicals(self, prices: List[float]) -> Dict[str, float]:
        """Fast technical indicators. No libraries needed."""
        if len(prices) < 20:
            return {}
            
        # Simple Moving Averages
        sma_5 = np.mean(prices[-5:])
        sma_20 = np.mean(prices[-20:])
        
        # RSI approximation
        gains = [max(0, prices[i] - prices[i-1]) for i in range(1, len(prices))]
        losses = [max(0, prices[i-1] - prices[i]) for i in range(1, len(prices))]
        
        avg_gain = np.mean(gains[-14:]) if gains[-14:] else 0
        avg_loss = np.mean(losses[-14:]) if losses[-14:] else 0
        
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        # Momentum
        momentum = (prices[-1] / prices[-10] - 1) * 100 if len(prices) > 10 else 0
        
        return {
            'sma_5': sma_5,
            'sma_20': sma_20,
            'rsi': rsi,
            'momentum': momentum,
            'trend': 'UP' if sma_5 > sma_20 else 'DOWN'
        }
        
    async def _fetch_web_context(self, symbol: str) -> str:
        """Fetch real-time web context for a stock"""
        if not self.web_search_enabled:
            return ""
            
        try:
            query = f"latest news analyst sentiment {symbol} stock price target"
            
            async with aiohttp.ClientSession() as session:
                url = "https://api.tavily.com/search"
                headers = {"Content-Type": "application/json"}
                data = {
                    "api_key": self.tavily_key,
                    "query": query,
                    "max_results": 3,
                    "search_depth": "basic",
                    "include_answer": True
                }
                
                async with session.post(url, headers=headers, json=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        # Build concise context
                        context_parts = []
                        
                        # Add direct answer if available
                        if result.get('answer'):
                            context_parts.append(f"Summary: {result['answer'][:150]}")
                            
                        # Add top results
                        for r in result.get('results', [])[:2]:
                            title = r.get('title', '')
                            snippet = r.get('snippet', '')[:100]
                            if title and snippet:
                                context_parts.append(f"- {title}: {snippet}")
                                
                        return "\n".join(context_parts) if context_parts else ""
                        
        except Exception as e:
            # Fail silently - web search is optional enhancement
            return ""
            
        return ""
        
    async def ai_predict(self, symbol: str, data: Dict, news: List[Dict], portfolio_summary: Optional[Dict] = None) -> Dict[str, any]:
        """AI-powered prediction. Direct to the point."""
        if not self.client:
            return self._simple_predict(symbol, data)
            
        # Build concise context
        context = f"""
SYMBOL: {symbol}
PRICE: ${data.get('price', 0):.2f}
CHANGE: {data.get('change_percent', 0):.2f}%
RSI: {data.get('rsi', 50):.1f}
TREND: {data.get('trend', 'UNKNOWN')}
NEWS: {len(news)} articles today
        """
        
        # Add portfolio context if available
        if portfolio_summary:
            context += f"\nPORTFOLIO: ${portfolio_summary.get('total_value', 100000):.0f} total"
            if symbol in portfolio_summary.get('positions', {}):
                pos = portfolio_summary['positions'][symbol]
                context += f", owns {pos['shares']} shares @ ${pos['avg_price']:.2f}"
            context += f", {len(portfolio_summary.get('positions', {}))} positions"
        
        # Fetch web context for deeper insights
        web_context = await self._fetch_web_context(symbol)
        if web_context:
            context += f"\n\nWEB INSIGHTS:\n{web_context}"
        
        try:
            prompt = "Quick stock analysis. Be extremely concise.\n" + context
            if portfolio_summary:
                prompt += "\nConsider portfolio diversification."
            if web_context:
                prompt += "\nConsider recent news sentiment."
            prompt += "\nPrediction (BUY/HOLD/SELL) with 1-line reason:"
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=150,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            text = response.content[0].text.strip()
            # Parse response
            if 'BUY' in text.upper():
                signal = 'BUY'
            elif 'SELL' in text.upper():
                signal = 'SELL'
            else:
                signal = 'HOLD'
                
            return {
                'signal': signal,
                'confidence': 0.7,  # Placeholder
                'reason': text.split('\n')[0][:80]  # Keep it short
            }
            
        except Exception as e:
            return self._simple_predict(symbol, data)
            
    def _simple_predict(self, symbol: str, data: Dict) -> Dict[str, any]:
        """Fallback prediction using simple rules"""
        rsi = data.get('rsi', 50)
        momentum = data.get('momentum', 0)
        trend = data.get('trend', 'UNKNOWN')
        
        if rsi < 30 and momentum > 0:
            signal = 'BUY'
            reason = 'Oversold + positive momentum'
        elif rsi > 70 and momentum < 0:
            signal = 'SELL'
            reason = 'Overbought + negative momentum'
        elif trend == 'UP' and rsi < 50:
            signal = 'BUY'
            reason = 'Uptrend continuation'
        elif trend == 'DOWN' and rsi > 50:
            signal = 'SELL'
            reason = 'Downtrend continuation'
        else:
            signal = 'HOLD'
            reason = 'No clear signal'
            
        confidence = min(0.8, abs(rsi - 50) / 50 + abs(momentum) / 20)
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason
        }
        
    def calculate_risk(self, price: float, high: float, low: float, volume: int) -> Dict[str, float]:
        """Quick risk metrics"""
        volatility = (high - low) / price * 100 if price > 0 else 0
        
        return {
            'volatility': volatility,
            'stop_loss': price * 0.98,  # 2% stop
            'take_profit': price * 1.05,  # 5% target
            'risk_score': min(10, volatility)  # 0-10 scale
        }