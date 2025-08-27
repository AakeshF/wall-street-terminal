#!/usr/bin/env python3
"""Test script to check add stock functionality"""

import curses
import sys

def test_add_stock(stdscr):
    # Initialize colors
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    
    # Clear screen
    stdscr.clear()
    
    # Show initial state
    stdscr.addstr(0, 0, "Testing Add Stock Functionality", curses.A_BOLD)
    stdscr.addstr(2, 0, "Press 'A' to test add stock...")
    stdscr.refresh()
    
    # Wait for 'A' key
    while True:
        key = stdscr.getch()
        if key == ord('a') or key == ord('A'):
            break
        elif key == ord('q'):
            return
    
    # Test the add stock functionality
    stdscr.addstr(4, 0, "Detected 'A' key press - simulating add stock")
    stdscr.refresh()
    
    try:
        # Enable echo mode to capture text input
        curses.echo()
        stdscr.addstr(6, 0, "ENTER SYMBOL: ")
        stdscr.refresh()
        
        # Try to get string input
        symbol = stdscr.getstr(6, 14, 10).decode('utf-8').upper()
        
        curses.noecho()
        
        stdscr.addstr(8, 0, f"Successfully captured symbol: {symbol}")
        stdscr.addstr(10, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()
        
    except Exception as e:
        curses.noecho()
        stdscr.addstr(8, 0, f"ERROR: {str(e)}")
        stdscr.addstr(10, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(test_add_stock)