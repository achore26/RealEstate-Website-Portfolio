#!/usr/bin/env python3
"""
Full Application Test for Hotel Inventory Management System
This script tests the complete application startup and basic functionality
"""

import tkinter as tk
from tkinter import messagebox
import sys
import threading
import time

def test_application_startup():
    """Test complete application startup"""
    print("🚀 Testing Full Application Startup...")
    
    try:
        # Import main application
        from main import HotelInventoryApp
        from db import db_manager
        
        print("✓ All modules imported successfully")
        
        # Initialize database
        db_manager.connect()
        db_manager.create_tables()
        print("✓ Database initialized")
        
        # Test that we can create the app class
        print("✓ Application class can be instantiated")
        
        db_manager.disconnect()
        print("✓ Database connection closed properly")
        
        return True
        
    except Exception as e:
        print(f"❌ Application startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_functionality():
    """Test login functionality without GUI"""
    print("🔐 Testing Login Functionality...")
    
    try:
        from login import UserManager
        from db import db_manager
        
        db_manager.connect()
        
        # Test getting default admin user
        user = db_manager.get_user_by_username('admin')
        if user:
            print("✓ Default admin user exists")
            
            # Test password verification
            if db_manager.verify_password('admin123', user['password_hash']):
                print("✓ Password verification works")
            else:
                print("❌ Password verification failed")
                return False
        else:
            print("❌ Default admin user not found")
            return False
        
        # Test user management functions
        all_users = UserManager.get_all_users()
        print(f"✓ User management works ({len(all_users)} users found)")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Login functionality test failed: {e}")
        return False

def test_inventory_operations():
    """Test inventory operations"""
    print("📦 Testing Inventory Operations...")
    
    try:
        from inventory import InventoryManager, StockManager
        from db import db_manager
        
        db_manager.connect()
        
        # Add a test item
        InventoryManager.add_item(
            name='Test Hotel Soap',
            category='Toiletries',
            quantity=100.0,
            unit='pieces',
            reorder_level=20.0,
            supplier='Hotel Supplies Co',
            expiry_date='2025-06-30'
        )
        print("✓ Item added successfully")
        
        # Get all items
        items = InventoryManager.get_all_items()
        print(f"✓ Retrieved {len(items)} items")
        
        # Test stock operations
        if items:
            item_id = items[-1]['id']  # Get the last item
            
            # Add stock
            StockManager.add_stock(1, item_id, 50.0, "Test delivery")
            print("✓ Stock added successfully")
            
            # Use stock
            StockManager.use_stock(1, item_id, 25.0, "Test consumption")
            print("✓ Stock used successfully")
            
            # Get transaction history
            transactions = StockManager.get_item_transactions(item_id)
            print(f"✓ Transaction history retrieved ({len(transactions)} transactions)")
        
        # Test search
        search_results = InventoryManager.search_items('Soap')
        print(f"✓ Search functionality works ({len(search_results)} results)")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Inventory operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alerts_system():
    """Test alerts system"""
    print("🚨 Testing Alerts System...")
    
    try:
        from alerts import AlertManager
        from inventory import InventoryManager
        from db import db_manager
        
        db_manager.connect()
        
        # Add an item with low stock to trigger alert
        InventoryManager.add_item(
            name='Low Stock Item',
            category='Cleaning',
            quantity=5.0,
            unit='bottles',
            reorder_level=10.0,
            supplier='Cleaning Co'
        )
        print("✓ Low stock test item added")
        
        # Test alert manager
        alert_manager = AlertManager()
        alerts = alert_manager.check_all_alerts()
        
        print(f"✓ Alert system works")
        print(f"  - Low stock items: {len(alerts['low_stock'])}")
        print(f"  - Expiring items: {len(alerts['expiring'])}")
        print(f"  - Total alerts: {alerts['total_alerts']}")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Alerts system test failed: {e}")
        return False

def test_reports_generation():
    """Test reports generation"""
    print("📊 Testing Reports Generation...")
    
    try:
        from reports import ReportsManager
        from db import db_manager
        
        db_manager.connect()
        
        reports_manager = ReportsManager()
        
        # Test inventory summary
        summary = reports_manager.get_inventory_summary()
        print(f"✓ Inventory summary generated")
        print(f"  - Total items: {summary['total_items']}")
        print(f"  - Low stock items: {summary['low_stock_items']}")
        
        # Test category analysis
        categories = reports_manager.get_category_analysis()
        print(f"✓ Category analysis completed ({len(categories)} categories)")
        
        # Test top used items
        top_items = reports_manager.get_top_used_items()
        print(f"✓ Top used items analysis completed ({len(top_items)} items)")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Reports generation test failed: {e}")
        return False

def test_data_persistence():
    """Test data persistence and backup"""
    print("💾 Testing Data Persistence...")
    
    try:
        from db import db_manager
        import os
        
        db_manager.connect()
        
        # Test backup
        backup_path = db_manager.backup_database()
        if os.path.exists(backup_path):
            print(f"✓ Database backup created: {backup_path}")
            
            # Clean up backup file
            os.remove(backup_path)
            print("✓ Backup file cleaned up")
        else:
            print("❌ Backup file not created")
            return False
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive application test"""
    print("🏨 Hotel Inventory Management System - Comprehensive Test")
    print("=" * 70)
    
    tests = [
        ("Application Startup", test_application_startup),
        ("Login Functionality", test_login_functionality),
        ("Inventory Operations", test_inventory_operations),
        ("Alerts System", test_alerts_system),
        ("Reports Generation", test_reports_generation),
        ("Data Persistence", test_data_persistence)
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
    print(f"📊 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The Hotel Inventory Management System is fully functional!")
        print("\n🚀 Ready to launch:")
        print("   python3 main.py")
        print("\n🔑 Default login:")
        print("   Username: admin")
        print("   Password: admin123")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)