#!/usr/bin/env python3
"""
Enhanced Launcher for Madit Hotel Inventory System
Includes theme application and user role information
"""

import os
import sys
import subprocess

def main():
    print("🏨 MADIT HOTEL INVENTORY SYSTEM")
    print("=" * 50)
    print("Enhanced with beautiful UI and role-based permissions")
    print()
    
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
        print(f"\\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("📦 Install with: pip install bcrypt matplotlib pandas")
        return False
    
    print("\\n🎨 UI ENHANCEMENTS:")
    print("   • Beautiful Madit Hotel theme")
    print("   • Enhanced color scheme")
    print("   • Role-based button visibility")
    print("   • Improved navigation")
    
    print("\\n👥 USER ROLES AVAILABLE:")
    print("   🔴 Admin (admin/admin123) - Full access")
    print("   🔵 Clerk (create via Admin menu) - Add/Edit items, Stock operations")
    print("   🟡 Stock User (stockuser/stock123) - Remove stock only")
    
    print("\\n🚀 Starting Madit Hotel Inventory System...")
    print("-" * 50)
    
    # Import and run the application
    try:
        from main import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\\n👋 Application closed by user")
    except Exception as e:
        print(f"\\n❌ Application error: {e}")
        print("📋 Check hotel_inventory.log for details")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\\nPress Enter to exit...")