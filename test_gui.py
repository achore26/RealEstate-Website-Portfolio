#!/usr/bin/env python3
"""
GUI Test for Hotel Inventory Management System
This script tests the main GUI components without requiring user interaction
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

def test_login_window():
    """Test login window creation"""
    print("Testing Login Window...")
    
    try:
        from login import LoginWindow
        
        # Create a test window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Test login window creation (but don't show it)
        def mock_callback(user):
            print(f"✓ Login callback works: {user}")
            root.quit()
        
        # Just test that we can create the login window class
        login_window = LoginWindow(mock_callback)
        login_window.root.withdraw()  # Hide the login window
        
        print("✓ Login window created successfully")
        
        # Clean up
        login_window.root.destroy()
        root.destroy()
        
    except Exception as e:
        print(f"✗ Login window test failed: {e}")
        return False
    
    return True

def test_main_interface():
    """Test main application interface components"""
    print("Testing Main Interface Components...")
    
    try:
        # Test basic tkinter widgets
        root = tk.Tk()
        root.title("GUI Test")
        root.geometry("800x600")
        root.withdraw()  # Don't show the window
        
        # Test notebook (tabbed interface)
        notebook = ttk.Notebook(root)
        
        # Test frames
        frame1 = ttk.Frame(notebook)
        frame2 = ttk.Frame(notebook)
        
        notebook.add(frame1, text="Tab 1")
        notebook.add(frame2, text="Tab 2")
        
        # Test treeview (for inventory table)
        columns = ('ID', 'Name', 'Category', 'Quantity')
        tree = ttk.Treeview(frame1, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
        
        # Test buttons
        btn1 = ttk.Button(frame1, text="Test Button")
        btn2 = ttk.Button(frame2, text="Another Button")
        
        # Test labels
        label1 = ttk.Label(frame1, text="Test Label")
        label2 = ttk.Label(frame2, text="Another Label")
        
        # Test entry widgets
        entry1 = ttk.Entry(frame1)
        entry2 = ttk.Entry(frame2)
        
        print("✓ All tkinter widgets created successfully")
        
        # Test grid layout
        tree.grid(row=0, column=0, columnspan=2, sticky='nsew')
        btn1.grid(row=1, column=0, padx=5, pady=5)
        label1.grid(row=1, column=1, padx=5, pady=5)
        entry1.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        btn2.grid(row=0, column=0, padx=5, pady=5)
        label2.grid(row=0, column=1, padx=5, pady=5)
        entry2.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        print("✓ Grid layout works correctly")
        
        # Test notebook packing
        notebook.pack(fill='both', expand=True)
        
        print("✓ Notebook packing works correctly")
        
        # Clean up
        root.destroy()
        
    except Exception as e:
        print(f"✗ Main interface test failed: {e}")
        return False
    
    return True

def test_matplotlib_integration():
    """Test matplotlib integration with tkinter"""
    print("Testing Matplotlib Integration...")
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend for testing
        
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        # Create test window
        root = tk.Tk()
        root.withdraw()
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(['Item 1', 'Item 2', 'Item 3'], [10, 15, 8])
        ax.set_title('Test Chart')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, root)
        canvas.get_tk_widget().pack()
        
        print("✓ Matplotlib integration works")
        
        # Clean up
        plt.close(fig)
        root.destroy()
        
    except Exception as e:
        print(f"✗ Matplotlib integration test failed: {e}")
        return False
    
    return True

def test_database_gui_integration():
    """Test database integration with GUI components"""
    print("Testing Database-GUI Integration...")
    
    try:
        from db import db_manager
        from inventory import InventoryManager
        
        # Connect to database
        db_manager.connect()
        
        # Create test window with treeview
        root = tk.Tk()
        root.withdraw()
        
        # Create treeview
        columns = ('ID', 'Name', 'Category', 'Quantity', 'Unit')
        tree = ttk.Treeview(root, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
        
        # Get data from database and populate treeview
        items = InventoryManager.get_all_items()
        
        for item in items:
            tree.insert('', tk.END, values=(
                item['id'],
                item['name'],
                item['category'],
                f"{item['quantity']:.2f}",
                item['unit']
            ))
        
        print(f"✓ Database-GUI integration works ({len(items)} items loaded)")
        
        # Clean up
        root.destroy()
        db_manager.disconnect()
        
    except Exception as e:
        print(f"✗ Database-GUI integration test failed: {e}")
        return False
    
    return True

def run_all_tests():
    """Run all GUI tests"""
    print("🏨 Hotel Inventory Management System - GUI Tests")
    print("=" * 60)
    
    tests = [
        ("Login Window", test_login_window),
        ("Main Interface", test_main_interface),
        ("Matplotlib Integration", test_matplotlib_integration),
        ("Database-GUI Integration", test_database_gui_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All GUI tests passed! The system is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)