#!/usr/bin/env python3
"""
Quick launcher script for Hotel Inventory Management System
This script handles dependency checking and provides helpful error messages
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        print("Please upgrade Python and try again.")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'tkinter',
        'sqlite3',
        'bcrypt',
        'matplotlib',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'sqlite3':
                import sqlite3
            elif package == 'bcrypt':
                import bcrypt
            elif package == 'matplotlib':
                import matplotlib
            elif package == 'pandas':
                import pandas
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 To install missing packages, run:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def install_dependencies():
    """Attempt to install dependencies automatically"""
    print("🔄 Attempting to install dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies automatically")
        print("Please run manually: pip install -r requirements.txt")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def main():
    """Main launcher function"""
    print("🏨 Hotel Inventory Management System Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found")
        print("Please run this script from the hotel_inventory_system directory")
        input("Press Enter to exit...")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n🤔 Would you like to install missing dependencies automatically? (y/n): ", end="")
        choice = input().lower().strip()
        
        if choice in ['y', 'yes']:
            if not install_dependencies():
                input("Press Enter to exit...")
                return
        else:
            print("Please install dependencies manually and try again.")
            input("Press Enter to exit...")
            return
    
    print("✅ All dependencies satisfied")
    print("🚀 Starting Hotel Inventory Management System...")
    print("-" * 50)
    
    # Import and run the main application
    try:
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please check that all files are present and try again.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Application error: {e}")
        print("Check hotel_inventory.log for detailed error information.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()