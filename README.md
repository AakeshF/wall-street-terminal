# Wall Street Terminal v4.0 🚀

A professional-grade, minimalist stock trading terminal with AI-powered analysis, real-time market screening, and portfolio management. Built for speed, accuracy, and that authentic 80s Wall Street aesthetic.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Terminal](https://img.shields.io/badge/terminal-based-orange.svg)

## Features

### 📊 Real-Time Market Data
- Multi-source data fetching (Finnhub, Polygon, Alpha Vantage)
- Intelligent caching system (4-hour TTL)
- Live price updates with volume tracking
- **NEW**: ASCII price charts with sparklines

### 🤖 AI-Powered Analysis
- Claude-powered stock predictions
- Portfolio-aware recommendations
- Technical indicators (RSI, SMA, momentum)
- Risk management with stop-loss suggestions
- **NEW**: Web search integration for real-time sentiment

### 📈 Market Screener
- Find oversold opportunities (RSI < 30)
- Discover momentum plays
- Detect volume breakouts
- Screen top NASDAQ stocks automatically
- **NEW**: Custom screening with your own criteria

### 💼 Portfolio Management
- Track positions with real-time P&L
- Execute buy/sell orders with reasoning
- Transaction history with AI insights
- Starting capital: $100,000 (for simulations)
- **NEW**: Performance metrics and win rate analysis

### ⚡ Professional Features
- Background monitoring (60-second auto-updates)
- Real-time alerts for key events
- Data persistence (watchlist saves automatically)
- Fast, colorful terminal UI
- **NEW**: Visual price trends in detail view

### 🎯 v4.0 - Standalone Terminal App
- Modern TUI with Textual framework
- Interactive DataTable for watchlist
- Mouse support and clickable elements
- Multiple screens (Detail, Portfolio, Screener)
- Runs as its own application window
- Preserves the classic 80s Wall Street aesthetic

### 🖥️ NEW: GUI Desktop Application
- Full graphical interface with windows and menus
- Real-time stock data grid with sortable columns
- Interactive portfolio management with P&L tracking
- Pop-up dialogs for trading (Buy/Sell orders)
- Tabbed interface for easy navigation
- Dark theme optimized for trading
- No console window - runs as a true desktop app

## Quick Start

### 🚀 Easiest Installation (Recommended)

1. Go to the [latest releases page](https://github.com/AakeshF/wall-street-terminal/releases)
2. Choose your preferred version:
   - `WallStreetGUI.exe` - NEW! Full GUI desktop application
   - `WallStreetTerminal_v4.exe` - Textual terminal app (keyboard + mouse)
   - `WallStreetTerminal.exe` - Classic v3 terminal (keyboard only)
3. Double-click to run - that's it!
4. Copy `.env.example` to `.env` and add your free API keys

### 💻 Developer Installation

#### Prerequisites
- Python 3.8+
- Windows Terminal or PowerShell (for best experience)

#### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wall-street-terminal.git
cd wall-street-terminal
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API keys in `.env`:
```env
# Get free API keys from:
# Finnhub: https://finnhub.io (60 calls/min)
# Polygon: https://polygon.io (5 calls/min)
# Alpha Vantage: https://alphavantage.co (5 calls/min)
# Anthropic: https://anthropic.com (for AI analysis)

FINNHUB_API_KEY=your_finnhub_key
POLYGON_API_KEY=your_polygon_key
ALPHA_VANTAGE_KEY=your_alphavantage_key
ANTHROPIC_API_KEY=your_claude_key
```

4. Run your preferred version:
```bash
# GUI Desktop Application (NEW!)
python gui_app.py

# Textual Terminal App (v4.0)
python main_app.py

# Classic Terminal (v3.0)
python simple_terminal_v2.py
# or
.\run.bat
```

## Usage

### Commands
- `A` - Add stock to watchlist
- `R` - Remove stock from watchlist
- `U` - Update all data manually
- `K` - Run market screener (with custom criteria!)
- `1-9` - View detailed analysis with price charts
- `P` - Portfolio summary
- `V` - Performance review (win rate, best/worst trades)
- `B` - Buy stocks
- `S` - Sell stocks
- `Q` - Quit

### Market Screener Strategies
1. **Oversold Stocks** - Find stocks with RSI < 30
2. **Momentum Plays** - Stocks in uptrend with high momentum
3. **Volume Breakouts** - Unusual volume with positive movement
4. **Custom Criteria** - Define your own RSI range, trend, momentum, and signals

### Example Workflow
1. Press `K` to run the screener
2. Select "Oversold Stocks"
3. Add promising symbols to your watchlist
4. Press `1` to view detailed analysis
5. Press `B` to buy if the signal is strong
6. Monitor alerts for exit signals

## Architecture

```
stock_terminal/
├── simple_terminal_v2.py    # Main terminal application
├── data_fetcher.py         # Multi-source market data fetching
├── ai_analyzer.py          # Technical analysis & AI predictions
├── portfolio_manager.py    # Portfolio tracking & transactions
├── market_screener.py      # Market scanning strategies
├── cache_manager.py        # Intelligent data caching
├── screener_list.json      # Universe of stocks to screen
└── requirements.txt        # Python dependencies
```

## Trading Strategies

### For MarketWatch Simulations
- **Diversify**: 40% large-cap tech, 20% growth, 20% ETFs, 10% high-risk, 10% cash
- **Use Screener**: Find oversold quality stocks (RSI < 30)
- **Follow Alerts**: The terminal will alert you to opportunities
- **Risk Management**: Use suggested stop-losses

### Technical Indicators
- **RSI < 30**: Potentially oversold (buy signal)
- **RSI > 70**: Potentially overbought (sell signal)
- **Trend**: UP/DOWN based on moving averages
- **Momentum**: Rate of price change

## API Rate Limits

| Provider | Free Tier Limit | Best For |
|----------|----------------|----------|
| Finnhub | 60 calls/min | Primary data source |
| Polygon | 5 calls/min | Backup & historical |
| Alpha Vantage | 5 calls/min | Additional coverage |

The terminal intelligently manages these limits with caching and fallback strategies.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Claude AI assistance
- Inspired by 1980s Wall Street terminals
- Designed for modern traders who appreciate minimalist efficiency

## Disclaimer

This tool is for educational and simulation purposes. Always do your own research before making investment decisions. Not financial advice.

---

**Ready to dominate the market? Start your terminal and let's trade!** 📈