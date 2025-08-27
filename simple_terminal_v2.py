#!/usr/bin/env python3
"""
WALL STREET TERMINAL v2.0
========================
Professional. Fast. Reliable.
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()

# Load environment variables
load_dotenv()

from data_fetcher import DataFetcher, MarketData
from ai_analyzer import StockAnalyzer
from portfolio_manager import PortfolioManager
from market_screener import MarketScreener

# Color scheme for that 80s terminal feel
class Colors:
    HEADER = Fore.CYAN
    PROFIT = Fore.GREEN
    LOSS = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.CYAN
    RESET = Style.RESET_ALL
    BRIGHT = Style.BRIGHT

class ProfessionalTerminal:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.analyzer = StockAnalyzer()
        self.portfolio = PortfolioManager()
        self.screener = MarketScreener(self.fetcher, self.analyzer)
        self.watchlist: List[str] = []
        self.market_data: Dict[str, MarketData] = {}
        self.predictions: Dict[str, Dict] = {}
        self.news_cache: Dict[str, List] = {}
        self.alerts: List[str] = []
        
        # Background monitoring
        self.monitoring_task = None
        self.last_update = time.time()
        self.update_interval = 60  # seconds
        
        # File paths
        self.watchlist_file = "watchlist.json"
        
        # Load saved data
        self._load_watchlist()
        
    def _load_watchlist(self):
        """Load watchlist from file"""
        try:
            with open(self.watchlist_file, 'r') as f:
                data = json.load(f)
                self.watchlist = data.get('symbols', [])
                print(f"{Colors.INFO}Loaded {len(self.watchlist)} stocks from watchlist{Colors.RESET}")
                time.sleep(0.5)
        except FileNotFoundError:
            self.watchlist = []
        except Exception as e:
            print(f"{Colors.WARNING}Error loading watchlist: {e}{Colors.RESET}")
            self.watchlist = []
            
    def _save_watchlist(self):
        """Save watchlist to file"""
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump({'symbols': self.watchlist}, f, indent=2)
        except Exception as e:
            print(f"{Colors.WARNING}Error saving watchlist: {e}{Colors.RESET}")
            
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_header(self):
        print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BRIGHT}  WALL STREET TERMINAL  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
        
    def display_watchlist(self):
        if not self.watchlist:
            print(f"\n{Colors.WARNING}NO STOCKS IN WATCHLIST. PRESS 'A' TO ADD.{Colors.RESET}\n")
            return
            
        # Header
        print(f"\n{Colors.BRIGHT}{'#':<3} {'SYMBOL':<10} {'PRICE':<12} {'CHANGE':<10} {'VOLUME':<15} {'SIGNAL':<8} {'RISK':<5}{Colors.RESET}")
        print(f"{Colors.INFO}{'-' * 80}{Colors.RESET}")
        
        for i, symbol in enumerate(self.watchlist[:9], 1):
            data = self.market_data.get(symbol)
            pred = self.predictions.get(symbol, {})
            
            if not data:
                print(f"{i:<3} {symbol:<10} {Colors.INFO}{'LOADING...':<12}{Colors.RESET}")
                continue
                
            # Price color based on change
            change_color = Colors.PROFIT if data.change_percent >= 0 else Colors.LOSS
            change_str = f"{data.change_percent:+.2f}%"
            
            # Signal color
            signal = pred.get('signal', '---')
            signal_color = Colors.PROFIT if signal == 'BUY' else Colors.LOSS if signal == 'SELL' else Colors.INFO
            
            # Risk color
            risk = pred.get('risk_score', 0)
            risk_color = Colors.PROFIT if risk < 3 else Colors.WARNING if risk < 7 else Colors.LOSS
            
            print(f"{i:<3} {symbol:<10} ${data.price:<11.2f} {change_color}{change_str:<10}{Colors.RESET} {data.volume:<15,} {signal_color}{Colors.BRIGHT}{signal:<8}{Colors.RESET} {risk_color}{risk:<5.1f}{Colors.RESET}")
            
    def display_commands(self):
        # Show alerts if any
        if self.alerts:
            print(f"\n{Colors.WARNING}{'=' * 80}{Colors.RESET}")
            print(f"{Colors.WARNING}ALERTS:{Colors.RESET}")
            for alert in self.alerts[-3:]:  # Show last 3 alerts
                print(f"{Colors.WARNING}{alert}{Colors.RESET}")
                
        # Show last update time
        time_since_update = time.time() - self.last_update
        print(f"\n{Colors.INFO}{'-' * 80}{Colors.RESET}")
        print(f"{Colors.INFO}Last update: {int(time_since_update)}s ago | Auto-update: {'ON' if self.monitoring_task else 'OFF'}{Colors.RESET}")
        print(f"{Colors.BRIGHT}[A]DD  [R]EMOVE  [U]PDATE  [K]SCREEN  [1-9]DETAIL  [P]ORTFOLIO  [B]UY  [S]ELL  [Q]UIT{Colors.RESET}")
        
    async def fetch_historical_data(self, symbol: str) -> List[float]:
        """Fetch real historical data"""
        # Use the new fetch_historical_prices method
        prices = await self.fetcher.fetch_historical_prices(symbol)
        
        # Return empty list if no real data available
        # Better to show "DATA N/A" than misleading analysis
        return prices if prices else []
        
    async def update_data(self):
        if not self.watchlist:
            return
            
        print(f"\n{Colors.INFO}UPDATING DATA...{Colors.RESET}")
        
        # Fetch market data
        self.market_data = await self.fetcher.fetch_batch(self.watchlist)
        
        # Run AI analysis
        for symbol, data in self.market_data.items():
            if data:
                # Fetch real historical data
                prices = await self.fetch_historical_data(symbol)
                
                if not prices:
                    # No historical data available - skip analysis
                    self.predictions[symbol] = {
                        'signal': 'N/A',
                        'confidence': 0,
                        'reason': 'No historical data available',
                        'risk_score': 0,
                        'technicals': {}
                    }
                    continue
                
                # Technical analysis
                technicals = self.analyzer.quick_technicals(prices)
                
                # Fetch and cache news
                if symbol not in self.news_cache:
                    self.news_cache[symbol] = await self.fetcher.fetch_news(symbol, limit=5)
                
                # Get portfolio summary for AI context
                market_prices = {s: d.price for s, d in self.market_data.items()}
                portfolio_summary = self.portfolio.get_portfolio_summary(market_prices)
                
                # AI prediction with portfolio awareness
                prediction = await self.analyzer.ai_predict(
                    symbol, technicals, self.news_cache[symbol], portfolio_summary
                )
                
                # Risk calculation
                risk_metrics = self.analyzer.calculate_risk(
                    data.price, data.high, data.low, data.volume
                )
                
                self.predictions[symbol] = {
                    **prediction,
                    **risk_metrics,
                    'technicals': technicals
                }
                
        # Check for alerts
        self._check_alerts()
        
        print(f"{Colors.PROFIT}DATA UPDATED SUCCESSFULLY{Colors.RESET}")
        self.last_update = time.time()
        time.sleep(0.5)
        
    def _check_alerts(self):
        """Check for alert conditions and add to alerts list"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        for symbol, data in self.market_data.items():
            pred = self.predictions.get(symbol, {})
            
            # Check RSI alerts
            rsi = pred.get('technicals', {}).get('rsi', 50)
            if rsi < 30 and rsi > 0:
                self.alerts.append(f"[{timestamp}] {symbol} OVERSOLD: RSI={rsi:.1f}")
            elif rsi > 70:
                self.alerts.append(f"[{timestamp}] {symbol} OVERBOUGHT: RSI={rsi:.1f}")
                
            # Check stop loss alerts for positions
            if symbol in self.portfolio.positions:
                pos = self.portfolio.positions[symbol]
                if data.price < pred.get('stop_loss', 0):
                    self.alerts.append(f"[{timestamp}] {symbol} STOP LOSS HIT: ${data.price:.2f}")
                    
            # Check for strong signals
            signal = pred.get('signal', '')
            confidence = pred.get('confidence', 0)
            if signal == 'BUY' and confidence > 0.8:
                self.alerts.append(f"[{timestamp}] {symbol} STRONG BUY SIGNAL")
            elif signal == 'SELL' and confidence > 0.8:
                self.alerts.append(f"[{timestamp}] {symbol} STRONG SELL SIGNAL")
                
        # Keep only last 20 alerts
        self.alerts = self.alerts[-20:]
        
    async def background_monitor(self):
        """Background task for automatic updates"""
        while True:
            try:
                await asyncio.sleep(self.update_interval)
                
                if self.watchlist:
                    # Update data silently
                    self.market_data = await self.fetcher.fetch_batch(self.watchlist)
                    
                    # Quick analysis for alerts only
                    for symbol, data in self.market_data.items():
                        if data:
                            prices = await self.fetcher.fetch_historical_prices(symbol)
                            if prices:
                                technicals = self.analyzer.quick_technicals(prices)
                                self.predictions[symbol] = {
                                    **self.predictions.get(symbol, {}),
                                    'technicals': technicals
                                }
                                
                    self._check_alerts()
                    
            except asyncio.CancelledError:
                break
            except Exception:
                pass
        
    def view_detail(self, index: int):
        if index >= len(self.watchlist):
            return
            
        symbol = self.watchlist[index]
        data = self.market_data.get(symbol)
        pred = self.predictions.get(symbol, {})
        news = self.news_cache.get(symbol, [])
        
        self.clear_screen()
        print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BRIGHT}  STOCK ANALYSIS: {symbol}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
        
        if not data:
            print(f"\n{Colors.WARNING}NO DATA AVAILABLE{Colors.RESET}")
            input("\nPress Enter to continue...")
            return
            
        # Price information
        change_color = Colors.PROFIT if data.change_percent >= 0 else Colors.LOSS
        print(f"\n{Colors.BRIGHT}MARKET DATA{Colors.RESET}")
        print(f"Price: ${data.price:.2f}")
        print(f"Change: {change_color}{data.change_percent:+.2f}%{Colors.RESET}")
        print(f"Day Range: ${data.low:.2f} - ${data.high:.2f}")
        print(f"Volume: {data.volume:,}")
        
        # AI Analysis
        print(f"\n{Colors.BRIGHT}AI ANALYSIS{Colors.RESET}")
        signal = pred.get('signal', 'CALCULATING...')
        signal_color = Colors.PROFIT if signal == 'BUY' else Colors.LOSS if signal == 'SELL' else Colors.INFO
        print(f"Recommendation: {signal_color}{Colors.BRIGHT}{signal}{Colors.RESET}")
        print(f"Confidence: {pred.get('confidence', 0) * 100:.0f}%")
        print(f"Reasoning: {pred.get('reason', 'Analyzing...')}")
        
        # Technical Indicators
        tech = pred.get('technicals', {})
        if tech:
            print(f"\n{Colors.BRIGHT}TECHNICAL INDICATORS{Colors.RESET}")
            rsi = tech.get('rsi', 0)
            rsi_color = Colors.LOSS if rsi > 70 else Colors.PROFIT if rsi < 30 else Colors.INFO
            print(f"RSI: {rsi_color}{rsi:.1f}{Colors.RESET}")
            print(f"5-Day MA: ${tech.get('sma_5', 0):.2f}")
            print(f"20-Day MA: ${tech.get('sma_20', 0):.2f}")
            trend = tech.get('trend', 'UNKNOWN')
            trend_color = Colors.PROFIT if trend == 'UP' else Colors.LOSS
            print(f"Trend: {trend_color}{trend}{Colors.RESET}")
            print(f"Momentum: {tech.get('momentum', 0):.2f}%")
            
        # Risk Management
        if 'stop_loss' in pred:
            print(f"\n{Colors.BRIGHT}RISK MANAGEMENT{Colors.RESET}")
            print(f"Stop Loss: {Colors.LOSS}${pred['stop_loss']:.2f}{Colors.RESET}")
            print(f"Take Profit: {Colors.PROFIT}${pred['take_profit']:.2f}{Colors.RESET}")
            print(f"Volatility: {pred.get('volatility', 0):.2f}%")
            
        # Recent News
        if news:
            print(f"\n{Colors.BRIGHT}RECENT NEWS{Colors.RESET}")
            for i, article in enumerate(news[:3], 1):
                print(f"{i}. {article.get('headline', 'No headline')[:70]}...")
                
        input(f"\n{Colors.INFO}Press Enter to continue...{Colors.RESET}")
        
    def remove_stock(self):
        if not self.watchlist:
            print(f"{Colors.WARNING}No stocks to remove{Colors.RESET}")
            return
            
        print(f"\n{Colors.BRIGHT}Current watchlist:{Colors.RESET}")
        for i, symbol in enumerate(self.watchlist, 1):
            print(f"{i}. {symbol}")
            
        try:
            choice = input(f"\n{Colors.INFO}Enter number to remove (or 0 to cancel): {Colors.RESET}")
            idx = int(choice) - 1
            if 0 <= idx < len(self.watchlist):
                removed = self.watchlist.pop(idx)
                self._save_watchlist()
                # Clear cached data
                self.market_data.pop(removed, None)
                self.predictions.pop(removed, None)
                self.news_cache.pop(removed, None)
                print(f"{Colors.PROFIT}Removed {removed} from watchlist{Colors.RESET}")
            elif int(choice) != 0:
                print(f"{Colors.WARNING}Invalid selection{Colors.RESET}")
        except ValueError:
            print(f"{Colors.WARNING}Invalid input{Colors.RESET}")
            
        time.sleep(1)
        
    def run(self):
        print(f"{Colors.HEADER}{Colors.BRIGHT}")
        print("WALL STREET TERMINAL v2.0")
        print("========================")
        print(f"Professional Trading Assistant{Colors.RESET}")
        time.sleep(1)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initial data load if watchlist exists
        if self.watchlist:
            print(f"\n{Colors.INFO}Loading market data...{Colors.RESET}")
            loop.run_until_complete(self.update_data())
            
        # Start background monitoring
        self.monitoring_task = loop.create_task(self.background_monitor())
        
        while True:
            self.clear_screen()
            self.display_header()
            self.display_watchlist()
            self.display_commands()
            
            command = input(f"\n{Colors.BRIGHT}> {Colors.RESET}").upper().strip()
            
            if command == 'Q':
                print(f"\n{Colors.INFO}Saving data...{Colors.RESET}")
                self._save_watchlist()
                # Cancel background monitoring
                if self.monitoring_task:
                    self.monitoring_task.cancel()
                print(f"{Colors.PROFIT}GOODBYE{Colors.RESET}")
                break
            elif command == 'A':
                symbol = input(f"\n{Colors.INFO}Enter symbol: {Colors.RESET}").upper().strip()
                if symbol and len(symbol) <= 6 and symbol not in self.watchlist:
                    self.watchlist.append(symbol)
                    self._save_watchlist()
                    print(f"{Colors.PROFIT}Added {symbol} to watchlist{Colors.RESET}")
                    loop.run_until_complete(self.update_data())
                else:
                    print(f"{Colors.WARNING}Invalid symbol or already in list{Colors.RESET}")
                    time.sleep(1)
            elif command == 'R':
                self.remove_stock()
            elif command == 'U':
                loop.run_until_complete(self.update_data())
            elif command.isdigit() and 1 <= int(command) <= 9:
                self.view_detail(int(command) - 1)
            elif command == 'P':
                self.view_portfolio()
            elif command == 'B':
                self.execute_buy()
            elif command == 'S':
                self.execute_sell()
            elif command == 'K':
                loop.run_until_complete(self.run_screener())
            
    def view_portfolio(self):
        """Display portfolio view"""
        self.clear_screen()
        print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BRIGHT}  PORTFOLIO SUMMARY{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
        
        # Get market prices
        market_prices = {symbol: data.price for symbol, data in self.market_data.items()}
        summary = self.portfolio.get_portfolio_summary(market_prices)
        
        # Overall summary
        pnl_color = Colors.PROFIT if summary['total_pnl'] >= 0 else Colors.LOSS
        print(f"\n{Colors.BRIGHT}ACCOUNT VALUE{Colors.RESET}")
        print(f"Cash: ${summary['cash']:,.2f}")
        print(f"Stock Value: ${summary['stock_value']:,.2f}")
        print(f"Total Value: ${summary['total_value']:,.2f}")
        print(f"Total P&L: {pnl_color}${summary['total_pnl']:,.2f} ({summary['total_pnl_percent']:+.2f}%){Colors.RESET}")
        print(f"Transactions: {summary['transaction_count']}")
        
        # Positions
        if summary['positions']:
            print(f"\n{Colors.BRIGHT}POSITIONS{Colors.RESET}")
            print(f"{'SYMBOL':<10} {'SHARES':<10} {'AVG COST':<10} {'CURRENT':<10} {'VALUE':<12} {'P&L':<12} {'%':<8}")
            print(f"{Colors.INFO}{'-' * 80}{Colors.RESET}")
            
            for symbol, pos in summary['positions'].items():
                pnl_color = Colors.PROFIT if pos['pnl'] >= 0 else Colors.LOSS
                print(f"{symbol:<10} {pos['shares']:<10} ${pos['avg_price']:<9.2f} ${pos['current_price']:<9.2f} ${pos['value']:<11,.2f} {pnl_color}${pos['pnl']:<11,.2f} {pos['pnl_percent']:+7.2f}%{Colors.RESET}")
                
        input(f"\n{Colors.INFO}Press Enter to continue...{Colors.RESET}")
        
    def execute_buy(self):
        """Execute a buy order"""
        print(f"\n{Colors.BRIGHT}BUY STOCK{Colors.RESET}")
        print(f"Cash Available: ${self.portfolio.cash:,.2f}")
        
        symbol = input(f"{Colors.INFO}Symbol: {Colors.RESET}").upper().strip()
        if symbol not in self.watchlist:
            print(f"{Colors.WARNING}Symbol not in watchlist. Add it first.{Colors.RESET}")
            time.sleep(1)
            return
            
        data = self.market_data.get(symbol)
        if not data:
            print(f"{Colors.WARNING}No market data available{Colors.RESET}")
            time.sleep(1)
            return
            
        print(f"Current Price: ${data.price:.2f}")
        
        try:
            shares = int(input(f"{Colors.INFO}Shares to buy: {Colors.RESET}"))
            total_cost = shares * data.price
            
            print(f"\n{Colors.BRIGHT}ORDER SUMMARY{Colors.RESET}")
            print(f"{shares} shares of {symbol} @ ${data.price:.2f}")
            print(f"Total Cost: ${total_cost:,.2f}")
            
            confirm = input(f"\n{Colors.WARNING}Confirm order? (Y/N): {Colors.RESET}").upper()
            if confirm == 'Y':
                if self.portfolio.buy_stock(symbol, shares, data.price):
                    print(f"{Colors.PROFIT}ORDER EXECUTED!{Colors.RESET}")
                    print(f"Bought {shares} shares of {symbol} @ ${data.price:.2f}")
                else:
                    print(f"{Colors.LOSS}ORDER FAILED! Insufficient funds.{Colors.RESET}")
            else:
                print(f"{Colors.INFO}Order cancelled{Colors.RESET}")
                
        except ValueError:
            print(f"{Colors.WARNING}Invalid input{Colors.RESET}")
            
        time.sleep(2)
        
    def execute_sell(self):
        """Execute a sell order"""
        if not self.portfolio.positions:
            print(f"{Colors.WARNING}No positions to sell{Colors.RESET}")
            time.sleep(1)
            return
            
        print(f"\n{Colors.BRIGHT}SELL STOCK{Colors.RESET}")
        print(f"\n{Colors.BRIGHT}Current Positions:{Colors.RESET}")
        
        for i, (symbol, pos) in enumerate(self.portfolio.positions.items(), 1):
            print(f"{i}. {symbol}: {pos.shares} shares @ ${pos.purchase_price:.2f}")
            
        try:
            choice = input(f"\n{Colors.INFO}Select position (number): {Colors.RESET}")
            idx = int(choice) - 1
            symbols = list(self.portfolio.positions.keys())
            
            if 0 <= idx < len(symbols):
                symbol = symbols[idx]
                pos = self.portfolio.positions[symbol]
                data = self.market_data.get(symbol)
                
                if not data:
                    print(f"{Colors.WARNING}No current market data{Colors.RESET}")
                    time.sleep(1)
                    return
                    
                print(f"\nSelling {symbol}")
                print(f"Current Price: ${data.price:.2f}")
                print(f"You own: {pos.shares} shares")
                
                shares = int(input(f"{Colors.INFO}Shares to sell: {Colors.RESET}"))
                
                if shares > pos.shares:
                    print(f"{Colors.WARNING}You don't own that many shares{Colors.RESET}")
                    time.sleep(1)
                    return
                    
                proceeds = shares * data.price
                pnl = (data.price - pos.purchase_price) * shares
                pnl_color = Colors.PROFIT if pnl >= 0 else Colors.LOSS
                
                print(f"\n{Colors.BRIGHT}ORDER SUMMARY{Colors.RESET}")
                print(f"Sell {shares} shares of {symbol} @ ${data.price:.2f}")
                print(f"Proceeds: ${proceeds:,.2f}")
                print(f"P&L: {pnl_color}${pnl:,.2f}{Colors.RESET}")
                
                confirm = input(f"\n{Colors.WARNING}Confirm order? (Y/N): {Colors.RESET}").upper()
                if confirm == 'Y':
                    if self.portfolio.sell_stock(symbol, shares, data.price):
                        print(f"{Colors.PROFIT}ORDER EXECUTED!{Colors.RESET}")
                        print(f"Sold {shares} shares of {symbol} @ ${data.price:.2f}")
                    else:
                        print(f"{Colors.LOSS}ORDER FAILED!{Colors.RESET}")
                else:
                    print(f"{Colors.INFO}Order cancelled{Colors.RESET}")
                    
        except (ValueError, IndexError):
            print(f"{Colors.WARNING}Invalid selection{Colors.RESET}")
            
        time.sleep(2)
        
    async def run_screener(self):
        """Run market screener"""
        self.clear_screen()
        print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BRIGHT}  MARKET SCREENER{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT}Select screening strategy:{Colors.RESET}")
        print("1. Oversold (RSI < 30)")
        print("2. Momentum Plays (Uptrend + High Momentum)")
        print("3. Volume Breakouts")
        print("4. Custom Criteria")
        print("0. Cancel")
        
        choice = input(f"\n{Colors.INFO}Choice: {Colors.RESET}").strip()
        
        if choice == '0':
            return
            
        print(f"\n{Colors.INFO}Scanning market... This may take 30-60 seconds...{Colors.RESET}")
        
        try:
            if choice == '1':
                results = await self.screener.screen_oversold()
                title = "OVERSOLD STOCKS"
            elif choice == '2':
                results = await self.screener.screen_momentum()
                title = "MOMENTUM PLAYS"
            elif choice == '3':
                results = await self.screener.screen_breakout()
                title = "VOLUME BREAKOUTS"
            else:
                print(f"{Colors.WARNING}Invalid choice{Colors.RESET}")
                time.sleep(1)
                return
                
            # Display results
            self.clear_screen()
            print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
            print(f"{Colors.HEADER}{Colors.BRIGHT}  {title}{Colors.RESET}")
            print(f"{Colors.HEADER}{Colors.BRIGHT}{'=' * 80}{Colors.RESET}")
            
            if not results:
                print(f"\n{Colors.WARNING}No stocks found matching criteria{Colors.RESET}")
            else:
                print(f"\n{Colors.BRIGHT}Found {len(results)} stocks:{Colors.RESET}")
                print(f"\n{'SYMBOL':<10} {'PRICE':<10} {'CHANGE':<10} {'RSI':<8} {'TREND':<8} {'MOMENTUM':<10} {'SIGNAL':<8}")
                print(f"{Colors.INFO}{'-' * 80}{Colors.RESET}")
                
                for r in results[:20]:  # Top 20
                    change_color = Colors.PROFIT if r.change_percent >= 0 else Colors.LOSS
                    signal_color = Colors.PROFIT if r.signal == 'BUY' else Colors.LOSS if r.signal == 'SELL' else Colors.INFO
                    
                    print(f"{r.symbol:<10} ${r.price:<9.2f} {change_color}{r.change_percent:+.2f}%{Colors.RESET:<8} "
                          f"{r.rsi:<8.1f} {r.trend:<8} {r.momentum:<10.2f} {signal_color}{r.signal:<8}{Colors.RESET}")
                          
                print(f"\n{Colors.BRIGHT}Add to watchlist?{Colors.RESET}")
                symbols = input(f"{Colors.INFO}Enter symbols (space-separated) or press Enter to skip: {Colors.RESET}").upper().strip()
                
                if symbols:
                    for symbol in symbols.split():
                        if symbol and symbol not in self.watchlist and len(self.watchlist) < 9:
                            self.watchlist.append(symbol)
                            print(f"{Colors.PROFIT}Added {symbol}{Colors.RESET}")
                    
                    self._save_watchlist()
                    print(f"\n{Colors.INFO}Updating market data for new symbols...{Colors.RESET}")
                    await self.update_data()
                    
        except Exception as e:
            print(f"{Colors.LOSS}Error during screening: {str(e)}{Colors.RESET}")
            
        input(f"\n{Colors.INFO}Press Enter to continue...{Colors.RESET}")
                
if __name__ == "__main__":
    terminal = ProfessionalTerminal()
    terminal.run()