#!/usr/bin/env python3
"""
Simple launcher for Hotel Inventory Management System
Handles virtual environment and dependency checking automatically
"""

import os
import sys
import subprocess

def main():
    print("🏨 Hotel Inventory Management System Launcher")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in virtual environment")
        print("💡 Tip: Run 'source venv/bin/activate' first for best results")
    
    # Check critical dependencies
    missing_deps = []
    
    try:
        import tkinter
        print("✅ tkinter available")
    except ImportError:
        missing_deps.append("tkinter (install python3-tk)")
    
    try:
        import sqlite3
        print("✅ sqlite3 available")
    except ImportError:
        missing_deps.append("sqlite3")
    
    try:
        import bcrypt
        print("✅ bcrypt available")
    except ImportError:
        missing_deps.append("bcrypt")
        
    try:
        import matplotlib
        print("✅ matplotlib available")
    except ImportError:
        missing_deps.append("matplotlib")
        
    try:
        import pandas
        print("✅ pandas available")
    except ImportError:
        missing_deps.append("pandas")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("📦 Install with: pip install bcrypt matplotlib pandas")
        return False
    
    print("\n🚀 Starting Hotel Inventory Management System...")
    print("🔑 Default login: admin / admin123")
    print("-" * 50)
    
    # Import and run the application
    try:
        from main import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        print("📋 Check hotel_inventory.log for details")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPress Enter to exit...")