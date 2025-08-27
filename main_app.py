#!/usr/bin/env python3
"""
Wall Street Terminal v4.0 - Professional Trading Terminal
=========================================================
A sophisticated terminal-based stock trading application with real-time data
"""

import asyncio
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional, List, Dict, Any

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, DataTable, Static, Button, 
    Label, Input, LoadingIndicator, Placeholder
)
from textual.worker import Worker, WorkerState

from rich.text import Text
from rich.table import Table

# Import our backend modules
from data_fetcher import DataFetcher, MarketData
from portfolio_manager import PortfolioManager
from market_screener import MarketScreener
from ai_analyzer import StockAnalyzer
from visualizer import Visualizer
from cache_manager import CacheManager


class WallStreetApp(App):
    """Main application class for Wall Street Terminal."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    DataTable {
        height: 100%;
        border: solid $primary;
    }
    
    .watchlist-container {
        height: 100%;
        border: solid green;
        margin: 1;
        padding: 1;
    }
    
    .detail-panel {
        border: solid blue;
        margin: 1;
        padding: 1;
    }
    
    .status-bar {
        dock: bottom;
        height: 3;
        border: solid $secondary;
        margin: 0 1;
        padding: 0 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    .positive {
        color: green;
    }
    
    .negative {
        color: red;
    }
    
    .neutral {
        color: white;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("a", "add_stock", "Add Stock"),
        Binding("r", "remove_stock", "Remove"),
        Binding("u", "update_data", "Update"),
        Binding("p", "show_portfolio", "Portfolio"),
        Binding("k", "show_screener", "Screen"),
        Binding("v", "show_performance", "Performance"),
        Binding("b", "buy_stock", "Buy"),
        Binding("s", "sell_stock", "Sell"),
        Binding("1-9", "show_detail", "Detail", show=False),
    ]
    
    # App title
    TITLE = "Wall Street Terminal v4.0"
    SUB_TITLE = "Professional Trading Terminal"
    
    def __init__(self):
        super().__init__()
        self.data_fetcher = DataFetcher()
        self.ai_analyzer = StockAnalyzer()
        self.portfolio = PortfolioManager()
        self.screener = MarketScreener(self.data_fetcher, self.ai_analyzer)
        self.cache = CacheManager()
        
        # Load watchlist
        self.watchlist_file = Path("watchlist.json")
        self.watchlist = self._load_watchlist()
        
        # Market data storage
        self.market_data: Dict[str, Any] = {}
        
        # Update worker
        self.update_worker: Optional[Worker] = None
        
    def _load_watchlist(self) -> List[str]:
        """Load watchlist from file."""
        if self.watchlist_file.exists():
            with open(self.watchlist_file, 'r') as f:
                data = json.load(f)
                return data.get('stocks', [])
        return []
    
    def _save_watchlist(self):
        """Save watchlist to file."""
        with open(self.watchlist_file, 'w') as f:
            json.dump({'stocks': self.watchlist}, f, indent=2)
    
    def compose(self) -> ComposeResult:
        """Create the app layout."""
        yield Header()
        yield WatchlistScreen()
        yield Footer()


class WatchlistScreen(Screen):
    """Main watchlist screen."""
    
    def compose(self) -> ComposeResult:
        """Create watchlist layout."""
        with Container(classes="watchlist-container"):
            yield Label("WATCHLIST", id="watchlist-title")
            yield DataTable(id="watchlist-table")
        
        with Horizontal(classes="status-bar"):
            yield Label("Last Update: Never", id="last-update")
            yield Label("Auto-Update: ON", id="auto-update-status")
            yield LoadingIndicator(id="loading", classes="hidden")
    
    def on_mount(self) -> None:
        """Initialize the watchlist table."""
        table = self.query_one("#watchlist-table", DataTable)
        
        # Set up columns
        table.add_column("#", width=3)
        table.add_column("Symbol", width=8)
        table.add_column("Price", width=12)
        table.add_column("Change", width=12)
        table.add_column("Volume", width=15)
        table.add_column("Signal", width=10)
        table.add_column("Risk", width=8)
        
        # Add initial data
        self._refresh_watchlist()
        
        # Start auto-update
        self.set_interval(30, self._auto_update)
    
    def _refresh_watchlist(self) -> None:
        """Refresh the watchlist display."""
        app = self.app
        table = self.query_one("#watchlist-table", DataTable)
        
        # Clear existing rows
        table.clear()
        
        # Add rows for each stock
        for idx, symbol in enumerate(app.watchlist, 1):
            data = app.market_data.get(symbol, {})
            
            # Format price
            if isinstance(data, MarketData):
                price = data.price
                change = data.change_percent
            else:
                price = data.get('price', 0) if data else 0
                change = data.get('change_percent', 0) if data else 0
            
            price_str = f"${price:.2f}" if price else "Loading..."
            if change > 0:
                change_str = Text(f"+{change:.2f}%", style="green")
            elif change < 0:
                change_str = Text(f"{change:.2f}%", style="red")
            else:
                change_str = Text(f"{change:.2f}%", style="white")
            
            # Format volume
            volume = data.volume if isinstance(data, MarketData) else data.get('volume', 0) if data else 0
            if volume >= 1_000_000:
                volume_str = f"{volume/1_000_000:.1f}M"
            elif volume >= 1_000:
                volume_str = f"{volume/1_000:.0f}K"
            else:
                volume_str = str(volume) if volume else "-"
            
            # Get AI signal and risk
            signal = 'N/A'  # Will be updated later
            risk = 0  # Will be updated later
            
            # Add row
            table.add_row(
                str(idx),
                symbol,
                price_str,
                change_str,
                volume_str,
                signal,
                f"{risk:.1f}" if risk else "-"
            )
    
    @work(exclusive=True)
    async def _fetch_market_data(self) -> None:
        """Fetch market data in background."""
        app = self.app
        
        # Show loading indicator
        self.query_one("#loading").remove_class("hidden")
        
        try:
            # Fetch data for all symbols
            for symbol in app.watchlist:
                data = await app.data_fetcher.fetch_quote(symbol)
                if data:
                    app.market_data[symbol] = data
            
            # Update display
            self._refresh_watchlist()
            
            # Update last update time
            self.query_one("#last-update").update(
                f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
            )
            
        finally:
            # Hide loading indicator
            self.query_one("#loading").add_class("hidden")
    
    async def _auto_update(self) -> None:
        """Auto-update market data."""
        if not self.update_worker or self.update_worker.state == WorkerState.SUCCESS:
            self.update_worker = self._fetch_market_data()
    
    def action_update_data(self) -> None:
        """Manual data update."""
        self._fetch_market_data()


class StockDetailScreen(Screen):
    """Detailed view for a single stock."""
    
    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol
    
    def compose(self) -> ComposeResult:
        """Create detail view layout."""
        yield Header()
        
        with ScrollableContainer():
            with Container(classes="detail-panel"):
                yield Label(f"Stock Details: {self.symbol}", id="detail-title")
                yield Static(id="price-info")
                yield Static(id="market-data")
                yield Static(id="ai-analysis")
                yield Static(id="price-chart")
                
            with Horizontal():
                yield Button("Back", id="back-button")
                yield Button("Buy", id="buy-button", variant="success")
                yield Button("Sell", id="sell-button", variant="error")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Load stock details."""
        await self._load_details()
    
    @on(Button.Pressed, "#back-button")
    def handle_back(self) -> None:
        """Return to watchlist."""
        self.app.pop_screen()
    
    async def _load_details(self) -> None:
        """Load and display stock details."""
        app = self.app
        data = app.market_data.get(self.symbol, {})
        
        if not data:
            # Fetch fresh data
            data = await app.data_fetcher.fetch_quote(self.symbol)
            if data:
                app.market_data[self.symbol] = data
        
        # Update displays
        self._update_price_info(data)
        self._update_market_data(data)
        await self._update_ai_analysis()
        self._update_chart(data)
    
    def _update_price_info(self, data: Any) -> None:
        """Update price information display."""
        if isinstance(data, MarketData):
            price = data.price
            change = data.change_percent
        else:
            price = data.get('price', 0) if data else 0
            change = data.get('change_percent', 0) if data else 0
        
        price_text = f"Current Price: ${price:.2f}\n"
        if change > 0:
            price_text += f"Change: [green]+{change:.2f}%[/green]"
        elif change < 0:
            price_text += f"Change: [red]{change:.2f}%[/red]"
        else:
            price_text += f"Change: {change:.2f}%"
        
        self.query_one("#price-info").update(price_text)
    
    def _update_market_data(self, data: Any) -> None:
        """Update market data display."""
        if isinstance(data, MarketData):
            volume = data.volume
            high = data.high
            low = data.low
        else:
            volume = data.get('volume', 0) if data else 0
            high = data.get('high', 0) if data else 0
            low = data.get('low', 0) if data else 0
        
        market_text = f"""
Volume: {volume:,}
Day High: ${high:.2f}
Day Low: ${low:.2f}
        """
        self.query_one("#market-data").update(market_text.strip())
    
    async def _update_ai_analysis(self) -> None:
        """Update AI analysis display."""
        analysis = await self.app.ai_analyzer.analyze_stock(self.symbol)
        self.query_one("#ai-analysis").update(f"AI Analysis:\n{analysis}")
    
    def _update_chart(self, data: Any) -> None:
        """Update price chart."""
        # For now, just show a placeholder
        self.query_one("#price-chart").update("Price Chart: [Chart visualization coming soon]")


