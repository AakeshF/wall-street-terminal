#!/usr/bin/env python3
"""
Wall Street Terminal v4.0 Launcher
==================================
Handles proper initialization for standalone execution
"""

import sys
import os

# Set up proper environment for Windows standalone execution
if sys.platform == "win32":
    # Ensure we have proper console allocation
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        
        # Allocate a console if we don't have one
        if not kernel32.GetConsoleWindow():
            kernel32.AllocConsole()
            
            # Redirect stdout/stderr to the new console
            sys.stdout = open('CONOUT$', 'w')
            sys.stderr = open('CONOUT$', 'w')
            sys.stdin = open('CONIN$', 'r')
    except:
        pass

# Now import and run the main app
from main_app import main

if __name__ == "__main__":
    main()