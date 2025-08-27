#!/usr/bin/env python3
"""Modified version of main.py to test add stock functionality with logging"""

import sys
import curses
from datetime import datetime
from typing import Dict
from dataclasses import dataclass

@dataclass
class Stock:
    symbol: str
    price: float
    change: float
    volume: int

class TestTerminalUI:
    def __init__(self):
        self.stocks: Dict[str, Stock] = {}
        self.log_file = open("test_log.txt", "w")
        
    def log(self, message):
        self.log_file.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_file.flush()
        
    def run(self):
        try:
            curses.wrapper(self._main_loop)
        finally:
            self.log_file.close()
            
    def _main_loop(self, stdscr):
        self.log("Starting main loop")
        
        try:
            curses.curs_set(0)
            stdscr.nodelay(0)  # Make it blocking for easier testing
            
            # Color pairs
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
            
            self.log("Initialized curses settings")
            
            # Draw initial screen
            stdscr.clear()
            stdscr.addstr(0, 0, "STOCK TERMINAL TEST", curses.A_BOLD)
            stdscr.addstr(2, 0, "Press 'A' to add stock, 'Q' to quit")
            stdscr.addstr(4, 0, "Current stocks: " + str(len(self.stocks)))
            stdscr.refresh()
            
            self.log("Drew initial screen")
            
            # Wait for A key
            while True:
                key = stdscr.getch()
                self.log(f"Key pressed: {key} ('{chr(key) if 32 <= key <= 126 else 'special'}')")
                
                if key == ord('q') or key == ord('Q'):
                    self.log("Quit command received")
                    break
                elif key == ord('a') or key == ord('A'):
                    self.log("Add stock command received")
                    self._test_add_stock(stdscr)
                    
        except Exception as e:
            self.log(f"ERROR in main loop: {str(e)}")
            raise
            
    def _test_add_stock(self, stdscr):
        self.log("Entering _test_add_stock function")
        
        try:
            # Clear some space
            stdscr.addstr(6, 0, " " * 60)
            stdscr.addstr(7, 0, " " * 60)
            stdscr.addstr(8, 0, " " * 60)
            
            # Enable echo for input
            self.log("Enabling echo mode")
            curses.echo()
            
            # Show prompt
            stdscr.addstr(6, 0, "ENTER SYMBOL: ")
            stdscr.refresh()
            self.log("Displayed input prompt")
            
            # Try to get input
            try:
                self.log("Attempting to get string input...")
                symbol = stdscr.getstr(6, 14, 10).decode('utf-8').upper()
                self.log(f"Successfully captured symbol: '{symbol}'")
                
                # Disable echo
                curses.noecho()
                
                # Add the stock
                self.stocks[symbol] = Stock(symbol, 100.0, 0.0, 1000000)
                self.log(f"Added stock {symbol} to dictionary")
                
                # Show success
                stdscr.addstr(8, 0, f"Added: {symbol}", curses.color_pair(1))
                stdscr.addstr(10, 0, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
                
                # Redraw main screen
                stdscr.clear()
                stdscr.addstr(0, 0, "STOCK TERMINAL TEST", curses.A_BOLD)
                stdscr.addstr(2, 0, "Press 'A' to add stock, 'Q' to quit")
                stdscr.addstr(4, 0, f"Current stocks: {len(self.stocks)}")
                
                # Show stocks
                row = 6
                for sym, stock in self.stocks.items():
                    stdscr.addstr(row, 0, f"  {stock.symbol}: ${stock.price:.2f}")
                    row += 1
                    
                stdscr.refresh()
                
            except Exception as e:
                self.log(f"ERROR getting string input: {str(e)}")
                curses.noecho()
                stdscr.addstr(8, 0, f"Error: {str(e)}", curses.color_pair(2))
                stdscr.refresh()
                stdscr.getch()
                
        except Exception as e:
            self.log(f"ERROR in _test_add_stock: {str(e)}")
            raise

if __name__ == "__main__":
    terminal = TestTerminalUI()
    terminal.run()
    
    # Print the log
    print("\n" + "=" * 60)
    print("TEST LOG:")
    print("=" * 60)
    with open("test_log.txt", "r") as f:
        print(f.read())