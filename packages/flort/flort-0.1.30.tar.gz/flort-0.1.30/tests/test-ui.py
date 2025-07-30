#!/usr/bin/env python3
"""
Test script to check if the UI functionality works properly.

This script tests:
1. Curses module availability
2. Curses selector import
3. Basic UI functionality
"""

import sys
import os
from pathlib import Path

def test_curses_availability():
    """Test if curses module is available."""
    print("🔍 Testing curses module availability...")
    
    try:
        import curses
        print("✅ Curses module imported successfully")
        
        # Test basic curses functionality
        try:
            # This is a safe test that doesn't actually start curses
            curses.version
            print(f"✅ Curses version: {getattr(curses, 'version', 'unknown')}")
            return True
        except Exception as e:
            print(f"⚠️  Curses module imported but may not work: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Curses module not available: {e}")
        print("\n💡 To fix this:")
        if sys.platform.startswith('win'):
            print("   On Windows: pip install windows-curses")
        else:
            print("   On Linux/macOS: curses should be included with Python")
            print("   If missing, install with your package manager")
        return False

def test_flort_ui_import():
    """Test if flort curses selector can be imported."""
    print("\n🔍 Testing flort UI module...")
    
    try:
        # Add flort directory to path if needed
        flort_dir = Path(__file__).parent.parent / "flort"
        if flort_dir.exists() and str(flort_dir) not in sys.path:
            sys.path.insert(0, str(flort_dir.parent))
        
        from flort.curses_selector import select_files
        print("✅ Flort curses selector imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Flort curses selector import failed: {e}")
        print("\n💡 Possible issues:")
        print("   - Curses module not available (see above)")
        print("   - Flort not properly installed")
        print("   - Missing dependencies")
        return False

def test_basic_ui_functionality():
    """Test basic UI functionality without actually starting it."""
    print("\n🔍 Testing basic UI functionality...")
    
    try:
        import curses
        from flort.curses_selector import (
            is_accessible, should_show_file, get_directory_contents
        )
        
        # Test utility functions
        current_dir = Path(".")
        
        # Test accessibility check
        accessible = is_accessible(current_dir)
        print(f"✅ Directory accessibility test: {accessible}")
        
        # Test file filtering
        test_file = current_dir / "setup.py"
        if test_file.exists():
            show_file = should_show_file(test_file, [".py"], {})
            print(f"✅ File filtering test: {show_file}")
        
        print("✅ Basic UI functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic UI functionality test failed: {e}")
        return False

def test_ui_integration():
    """Test the UI integration with flort CLI."""
    print("\n🔍 Testing UI integration...")
    
    try:
        from flort.cli import process_ui_integration
        from argparse import Namespace
        
        # Create test args
        args = Namespace()
        args.ui = False  # Don't actually start UI
        args.extensions = "py"
        args.include_files = None
        args.ignore_dirs = None
        args.directories = ["."]
        
        # Test the integration function
        result_args = process_ui_integration(args)
        print("✅ UI integration function works")
        return True
        
    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        return False

def run_interactive_test():
    """Run an actual interactive test if possible."""
    print("\n🔍 Running interactive test...")
    
    try:
        import curses
        from flort.curses_selector import select_files
        
        print("⚠️  This will start the interactive UI for 5 seconds...")
        print("   Press 'q' to quit or wait for auto-exit")
        
        def test_ui(stdscr):
            # Simple test that shows the UI briefly
            stdscr.clear()
            stdscr.addstr(0, 0, "Flort UI Test - Press 'q' to quit")
            stdscr.addstr(1, 0, "This is a test of the curses interface")
            stdscr.addstr(2, 0, "If you see this, the UI is working!")
            stdscr.refresh()
            
            # Wait for input or timeout
            stdscr.timeout(5000)  # 5 second timeout
            key = stdscr.getch()
            
            return key
        
        # Run the test
        result = curses.wrapper(test_ui)
        print("✅ Interactive UI test completed successfully")
        return True
        
    except KeyboardInterrupt:
        print("⚠️  Interactive test cancelled by user")
        return True
    except Exception as e:
        print(f"❌ Interactive UI test failed: {e}")
        return False

def main():
    """Run all UI tests."""
    print("🧪 Flort UI Test Suite")
    print("=" * 50)
    
    tests = [
        ("Curses Module", test_curses_availability),
        ("Flort UI Import", test_flort_ui_import),
        ("Basic UI Functions", test_basic_ui_functionality),
        ("UI Integration", test_ui_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! UI should work correctly.")
        
        # Offer interactive test
        try:
            response = input("\n❓ Run interactive UI test? (y/N): ")
            if response.lower() in ['y', 'yes']:
                run_interactive_test()
        except (KeyboardInterrupt, EOFError):
            print("\nSkipping interactive test.")
    else:
        print("⚠️  Some tests failed. UI may not work properly.")
        print("\n💡 Common solutions:")
        if sys.platform.startswith('win'):
            print("   • Install windows-curses: pip install windows-curses")
        print("   • Reinstall flort: pip install -e .")
        print("   • Check Python version compatibility")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)