class PortfolioScreen(Screen):
    """Portfolio management screen."""
    
    def compose(self) -> ComposeResult:
        """Create portfolio layout."""
        yield Header()
        
        with Container():
            yield Label("PORTFOLIO", id="portfolio-title")
            yield DataTable(id="portfolio-table")
            yield Static(id="portfolio-summary")
            yield Button("Back", id="back-button")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize portfolio display."""
        self._refresh_portfolio()
    
    @on(Button.Pressed, "#back-button")
    def handle_back(self) -> None:
        """Return to watchlist."""
        self.app.pop_screen()
    
    def _refresh_portfolio(self) -> None:
        """Refresh portfolio display."""
        table = self.query_one("#portfolio-table", DataTable)
        
        # Set up columns
        table.add_column("Symbol", width=8)
        table.add_column("Shares", width=10)
        table.add_column("Avg Cost", width=12)
        table.add_column("Current", width=12)
        table.add_column("P&L", width=15)
        table.add_column("P&L %", width=10)
        
        # Load portfolio data
        positions = self.app.portfolio.get_all_positions()
        
        total_value = Decimal('0')
        total_cost = Decimal('0')
        
        for position in positions:
            symbol = position['symbol']
            shares = position['shares']
            avg_cost = position['average_price']
            
            # Get current price
            market_data = self.app.market_data.get(symbol)
            if isinstance(market_data, MarketData):
                current_price = market_data.price
            elif market_data:
                current_price = market_data.get('price', avg_cost)
            else:
                current_price = avg_cost
            
            # Calculate P&L
            cost_basis = avg_cost * shares
            current_value = current_price * shares
            pnl = current_value - cost_basis
            pnl_percent = (pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            total_value += current_value
            total_cost += cost_basis
            
            # Format P&L with color
            if pnl > 0:
                pnl_text = Text(f"+${pnl:.2f}", style="green")
                pnl_pct_text = Text(f"+{pnl_percent:.2f}%", style="green")
            elif pnl < 0:
                pnl_text = Text(f"-${abs(pnl):.2f}", style="red")
                pnl_pct_text = Text(f"{pnl_percent:.2f}%", style="red")
            else:
                pnl_text = Text(f"${pnl:.2f}", style="white")
                pnl_pct_text = Text(f"{pnl_percent:.2f}%", style="white")
            
            # Add row
            table.add_row(
                symbol,
                str(shares),
                f"${avg_cost:.2f}",
                f"${current_price:.2f}",
                pnl_text,
                pnl_pct_text
            )
        
        # Update summary
        total_pnl = total_value - total_cost
        summary_text = f"""
Portfolio Summary:
Total Value: ${total_value:.2f}
Total Cost: ${total_cost:.2f}
Total P&L: ${total_pnl:.2f} ({(total_pnl/total_cost*100) if total_cost > 0 else 0:.2f}%)
        """
        self.query_one("#portfolio-summary").update(summary_text.strip())


def main():
    """Run the Wall Street Terminal application."""
    app = WallStreetApp()
    app.run()


if __name__ == "__main__":
    main()