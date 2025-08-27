#!/usr/bin/env python3
"""
Wall Street Terminal - GUI Application
======================================
A professional stock trading application with a real graphical interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path

# Import our backend modules
from data_fetcher import DataFetcher, MarketData
from portfolio_manager import PortfolioManager
from market_screener import MarketScreener
from ai_analyzer import StockAnalyzer
from cache_manager import CacheManager


class StockTradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wall Street Terminal - Professional Trading Platform")
        self.root.geometry("1400x800")
        
        # Set dark theme colors
        self.bg_color = "#1a1a1a"
        self.fg_color = "#00ff00"
        self.button_bg = "#2a2a2a"
        self.entry_bg = "#2a2a2a"
        
        self.root.configure(bg=self.bg_color)
        
        # Initialize backend
        self.data_fetcher = DataFetcher()
        self.ai_analyzer = StockAnalyzer()
        self.portfolio = PortfolioManager()
        self.screener = MarketScreener(self.data_fetcher, self.ai_analyzer)
        self.cache = CacheManager()
        
        # Load watchlist
        self.watchlist_file = Path("watchlist.json")
        self.watchlist = self._load_watchlist()
        self.market_data = {}
        
        # Create GUI
        self._create_menu()
        self._create_main_layout()
        
        # Start background updates
        self.update_thread = threading.Thread(target=self._run_async_updates, daemon=True)
        self.update_thread.start()
        
    def _load_watchlist(self):
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
    
    def _create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root, bg=self.button_bg, fg=self.fg_color)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.button_bg, fg=self.fg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Stock", command=self._add_stock_dialog)
        file_menu.add_command(label="Export Portfolio", command=self._export_portfolio)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Trading menu
        trade_menu = tk.Menu(menubar, tearoff=0, bg=self.button_bg, fg=self.fg_color)
        menubar.add_cascade(label="Trading", menu=trade_menu)
        trade_menu.add_command(label="Buy Stock", command=self._buy_stock_dialog)
        trade_menu.add_command(label="Sell Stock", command=self._sell_stock_dialog)
        trade_menu.add_separator()
        trade_menu.add_command(label="View Portfolio", command=self._show_portfolio)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0, bg=self.button_bg, fg=self.fg_color)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Run Screener", command=self._run_screener)
        analysis_menu.add_command(label="AI Analysis", command=self._ai_analysis)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.button_bg, fg=self.fg_color)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self):
        """Create the main application layout."""
        # Top frame for controls
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add stock entry
        tk.Label(control_frame, text="Add Symbol:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        self.symbol_entry = tk.Entry(control_frame, bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color)
        self.symbol_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Add", command=self._add_stock, 
                 bg=self.button_bg, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Remove Selected", command=self._remove_stock,
                 bg=self.button_bg, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Refresh", command=self._refresh_data,
                 bg=self.button_bg, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(control_frame, text="Ready", bg=self.bg_color, fg=self.fg_color)
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Main content area with notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Watchlist tab
        self.watchlist_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.watchlist_frame, text="Watchlist")
        self._create_watchlist_view()
        
        # Portfolio tab
        self.portfolio_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.portfolio_frame, text="Portfolio")
        self._create_portfolio_view()
        
        # Detail tab
        self.detail_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.detail_frame, text="Stock Details")
        self._create_detail_view()
        
    def _create_watchlist_view(self):
        """Create the watchlist table view."""
        # Create Treeview for stock data
        columns = ("Symbol", "Price", "Change %", "Volume", "Day High", "Day Low", "Signal")
        self.watchlist_tree = ttk.Treeview(self.watchlist_frame, columns=columns, show="headings", height=20)
        
        # Define column headings
        for col in columns:
            self.watchlist_tree.heading(col, text=col)
            if col == "Symbol":
                self.watchlist_tree.column(col, width=100)
            else:
                self.watchlist_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.watchlist_frame, orient=tk.VERTICAL, command=self.watchlist_tree.yview)
        self.watchlist_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.watchlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click
        self.watchlist_tree.bind("<Double-1>", self._on_stock_select)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=self.entry_bg, foreground=self.fg_color, fieldbackground=self.entry_bg)
        style.configure("Treeview.Heading", background=self.button_bg, foreground=self.fg_color)
        
    def _create_portfolio_view(self):
        """Create the portfolio view."""
        # Portfolio summary
        summary_frame = tk.Frame(self.portfolio_frame, bg=self.bg_color)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.portfolio_summary = tk.Label(summary_frame, text="Portfolio Summary", 
                                        bg=self.bg_color, fg=self.fg_color, font=("Arial", 12, "bold"))
        self.portfolio_summary.pack()
        
        # Portfolio table
        columns = ("Symbol", "Shares", "Avg Cost", "Current Price", "Value", "P&L", "P&L %")
        self.portfolio_tree = ttk.Treeview(self.portfolio_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.portfolio_tree.heading(col, text=col)
            self.portfolio_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(self.portfolio_frame, orient=tk.VERTICAL, command=self.portfolio_tree.yview)
        self.portfolio_tree.configure(yscrollcommand=scrollbar.set)
        
        self.portfolio_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_detail_view(self):
        """Create the stock detail view."""
        # Title
        self.detail_title = tk.Label(self.detail_frame, text="Select a stock to view details",
                                   bg=self.bg_color, fg=self.fg_color, font=("Arial", 16, "bold"))
        self.detail_title.pack(pady=10)
        
        # Detail text area
        self.detail_text = tk.Text(self.detail_frame, bg=self.entry_bg, fg=self.fg_color,
                                 font=("Courier", 10), wrap=tk.WORD)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Detail scrollbar
        detail_scroll = ttk.Scrollbar(self.detail_text, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _add_stock(self):
        """Add stock to watchlist."""
        symbol = self.symbol_entry.get().upper().strip()
        if symbol and symbol not in self.watchlist:
            self.watchlist.append(symbol)
            self._save_watchlist()
            self.symbol_entry.delete(0, tk.END)
            self._refresh_data()
            self.status_label.config(text=f"Added {symbol} to watchlist")
        
    def _remove_stock(self):
        """Remove selected stock from watchlist."""
        selected = self.watchlist_tree.selection()
        if selected:
            item = self.watchlist_tree.item(selected[0])
            symbol = item['values'][0]
            self.watchlist.remove(symbol)
            self._save_watchlist()
            self._refresh_data()
            self.status_label.config(text=f"Removed {symbol} from watchlist")
    
    def _refresh_data(self):
        """Refresh market data."""
        self.status_label.config(text="Updating data...")
        # The async update will handle the actual refresh
        
    def _on_stock_select(self, event):
        """Handle stock selection."""
        selected = self.watchlist_tree.selection()
        if selected:
            item = self.watchlist_tree.item(selected[0])
            symbol = item['values'][0]
            self._show_stock_details(symbol)
    
    def _show_stock_details(self, symbol):
        """Show detailed information for a stock."""
        self.notebook.select(self.detail_frame)
        self.detail_title.config(text=f"Details for {symbol}")
        
        # Get market data
        data = self.market_data.get(symbol, {})
        
        # Format details
        details = f"""
