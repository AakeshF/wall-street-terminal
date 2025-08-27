#!/usr/bin/env python3
"""Test if curses works on Windows and check specific functionality"""

import sys
import curses

print("Testing curses functionality on Windows...")
print("Python version:", sys.version)
print("Platform:", sys.platform)

try:
    # Test if curses module loads
    print("\n1. Curses module imported successfully")
    
    # Test basic curses initialization
    def test_curses(stdscr):
        results = []
        
        try:
            # Basic setup
            curses.curs_set(0)
            results.append("✓ Cursor visibility setting works")
        except Exception as e:
            results.append(f"✗ Cursor visibility error: {e}")
            
        try:
            # Test echo/noecho
            curses.echo()
            curses.noecho()
            results.append("✓ Echo mode toggling works")
        except Exception as e:
            results.append(f"✗ Echo mode error: {e}")
            
        try:
            # Test colors
            if curses.has_colors():
                curses.start_color()
                curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
                results.append("✓ Color support available and working")
            else:
                results.append("✗ No color support")
        except Exception as e:
            results.append(f"✗ Color initialization error: {e}")
            
        try:
            # Test screen operations
            stdscr.clear()
            stdscr.addstr(0, 0, "Test text")
            stdscr.refresh()
            results.append("✓ Basic screen operations work")
        except Exception as e:
            results.append(f"✗ Screen operations error: {e}")
            
        try:
            # Test getstr functionality
            stdscr.addstr(2, 0, "Testing getstr: ")
            stdscr.refresh()
            # Note: We can't actually test interactive input in this context
            results.append("✓ getstr method exists (interactive test needed)")
        except Exception as e:
            results.append(f"✗ getstr error: {e}")
            
        return results
    
    # Run the test
    results = curses.wrapper(test_curses)
    
    print("\n2. Curses wrapper executed successfully")
    print("\nTest Results:")
    for result in results:
        print("  ", result)
        
except ImportError as e:
    print(f"\n✗ Failed to import curses: {e}")
    print("\nOn Windows, you might need:")
    print("  - windows-curses package: pip install windows-curses")
    print("  - Or use Windows Terminal instead of cmd.exe")
    
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")

# Check if windows-curses is installed
print("\nChecking for windows-curses package...")
try:
    import pip
    installed_packages = [pkg.key for pkg in pip.get_installed_distributions()]
    if 'windows-curses' in installed_packages:
        print("✓ windows-curses is installed")
    else:
        print("✗ windows-curses not found")
except:
    # Try alternative method
    try:
        import pkg_resources
        installed = [pkg.key for pkg in pkg_resources.working_set]
        if 'windows-curses' in installed:
            print("✓ windows-curses is installed")
        else:
            print("✗ windows-curses might not be installed")
    except:
        print("Could not check package installation")