#!/usr/bin/env python3
"""Simple test to check if curses input works"""

import curses
import sys

def test_input(stdscr):
    # Setup
    curses.curs_set(1)  # Show cursor
    stdscr.clear()
    
    # Show instructions
    stdscr.addstr(0, 0, "CURSES INPUT TEST")
    stdscr.addstr(2, 0, "This will test the 'add stock' functionality")
    stdscr.addstr(4, 0, "Press 'A' to test adding a stock...")
    stdscr.refresh()
    
    # Wait for 'A' key
    while True:
        key = stdscr.getch()
        if key == ord('a') or key == ord('A'):
            break
        elif key == ord('q') or key == ord('Q'):
            return "User quit without testing"
    
    # Test input
    stdscr.addstr(6, 0, "You pressed 'A'! Now testing text input...")
    stdscr.addstr(8, 0, "ENTER SYMBOL: ")
    stdscr.refresh()
    
    try:
        # Enable echo to show typed characters
        curses.echo()
        
        # Get string input (max 10 characters)
        symbol = stdscr.getstr(8, 14, 10).decode('utf-8').upper()
        
        # Disable echo
        curses.noecho()
        
        # Show result
        stdscr.addstr(10, 0, f"You entered: {symbol}")
        stdscr.addstr(12, 0, "SUCCESS! Input functionality works correctly.")
        stdscr.addstr(14, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()
        
        return f"SUCCESS: Captured symbol '{symbol}'"
        
    except Exception as e:
        curses.noecho()
        error_msg = f"ERROR: {str(e)}"
        stdscr.addstr(10, 0, error_msg)
        stdscr.addstr(12, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()
        return error_msg

# Check if windows-curses is needed
if sys.platform == "win32":
    try:
        import _curses
        print("Native curses support detected")
    except ImportError:
        print("Windows detected. Make sure windows-curses is installed:")
        print("  pip install windows-curses")
        print()

# Run the test
try:
    result = curses.wrapper(test_input)
    print("\nTest completed!")
    print("Result:", result)
except Exception as e:
    print(f"\nFailed to run curses test: {e}")
    print("\nPossible solutions:")
    print("1. Install windows-curses: pip install windows-curses")
    print("2. Use Windows Terminal instead of cmd.exe")
    print("3. Run in a compatible terminal emulator")