"""
Portfolio Manager
=================
Track trades. Calculate P&L. Win.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Position:
    symbol: str
    shares: int
    purchase_price: float
    purchase_date: str
    
@dataclass
class Transaction:
    symbol: str
    action: str  # BUY or SELL
    shares: int
    price: float
    date: str
    
class PortfolioManager:
    def __init__(self, initial_cash: float = 100000.0):
        self.portfolio_file = "portfolio.json"
        self.cash: float = initial_cash
        self.positions: Dict[str, Position] = {}
        self.transactions: List[Transaction] = []
        
        self._load_portfolio()
        
    def _load_portfolio(self):
        """Load portfolio from file"""
        try:
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
                self.cash = data.get('cash', 100000.0)
                self.positions = {}
                for symbol, pos_data in data.get('positions', {}).items():
                    self.positions[symbol] = Position(**pos_data)
                self.transactions = []
                for trans_data in data.get('transactions', []):
                    self.transactions.append(Transaction(**trans_data))
        except FileNotFoundError:
            # Create default portfolio
            self._save_portfolio()
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            
    def _save_portfolio(self):
        """Save portfolio to file"""
        try:
            data = {
                'cash': self.cash,
                'positions': {symbol: asdict(pos) for symbol, pos in self.positions.items()},
                'transactions': [asdict(trans) for trans in self.transactions],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.portfolio_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving portfolio: {e}")
            
    def buy_stock(self, symbol: str, shares: int, price: float) -> bool:
        """Execute a buy order"""
        total_cost = shares * price
        
        if total_cost > self.cash:
            return False  # Not enough cash
            
        # Update cash
        self.cash -= total_cost
        
        # Update or create position
        if symbol in self.positions:
            # Average up/down
            pos = self.positions[symbol]
            total_shares = pos.shares + shares
            avg_price = ((pos.shares * pos.purchase_price) + (shares * price)) / total_shares
            self.positions[symbol] = Position(
                symbol=symbol,
                shares=total_shares,
                purchase_price=avg_price,
                purchase_date=datetime.now().strftime('%Y-%m-%d')
            )
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                shares=shares,
                purchase_price=price,
                purchase_date=datetime.now().strftime('%Y-%m-%d')
            )
            
        # Record transaction
        self.transactions.append(Transaction(
            symbol=symbol,
            action='BUY',
            shares=shares,
            price=price,
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        self._save_portfolio()
        return True
        
    def sell_stock(self, symbol: str, shares: int, price: float) -> bool:
        """Execute a sell order"""
        if symbol not in self.positions:
            return False
            
        pos = self.positions[symbol]
        if shares > pos.shares:
            return False  # Not enough shares
            
        # Update cash
        self.cash += shares * price
        
        # Update position
        if shares == pos.shares:
            # Sold entire position
            del self.positions[symbol]
        else:
            pos.shares -= shares
            
        # Record transaction
        self.transactions.append(Transaction(
            symbol=symbol,
            action='SELL',
            shares=shares,
            price=price,
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        self._save_portfolio()
        return True
        
    def get_portfolio_value(self, market_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        stock_value = sum(
            pos.shares * market_prices.get(symbol, pos.purchase_price)
            for symbol, pos in self.positions.items()
        )
        return self.cash + stock_value
        
    def get_position_pnl(self, symbol: str, current_price: float) -> Dict[str, float]:
        """Calculate P&L for a position"""
        if symbol not in self.positions:
            return {'value': 0, 'pnl': 0, 'pnl_percent': 0}
            
        pos = self.positions[symbol]
        current_value = pos.shares * current_price
        cost_basis = pos.shares * pos.purchase_price
        pnl = current_value - cost_basis
        pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
        
        return {
            'shares': pos.shares,
            'avg_price': pos.purchase_price,
            'current_price': current_price,
            'value': current_value,
            'cost': cost_basis,
            'pnl': pnl,
            'pnl_percent': pnl_percent
        }
        
    def get_portfolio_summary(self, market_prices: Dict[str, float]) -> Dict:
        """Get complete portfolio summary"""
        positions_data = {}
        total_stock_value = 0
        total_pnl = 0
        
        for symbol, pos in self.positions.items():
            current_price = market_prices.get(symbol, pos.purchase_price)
            pos_data = self.get_position_pnl(symbol, current_price)
            positions_data[symbol] = pos_data
            total_stock_value += pos_data['value']
            total_pnl += pos_data['pnl']
            
        total_value = self.cash + total_stock_value
        
        return {
            'cash': self.cash,
            'stock_value': total_stock_value,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_percent': (total_pnl / 100000) * 100,  # Against initial capital
            'positions': positions_data,
            'transaction_count': len(self.transactions)
        }