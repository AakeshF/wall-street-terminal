#!/usr/bin/env python3
"""Test the main application's add stock functionality"""

import subprocess
import time
import sys
import os

# Test sequence: Wait, press A, type AAPL, press Enter, wait, press Q to quit
test_input = "a\nAAPL\nq"

# Create a test file with input
with open("test_input.txt", "w") as f:
    f.write(test_input)

print("Testing stock terminal add functionality...")
print("=" * 50)

# Run the main app with input redirection
try:
    # Note: This won't work well with curses apps, but will show any errors
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=test_input.encode(),
        capture_output=True,
        timeout=5
    )
    
    print("STDOUT:")
    print(result.stdout.decode() if result.stdout else "(empty)")
    print("\nSTDERR:")
    print(result.stderr.decode() if result.stderr else "(empty)")
    print("\nReturn code:", result.returncode)
    
except subprocess.TimeoutExpired:
    print("Process timed out (expected for interactive curses app)")
except Exception as e:
    print(f"Error: {e}")
    
# Clean up
if os.path.exists("test_input.txt"):
    os.remove("test_input.txt")

print("\n" + "=" * 50)
print("Note: Curses apps don't work well with automated testing.")
print("For proper testing, run main.py manually and:")
print("1. Press 'A' to add stock")
print("2. Try typing a symbol when prompted")
print("3. Press Enter to confirm")
print("4. Press 'Q' to quit")