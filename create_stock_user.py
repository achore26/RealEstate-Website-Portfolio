#!/usr/bin/env python3
"""
Script to create a Stock User with limited permissions
This user can only remove stock, not add stock or manage items
"""

from db import db_manager
from login import UserManager
import sys

def create_stock_user():
    """Create a stock user with limited permissions"""
    print("🏨 Creating Stock User for Madit Hotel Inventory")
    print("=" * 50)
    
    try:
        # Connect to database
        db_manager.connect()
        
        # Create stock user
        username = "stockuser"
        password = "stock123"
        role = "Stock User"
        
        # Check if user already exists
        existing_user = db_manager.get_user_by_username(username)
        if existing_user:
            print(f"⚠️  User '{username}' already exists")
            return True
        
        # Create the user
        UserManager.create_user(username, password, role)
        print(f"✅ Stock User created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Role: {role}")
        print(f"   Permissions: Can only remove stock from inventory")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create stock user: {e}")
        return False

if __name__ == "__main__":
    success = create_stock_user()
    if success:
        print("\n🎉 Stock User created! You can now login with:")
        print("   Username: stockuser")
        print("   Password: stock123")
    else:
        print("\n❌ Failed to create stock user")
    
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)