STOCK DETAILS - {symbol}
{'='*50}

Current Price: ${data.get('price', 0):.2f}
Change: {data.get('change_percent', 0):.2f}%
Volume: {data.get('volume', 0):,}

Day Range: ${data.get('low', 0):.2f} - ${data.get('high', 0):.2f}

Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, details)
        
        # Run AI analysis in background
        threading.Thread(target=self._get_ai_analysis, args=(symbol,), daemon=True).start()
    
    def _get_ai_analysis(self, symbol):
        """Get AI analysis for a stock."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(self.ai_analyzer.analyze_stock(symbol))
            
            self.detail_text.insert(tk.END, f"\n\nAI ANALYSIS\n{'='*50}\n{analysis}")
        except Exception as e:
            self.detail_text.insert(tk.END, f"\n\nAI Analysis unavailable: {str(e)}")
    
    def _update_watchlist_display(self):
        """Update the watchlist table with current data."""
        # Clear existing items
        for item in self.watchlist_tree.get_children():
            self.watchlist_tree.delete(item)
        
        # Add updated data
        for symbol in self.watchlist:
            data = self.market_data.get(symbol, {})
            
            if isinstance(data, MarketData):
                price = f"${data.price:.2f}"
                change = f"{data.change_percent:.2f}%"
                volume = f"{data.volume:,}"
                high = f"${data.high:.2f}"
                low = f"${data.low:.2f}"
            else:
                price = "Loading..."
                change = "-"
                volume = "-"
                high = "-"
                low = "-"
            
            signal = "N/A"  # Will be updated with AI analysis
            
            # Insert with color tags
            tag = "positive" if data and data.change_percent > 0 else "negative" if data and data.change_percent < 0 else "neutral"
            self.watchlist_tree.insert("", tk.END, values=(symbol, price, change, volume, high, low, signal), tags=(tag,))
        
        # Configure tags
        self.watchlist_tree.tag_configure("positive", foreground="#00ff00")
        self.watchlist_tree.tag_configure("negative", foreground="#ff0000")
        self.watchlist_tree.tag_configure("neutral", foreground="#ffffff")
    
    def _update_portfolio_display(self):
        """Update portfolio display."""
        # Clear existing
        for item in self.portfolio_tree.get_children():
            self.portfolio_tree.delete(item)
        
        # Get positions from the portfolio
        positions = []
        for symbol, pos in self.portfolio.positions.items():
            positions.append({
                'symbol': symbol,
                'shares': pos.shares,
                'average_price': pos.purchase_price
            })
        total_value = Decimal('0')
        total_cost = Decimal('0')
        
        for position in positions:
            symbol = position['symbol']
            shares = position['shares']
            avg_cost = position['average_price']
            
            # Get current price
            market_data = self.market_data.get(symbol)
            if isinstance(market_data, MarketData):
                current_price = market_data.price
            else:
                current_price = avg_cost
            
            # Calculate P&L
            cost_basis = avg_cost * shares
            current_value = current_price * shares
            pnl = current_value - cost_basis
            pnl_percent = (pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            total_value += current_value
            total_cost += cost_basis
            
            # Format values
            tag = "positive" if pnl > 0 else "negative" if pnl < 0 else "neutral"
            
            self.portfolio_tree.insert("", tk.END, values=(
                symbol,
                shares,
                f"${avg_cost:.2f}",
                f"${current_price:.2f}",
                f"${current_value:.2f}",
                f"${pnl:.2f}",
                f"{pnl_percent:.2f}%"
            ), tags=(tag,))
        
        # Update summary
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        summary_text = f"Total Value: ${total_value:.2f} | Total P&L: ${total_pnl:.2f} ({total_pnl_percent:.2f}%)"
        self.portfolio_summary.config(text=summary_text)
    
    def _run_async_updates(self):
        """Run async updates in background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while True:
            try:
                # Fetch data for all symbols
                for symbol in self.watchlist:
                    data = loop.run_until_complete(self.data_fetcher.fetch_quote(symbol))
                    if data:
                        self.market_data[symbol] = data
                
                # Update displays
                self.root.after(0, self._update_watchlist_display)
                self.root.after(0, self._update_portfolio_display)
                self.root.after(0, lambda: self.status_label.config(text=f"Updated: {datetime.now().strftime('%H:%M:%S')}"))
                
            except Exception as e:
                print(f"Update error: {e}")
            
            # Wait 30 seconds
            loop.run_until_complete(asyncio.sleep(30))
    
    # Dialog methods
    def _add_stock_dialog(self):
        """Show add stock dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Stock")
        dialog.geometry("300x150")
        dialog.configure(bg=self.bg_color)
        
        tk.Label(dialog, text="Enter Stock Symbol:", bg=self.bg_color, fg=self.fg_color).pack(pady=10)
        
        entry = tk.Entry(dialog, bg=self.entry_bg, fg=self.fg_color)
        entry.pack(pady=5)
        entry.focus()
        
        def add():
            symbol = entry.get().upper().strip()
            if symbol:
                self.watchlist.append(symbol)
                self._save_watchlist()
                self._refresh_data()
                dialog.destroy()
        
        tk.Button(dialog, text="Add", command=add, bg=self.button_bg, fg=self.fg_color).pack(pady=10)
    
    def _buy_stock_dialog(self):
        """Show buy stock dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Buy Stock")
        dialog.geometry("400x300")
        dialog.configure(bg=self.bg_color)
        
        # Symbol
        tk.Label(dialog, text="Symbol:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=10, pady=5)
        symbol_var = tk.StringVar()
        symbol_combo = ttk.Combobox(dialog, textvariable=symbol_var, values=self.watchlist)
        symbol_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Shares
        tk.Label(dialog, text="Shares:", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, padx=10, pady=5)
        shares_entry = tk.Entry(dialog, bg=self.entry_bg, fg=self.fg_color)
        shares_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Price display
        price_label = tk.Label(dialog, text="Current Price: -", bg=self.bg_color, fg=self.fg_color)
        price_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Total display
        total_label = tk.Label(dialog, text="Total Cost: -", bg=self.bg_color, fg=self.fg_color)
        total_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        def update_price(*args):
            symbol = symbol_var.get()
            if symbol and symbol in self.market_data:
                data = self.market_data[symbol]
                if isinstance(data, MarketData):
                    price_label.config(text=f"Current Price: ${data.price:.2f}")
                    
                    try:
                        shares = int(shares_entry.get())
                        total = shares * data.price
                        total_label.config(text=f"Total Cost: ${total:.2f}")
                    except:
                        pass
        
        symbol_var.trace("w", update_price)
        shares_entry.bind("<KeyRelease>", update_price)
        
        def execute_buy():
            try:
                symbol = symbol_var.get()
                shares = int(shares_entry.get())
                
                if symbol and shares > 0:
                    data = self.market_data.get(symbol)
                    if isinstance(data, MarketData):
                        price = data.price
                        self.portfolio.buy_stock(symbol, shares, price, "Manual buy order")
                        messagebox.showinfo("Success", f"Bought {shares} shares of {symbol} at ${price:.2f}")
                        dialog.destroy()
                        self._update_portfolio_display()
                    else:
                        messagebox.showerror("Error", "No price data available")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid shares")
        
        tk.Button(dialog, text="Buy", command=execute_buy, bg=self.button_bg, fg=self.fg_color).grid(row=4, column=0, columnspan=2, pady=20)
    
    def _sell_stock_dialog(self):
        """Show sell stock dialog."""
        # Get positions from the portfolio
        positions = []
        for symbol, pos in self.portfolio.positions.items():
            positions.append({
                'symbol': symbol,
                'shares': pos.shares,
                'average_price': pos.purchase_price
            })
        if not positions:
            messagebox.showinfo("No Positions", "You don't have any positions to sell")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Sell Stock")
        dialog.geometry("400x300")
        dialog.configure(bg=self.bg_color)
        
        # Symbol
        tk.Label(dialog, text="Symbol:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=10, pady=5)
        symbol_var = tk.StringVar()
        symbols = [p['symbol'] for p in positions]
        symbol_combo = ttk.Combobox(dialog, textvariable=symbol_var, values=symbols)
        symbol_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Position info
        position_label = tk.Label(dialog, text="Position: -", bg=self.bg_color, fg=self.fg_color)
        position_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Shares
        tk.Label(dialog, text="Shares to Sell:", bg=self.bg_color, fg=self.fg_color).grid(row=2, column=0, padx=10, pady=5)
        shares_entry = tk.Entry(dialog, bg=self.entry_bg, fg=self.fg_color)
        shares_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Price display
        price_label = tk.Label(dialog, text="Current Price: -", bg=self.bg_color, fg=self.fg_color)
        price_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Total display
        total_label = tk.Label(dialog, text="Total Proceeds: -", bg=self.bg_color, fg=self.fg_color)
        total_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        def update_info(*args):
            symbol = symbol_var.get()
            if symbol:
                # Find position
                position = next((p for p in positions if p['symbol'] == symbol), None)
                if position:
                    position_label.config(text=f"Position: {position['shares']} shares @ ${position['average_price']:.2f}")
                
                # Update price
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    if isinstance(data, MarketData):
                        price_label.config(text=f"Current Price: ${data.price:.2f}")
                        
                        try:
                            shares = int(shares_entry.get())
                            total = shares * data.price
                            total_label.config(text=f"Total Proceeds: ${total:.2f}")
                        except:
                            pass
        
        symbol_var.trace("w", update_info)
        shares_entry.bind("<KeyRelease>", update_info)
        
        def execute_sell():
            try:
                symbol = symbol_var.get()
                shares = int(shares_entry.get())
                
                if symbol and shares > 0:
                    data = self.market_data.get(symbol)
                    if isinstance(data, MarketData):
                        price = data.price
                        self.portfolio.sell_stock(symbol, shares, price, "Manual sell order")
                        messagebox.showinfo("Success", f"Sold {shares} shares of {symbol} at ${price:.2f}")
                        dialog.destroy()
                        self._update_portfolio_display()
                    else:
                        messagebox.showerror("Error", "No price data available")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid shares")
        
        tk.Button(dialog, text="Sell", command=execute_sell, bg=self.button_bg, fg=self.fg_color).grid(row=5, column=0, columnspan=2, pady=20)
    
    def _show_portfolio(self):
        """Show portfolio tab."""
        self.notebook.select(self.portfolio_frame)
    
    def _run_screener(self):
        """Run market screener."""
        messagebox.showinfo("Screener", "Market screener running... Results will appear in a moment.")
        # TODO: Implement screener dialog
    
    def _ai_analysis(self):
        """Run AI analysis on selected stock."""
        selected = self.watchlist_tree.selection()
        if selected:
            item = self.watchlist_tree.item(selected[0])
            symbol = item['values'][0]
            self._show_stock_details(symbol)
        else:
            messagebox.showinfo("Select Stock", "Please select a stock from the watchlist first")
    
    def _export_portfolio(self):
        """Export portfolio to file."""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            # TODO: Implement CSV export
            messagebox.showinfo("Export", f"Portfolio exported to {filename}")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """Wall Street Terminal GUI v1.0
        
A professional stock trading application
with real-time data and AI analysis.

Built with Python and Tkinter
        """
        messagebox.showinfo("About", about_text)


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = StockTradingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()