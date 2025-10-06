#!/usr/bin/env python3
"""
Database Migration Script for Madit Hotel Inventory System
Updates the database schema to support the new 'Stock User' role
"""

import sqlite3
import os
import sys
from db import db_manager

def migrate_database():
    """Migrate database to support Stock User role"""
    print("🏨 Madit Hotel Inventory - Database Migration")
    print("=" * 50)
    
    try:
        # Connect to database
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        print("📋 Checking current database schema...")
        
        # Check if we need to migrate
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        # Check current role constraint
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
        table_sql = cursor.fetchone()[0]
        
        if "'Stock User'" in table_sql:
            print("✅ Database already supports Stock User role")
            return True
        
        print("🔄 Migrating database schema...")
        
        # Create new users table with updated constraint
        cursor.execute('''
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('Admin', 'Clerk', 'Stock User')),
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Copy existing data
        cursor.execute('''
            INSERT INTO users_new (id, username, password_hash, role, created_date, last_login)
            SELECT id, username, password_hash, role, created_date, last_login
            FROM users
        ''')
        
        # Drop old table and rename new one
        cursor.execute('DROP TABLE users')
        cursor.execute('ALTER TABLE users_new RENAME TO users')
        
        db_manager.connection.commit()
        
        print("✅ Database migration completed successfully!")
        print("📊 New role constraint: Admin, Clerk, Stock User")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if db_manager.connection:
            db_manager.connection.rollback()
            db_manager.disconnect()
        return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎉 Migration completed! You can now create Stock Users.")
        print("💡 Run: python3 create_stock_user.py")
    else:
        print("\n❌ Migration failed. Please check the error above.")
    
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)