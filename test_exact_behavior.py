#!/usr/bin/env python3
"""Test exact behavior of add stock functionality from main.py"""

import curses
import sys
import os

def test_exact_behavior(stdscr):
    # Create log file
    log = open("test_results.txt", "w")
    
    try:
        # Match exact settings from main.py
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)
        
        # Color pairs
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        
        log.write("Initialization successful\n")
        
        # Draw screen similar to main app
        stdscr.clear()
        header = "=" * 80
        stdscr.addstr(0, 0, header[:80], curses.color_pair(3))
        stdscr.addstr(1, 0, " STOCK TERMINAL TEST - PRESS 'A' TO ADD STOCK ", curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(2, 0, header[:80], curses.color_pair(3))
        stdscr.addstr(5, 2, "NO STOCKS LOADED. PRESS 'A' TO ADD.", curses.color_pair(3))
        
        h, w = stdscr.getmaxyx()
        commands = "[A]DD STOCK  [Q]UIT"
        if h > 2:
            stdscr.addstr(h-2, 2, "-" * 76, curses.color_pair(3))
            stdscr.addstr(h-1, 2, commands, curses.color_pair(3))
        
        stdscr.refresh()
        log.write("Initial screen drawn\n")
        
        # Change to blocking mode for easier testing
        stdscr.nodelay(0)
        
        # Wait for 'A' key
        log.write("Waiting for user input...\n")
        key = stdscr.getch()
        log.write(f"Key pressed: {key} ('{chr(key) if 32 <= key <= 126 else 'special'}')\n")
        
        if key == ord('a') or key == ord('A'):
            log.write("'A' key detected - testing add stock functionality\n")
            
            # Exact code from main.py _add_stock method
            try:
                curses.echo()
                stdscr.addstr(10, 2, "ENTER SYMBOL: ")
                stdscr.refresh()
                
                log.write("Prompt displayed, waiting for input...\n")
                
                # This is the critical line - exact same as main.py line 94
                symbol = stdscr.getstr(10, 16, 10).decode('utf-8').upper()
                
                log.write(f"Successfully captured symbol: '{symbol}'\n")
                
                curses.noecho()
                
                # Show success
                stdscr.addstr(12, 2, f"Added: {symbol}", curses.color_pair(1))
                stdscr.addstr(14, 2, "Stock added successfully! Press any key to exit...", curses.color_pair(1))
                stdscr.refresh()
                stdscr.getch()
                
                log.write("Test completed successfully!\n")
                
            except Exception as e:
                curses.noecho()
                log.write(f"ERROR during input: {type(e).__name__}: {str(e)}\n")
                stdscr.addstr(12, 2, f"ERROR: {str(e)}", curses.color_pair(2))
                stdscr.addstr(14, 2, "Press any key to exit...", curses.color_pair(2))
                stdscr.refresh()
                stdscr.getch()
                
        else:
            log.write("Different key pressed, exiting\n")
            
    except Exception as e:
        log.write(f"FATAL ERROR: {type(e).__name__}: {str(e)}\n")
    finally:
        log.close()

# Run the test
print("Starting test...")
print("When the terminal opens:")
print("1. Press 'A' to test add stock functionality")
print("2. Try typing a stock symbol when prompted")
print("3. Press Enter to confirm")
print("\nPress Enter to start the test...")
input()

try:
    curses.wrapper(test_exact_behavior)
except Exception as e:
    print(f"\nError running test: {e}")

# Display results
print("\n" + "="*60)
print("TEST RESULTS:")
print("="*60)

if os.path.exists("test_results.txt"):
    with open("test_results.txt", "r") as f:
        print(f.read())
else:
    print("No results file created")
    
# Clean up
if os.path.exists("test_results.txt"):
    os.remove("test_results.txt")