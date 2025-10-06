#!/usr/bin/env python3
"""
Database Debug Script for Hotel Inventory Management System
This script helps identify and fix SQLite errors
"""

import sqlite3
import os
import sys
import traceback

def test_sqlite_basic():
    """Test basic SQLite functionality"""
    print("🔍 Testing Basic SQLite Functionality...")
    
    try:
        # Test SQLite version
        print(f"SQLite version: {sqlite3.sqlite_version}")
        print(f"Python sqlite3 module version: {sqlite3.version}")
        
        # Test basic connection
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Test basic table creation
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        
        # Test insert
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
        conn.commit()
        
        # Test select
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchall()
        
        conn.close()
        
        print("✅ Basic SQLite functionality works")
        return True
        
    except Exception as e:
        print(f"❌ Basic SQLite test failed: {e}")
        traceback.print_exc()
        return False

def test_database_file():
    """Test database file creation and permissions"""
    print("📁 Testing Database File Operations...")
    
    try:
        db_file = "test_hotel_inventory.db"
        
        # Remove existing test file
        if os.path.exists(db_file):
            os.remove(db_file)
        
        # Test file creation
        conn = sqlite3.connect(db_file)
        print(f"✅ Database file created: {db_file}")
        
        # Test write permissions
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        print("✅ Write permissions work")
        
        conn.close()
        
        # Test file exists
        if os.path.exists(db_file):
            print("✅ Database file persists")
            os.remove(db_file)  # Clean up
        else:
            print("❌ Database file not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database file test failed: {e}")
        traceback.print_exc()
        return False

def test_table_creation():
    """Test the exact table creation SQL from the application"""
    print("🏗️  Testing Application Table Creation...")
    
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Test users table
        print("Creating users table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('Admin', 'Clerk')),
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        print("✅ Users table created")
        
        # Test items table
        print("Creating items table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 0,
                unit TEXT NOT NULL,
                reorder_level REAL NOT NULL DEFAULT 0,
                supplier TEXT,
                expiry_date DATE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Items table created")
        
        # Test transactions table
        print("Creating transactions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('IN', 'OUT')),
                quantity REAL NOT NULL,
                notes TEXT,
                date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        ''')
        print("✅ Transactions table created")
        
        conn.commit()
        conn.close()
        
        print("✅ All application tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        traceback.print_exc()
        return False

def test_bcrypt_import():
    """Test bcrypt import (common issue)"""
    print("🔐 Testing bcrypt Import...")
    
    try:
        import bcrypt
        
        # Test basic bcrypt functionality
        password = "test123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        if bcrypt.checkpw(password.encode('utf-8'), hashed):
            print("✅ bcrypt works correctly")
            return True
        else:
            print("❌ bcrypt verification failed")
            return False
            
    except ImportError:
        print("❌ bcrypt not installed. Run: pip install bcrypt")
        return False
    except Exception as e:
        print(f"❌ bcrypt test failed: {e}")
        return False

def test_application_db_module():
    """Test the actual database module from the application"""
    print("🏨 Testing Application Database Module...")
    
    try:
        # Import the database module
        from db import DatabaseManager
        
        # Create database manager
        db_manager = DatabaseManager()
        print("✅ Database manager created")
        
        # Test connection
        db_manager.connect()
        print("✅ Database connection established")
        
        # Test table creation
        db_manager.create_tables()
        print("✅ Tables created successfully")
        
        # Test default admin creation
        user = db_manager.get_user_by_username('admin')
        if user:
            print("✅ Default admin user created")
        else:
            print("❌ Default admin user not found")
            return False
        
        # Test password verification
        if db_manager.verify_password('admin123', user['password_hash']):
            print("✅ Password verification works")
        else:
            print("❌ Password verification failed")
            return False
        
        db_manager.disconnect()
        print("✅ Database disconnected properly")
        
        return True
        
    except Exception as e:
        print(f"❌ Application database module test failed: {e}")
        traceback.print_exc()
        return False

def clean_database_files():
    """Clean up any existing database files"""
    print("🧹 Cleaning up database files...")
    
    db_files = [
        "hotel_inventory.db",
        "test_hotel_inventory.db",
        "hotel_inventory.db-journal"
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"✅ Removed {db_file}")
            except Exception as e:
                print(f"⚠️  Could not remove {db_file}: {e}")

def main():
    """Run all database diagnostic tests"""
    print("🏨 Hotel Inventory Management System - Database Diagnostics")
    print("=" * 70)
    
    tests = [
        ("SQLite Basic Functionality", test_sqlite_basic),
        ("Database File Operations", test_database_file),
        ("Table Creation SQL", test_table_creation),
        ("bcrypt Import", test_bcrypt_import),
        ("Application Database Module", test_application_db_module)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Diagnostic Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All database tests passed! The system should work correctly.")
        print("\n🚀 Try launching the application:")
        print("   python3 main.py")
    else:
        print("⚠️  Some database tests failed. Check the errors above.")
        print("\n🔧 Common fixes:")
        print("   1. Install missing dependencies: pip install bcrypt")
        print("   2. Check file permissions in the current directory")
        print("   3. Try running: python3 debug_db.py")
        
        # Offer to clean up
        print("\n🧹 Clean up database files? (y/n): ", end="")
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes']:
                clean_database_files()
        except:
            pass

if __name__ == "__main__":
    main()