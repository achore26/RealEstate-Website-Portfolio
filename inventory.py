"""
Inventory Management module for Hotel Inventory Management System
Handles item management, stock operations, and inventory display
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from db import db_manager
import logging

logger = logging.getLogger(__name__)

class InventoryManager:
    """Main inventory management class"""
    
    @staticmethod
    def add_item(name, category, quantity, unit, reorder_level, supplier=None, expiry_date=None):
        """Add a new item to inventory"""
        try:
            query = '''
                INSERT INTO items (name, category, quantity, unit, reorder_level, supplier, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            db_manager.execute_query(query, (name, category, quantity, unit, reorder_level, supplier, expiry_date))
            logger.info(f"Item '{name}' added to inventory")
            return True
        except Exception as e:
            logger.error(f"Error adding item: {e}")
            raise
    
    @staticmethod
    def update_item(item_id, name, category, quantity, unit, reorder_level, supplier=None, expiry_date=None):
        """Update an existing item"""
        try:
            query = '''
                UPDATE items 
                SET name=?, category=?, quantity=?, unit=?, reorder_level=?, supplier=?, expiry_date=?, updated_date=?
                WHERE id=?
            '''
            db_manager.execute_query(query, (name, category, quantity, unit, reorder_level, 
                                           supplier, expiry_date, datetime.now(), item_id))
            logger.info(f"Item ID {item_id} updated")
            return True
        except Exception as e:
            logger.error(f"Error updating item: {e}")
            raise
    
    @staticmethod
    def delete_item(item_id):
        """Delete an item from inventory"""
        try:
            # Check if item has transactions
            trans_query = "SELECT COUNT(*) FROM transactions WHERE item_id = ?"
            trans_count = db_manager.execute_query(trans_query, (item_id,))[0][0]
            
            if trans_count > 0:
                raise ValueError("Cannot delete item with transaction history")
            
            query = "DELETE FROM items WHERE id = ?"
            db_manager.execute_query(query, (item_id,))
            logger.info(f"Item ID {item_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting item: {e}")
            raise
    
    @staticmethod
    def get_all_items():
        """Get all items from inventory"""
        query = "SELECT * FROM items ORDER BY name"
        return db_manager.execute_query(query)
    
    @staticmethod
    def search_items(search_term, category_filter=None, supplier_filter=None):
        """Search items by name, category, or supplier"""
        query = "SELECT * FROM items WHERE name LIKE ?"
        params = [f"%{search_term}%"]
        
        if category_filter:
            query += " AND category = ?"
            params.append(category_filter)
        
        if supplier_filter:
            query += " AND supplier = ?"
            params.append(supplier_filter)
        
        query += " ORDER BY name"
        return db_manager.execute_query(query, params)
    
    @staticmethod
    def get_low_stock_items():
        """Get items with stock below reorder level"""
        query = "SELECT * FROM items WHERE quantity <= reorder_level ORDER BY name"
        return db_manager.execute_query(query)
    
    @staticmethod
    def get_expiring_items(days=5):
        """Get items expiring within specified days"""
        from datetime import timedelta
        expiry_threshold = (datetime.now() + timedelta(days=days)).date()
        query = "SELECT * FROM items WHERE expiry_date IS NOT NULL AND expiry_date <= ? ORDER BY expiry_date"
        return db_manager.execute_query(query, (expiry_threshold,))
    
    @staticmethod
    def get_categories():
        """Get all unique categories"""
        query = "SELECT DISTINCT category FROM items ORDER BY category"
        result = db_manager.execute_query(query)
        return [row[0] for row in result]
    
    @staticmethod
    def get_suppliers():
        """Get all unique suppliers"""
        query = "SELECT DISTINCT supplier FROM items WHERE supplier IS NOT NULL ORDER BY supplier"
        result = db_manager.execute_query(query)
        return [row[0] for row in result]

class StockManager:
    """Manage stock operations (IN/OUT transactions)"""
    
    @staticmethod
    def add_stock(user_id, item_id, quantity, notes=None):
        """Add stock (delivery/purchase)"""
        try:
            # Update item quantity
            update_query = "UPDATE items SET quantity = quantity + ?, updated_date = ? WHERE id = ?"
            db_manager.execute_query(update_query, (quantity, datetime.now(), item_id))
            
            # Record transaction
            trans_query = '''
                INSERT INTO transactions (user_id, item_id, type, quantity, notes)
                VALUES (?, ?, 'IN', ?, ?)
            '''
            db_manager.execute_query(trans_query, (user_id, item_id, quantity, notes))
            
            logger.info(f"Added {quantity} units to item ID {item_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding stock: {e}")
            raise
    
    @staticmethod
    def use_stock(user_id, item_id, quantity, notes=None):
        """Use stock (consumption/sale)"""
        try:
            # Check current stock
            stock_query = "SELECT quantity FROM items WHERE id = ?"
            current_stock = db_manager.execute_query(stock_query, (item_id,))[0][0]
            
            if current_stock < quantity:
                raise ValueError(f"Insufficient stock. Available: {current_stock}")
            
            # Update item quantity
            update_query = "UPDATE items SET quantity = quantity - ?, updated_date = ? WHERE id = ?"
            db_manager.execute_query(update_query, (quantity, datetime.now(), item_id))
            
            # Record transaction
            trans_query = '''
                INSERT INTO transactions (user_id, item_id, type, quantity, notes)
                VALUES (?, ?, 'OUT', ?, ?)
            '''
            db_manager.execute_query(trans_query, (user_id, item_id, quantity, notes))
            
            logger.info(f"Used {quantity} units from item ID {item_id}")
            return True
        except Exception as e:
            logger.error(f"Error using stock: {e}")
            raise
    
    @staticmethod
    def get_item_transactions(item_id, limit=50):
        """Get transaction history for an item"""
        query = '''
            SELECT t.*, u.username, i.name as item_name
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN items i ON t.item_id = i.id
            WHERE t.item_id = ?
            ORDER BY t.date_time DESC
            LIMIT ?
        '''
        return db_manager.execute_query(query, (item_id, limit))

class InventoryWindow:
    """Main inventory management window"""
    
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        self.create_inventory_interface()
        
    def create_inventory_interface(self):
        """Create the main inventory interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Inventory Management", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Search and filter frame
        self.create_search_frame()
        
        # Inventory table
        self.create_inventory_table()
        
        # Buttons frame
        self.create_buttons_frame()
        
        # Load inventory
        self.refresh_inventory()
    
    def create_search_frame(self):
        """Create search and filter controls"""
        search_frame = ttk.LabelFrame(self.main_frame, text="Search & Filter", padding="10")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        # Search by name
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_inventory())
        
        # Category filter
        ttk.Label(search_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, 
                                          state="readonly", width=15)
        self.category_combo.grid(row=0, column=3, padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self.search_inventory())
        
        # Supplier filter
        ttk.Label(search_frame, text="Supplier:").grid(row=0, column=4, sticky=tk.W, padx=(10, 5))
        self.supplier_var = tk.StringVar()
        self.supplier_combo = ttk.Combobox(search_frame, textvariable=self.supplier_var, 
                                          state="readonly", width=15)
        self.supplier_combo.grid(row=0, column=5, padx=5)
        self.supplier_combo.bind('<<ComboboxSelected>>', lambda e: self.search_inventory())
        
        # Clear filters button
        ttk.Button(search_frame, text="Clear", command=self.clear_filters).grid(row=0, column=6, padx=(10, 0))
        
        # Update filter options
        self.update_filter_options()
    
    def create_inventory_table(self):
        """Create inventory table with treeview"""
        # Table frame
        table_frame = ttk.Frame(self.main_frame)
        table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('ID', 'Name', 'Category', 'Quantity', 'Unit', 'Reorder Level', 
                  'Supplier', 'Expiry Date', 'Status')
        self.inventory_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure columns
        column_widths = {'ID': 50, 'Name': 150, 'Category': 100, 'Quantity': 80, 
                        'Unit': 60, 'Reorder Level': 100, 'Supplier': 120, 
                        'Expiry Date': 100, 'Status': 80}
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.inventory_tree.xview)
        self.inventory_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid
        self.inventory_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Double-click to edit
        self.inventory_tree.bind('<Double-1>', self.edit_item)
    
    def create_buttons_frame(self):
        """Create buttons frame with role-based permissions"""
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
        
        user_role = self.current_user['role']
        
        # Left side buttons (Admin and Clerk only)
        if user_role in ['Admin', 'Clerk']:
            left_frame = ttk.Frame(buttons_frame)
            left_frame.pack(side=tk.LEFT)
            
            if user_role == 'Admin':
                ttk.Button(left_frame, text="Add Item", command=self.add_item_dialog).pack(side=tk.LEFT, padx=5)
                ttk.Button(left_frame, text="Edit Item", command=self.edit_item).pack(side=tk.LEFT, padx=5)
                ttk.Button(left_frame, text="Delete Item", command=self.delete_item).pack(side=tk.LEFT, padx=5)
            elif user_role == 'Clerk':
                ttk.Button(left_frame, text="Add Item", command=self.add_item_dialog).pack(side=tk.LEFT, padx=5)
                ttk.Button(left_frame, text="Edit Item", command=self.edit_item).pack(side=tk.LEFT, padx=5)
        
        # Middle buttons (Stock operations)
        middle_frame = ttk.Frame(buttons_frame)
        middle_frame.pack(side=tk.LEFT, padx=20)
        
        if user_role in ['Admin', 'Clerk']:
            ttk.Button(middle_frame, text="Add Stock", command=self.add_stock_dialog).pack(side=tk.LEFT, padx=5)
        
        # All roles can use stock and view history
        ttk.Button(middle_frame, text="Use Stock", command=self.use_stock_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(middle_frame, text="View History", command=self.view_item_history).pack(side=tk.LEFT, padx=5)
        
        # Right side buttons (All roles)
        right_frame = ttk.Frame(buttons_frame)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Button(right_frame, text="Refresh", command=self.refresh_inventory).pack(side=tk.LEFT, padx=5)
        
        # Add role indicator
        role_frame = ttk.Frame(buttons_frame)
        role_frame.pack(side=tk.RIGHT, padx=20)
        
        role_color = {'Admin': '#e74c3c', 'Clerk': '#3498db', 'Stock User': '#f39c12'}
        ttk.Label(role_frame, text=f"Role: {user_role}", 
                 font=('Arial', 9, 'bold'), 
                 foreground=role_color.get(user_role, '#2c3e50')).pack()
    
    def update_filter_options(self):
        """Update category and supplier filter options"""
        # Categories
        categories = [''] + InventoryManager.get_categories()
        self.category_combo['values'] = categories
        
        # Suppliers
        suppliers = [''] + InventoryManager.get_suppliers()
        self.supplier_combo['values'] = suppliers
    
    def refresh_inventory(self):
        """Refresh inventory display"""
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Load items
        items = InventoryManager.get_all_items()
        
        for item in items:
            # Determine status
            status = "OK"
            tags = []
            
            if item['quantity'] <= item['reorder_level']:
                status = "LOW STOCK"
                tags.append('low_stock')
            
            if item['expiry_date']:
                expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
                days_to_expiry = (expiry_date - date.today()).days
                if days_to_expiry <= 5:
                    status = "EXPIRING" if status == "OK" else f"{status}/EXPIRING"
                    tags.append('expiring')
            
            # Format expiry date
            expiry_display = item['expiry_date'] if item['expiry_date'] else ''
            
            # Insert item
            item_id = self.inventory_tree.insert('', tk.END, values=(
                item['id'],
                item['name'],
                item['category'],
                f"{item['quantity']:.2f}",
                item['unit'],
                f"{item['reorder_level']:.2f}",
                item['supplier'] or '',
                expiry_display,
                status
            ), tags=tags)
        
        # Configure tags
        self.inventory_tree.tag_configure('low_stock', background='#ffcccc')
        self.inventory_tree.tag_configure('expiring', background='#ffffcc')
        
        # Update filter options
        self.update_filter_options()
    
    def search_inventory(self):
        """Search and filter inventory"""
        search_term = self.search_var.get()
        category_filter = self.category_var.get() if self.category_var.get() else None
        supplier_filter = self.supplier_var.get() if self.supplier_var.get() else None
        
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Search items
        items = InventoryManager.search_items(search_term, category_filter, supplier_filter)
        
        for item in items:
            # Determine status (same logic as refresh_inventory)
            status = "OK"
            tags = []
            
            if item['quantity'] <= item['reorder_level']:
                status = "LOW STOCK"
                tags.append('low_stock')
            
            if item['expiry_date']:
                expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
                days_to_expiry = (expiry_date - date.today()).days
                if days_to_expiry <= 5:
                    status = "EXPIRING" if status == "OK" else f"{status}/EXPIRING"
                    tags.append('expiring')
            
            expiry_display = item['expiry_date'] if item['expiry_date'] else ''
            
            self.inventory_tree.insert('', tk.END, values=(
                item['id'],
                item['name'],
                item['category'],
                f"{item['quantity']:.2f}",
                item['unit'],
                f"{item['reorder_level']:.2f}",
                item['supplier'] or '',
                expiry_display,
                status
            ), tags=tags)
        
        # Configure tags
        self.inventory_tree.tag_configure('low_stock', background='#ffcccc')
        self.inventory_tree.tag_configure('expiring', background='#ffffcc')
    
    def clear_filters(self):
        """Clear all filters and search"""
        self.search_var.set('')
        self.category_var.set('')
        self.supplier_var.set('')
        self.refresh_inventory()
    
    def add_item_dialog(self):
        """Show add item dialog"""
        AddItemDialog(self.parent, self.refresh_inventory)
    
    def edit_item(self, event=None):
        """Edit selected item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to edit")
            return
        
        item_id = self.inventory_tree.item(selection[0])['values'][0]
        EditItemDialog(self.parent, item_id, self.refresh_inventory)
    
    def delete_item(self):
        """Delete selected item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to delete")
            return
        
        item_id = self.inventory_tree.item(selection[0])['values'][0]
        item_name = self.inventory_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Delete item '{item_name}'?\n\nThis action cannot be undone."):
            try:
                InventoryManager.delete_item(item_id)
                messagebox.showinfo("Success", "Item deleted successfully")
                self.refresh_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {e}")
    
    def add_stock_dialog(self):
        """Show add stock dialog"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item")
            return
        
        item_id = self.inventory_tree.item(selection[0])['values'][0]
        item_name = self.inventory_tree.item(selection[0])['values'][1]
        
        StockOperationDialog(self.parent, item_id, item_name, "IN", 
                           self.current_user, self.refresh_inventory)
    
    def use_stock_dialog(self):
        """Show use stock dialog"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item")
            return
        
        item_id = self.inventory_tree.item(selection[0])['values'][0]
        item_name = self.inventory_tree.item(selection[0])['values'][1]
        
        StockOperationDialog(self.parent, item_id, item_name, "OUT", 
                           self.current_user, self.refresh_inventory)
    
    def view_item_history(self):
        """View transaction history for selected item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item")
            return
        
        item_id = self.inventory_tree.item(selection[0])['values'][0]
        item_name = self.inventory_tree.item(selection[0])['values'][1]
        
        ItemHistoryDialog(self.parent, item_id, item_name)

class AddItemDialog:
    """Dialog for adding new inventory item"""
    
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.create_dialog()
    
    def create_dialog(self):
        """Create add item dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add New Item")
        self.dialog.geometry("400x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Name
        ttk.Label(main_frame, text="Name *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Category
        ttk.Label(main_frame, text="Category *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, width=27)
        category_combo['values'] = ['Foodstuff', 'Cleaning', 'Toiletries', 'Beverages', 'Office Supplies', 'Maintenance', 'Other']
        category_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Quantity
        ttk.Label(main_frame, text="Initial Quantity *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.quantity_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Unit
        ttk.Label(main_frame, text="Unit *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(main_frame, textvariable=self.unit_var, width=27)
        unit_combo['values'] = ['kg', 'liters', 'packets', 'pieces', 'boxes', 'bottles', 'cans', 'rolls', 'bags']
        unit_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Reorder Level
        ttk.Label(main_frame, text="Reorder Level *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.reorder_var = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.reorder_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Supplier
        ttk.Label(main_frame, text="Supplier:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.supplier_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.supplier_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Expiry Date
        ttk.Label(main_frame, text="Expiry Date:").grid(row=row, column=0, sticky=tk.W, pady=5)
        expiry_frame = ttk.Frame(main_frame)
        expiry_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        self.expiry_var = tk.StringVar()
        ttk.Entry(expiry_frame, textvariable=self.expiry_var, width=20).pack(side=tk.LEFT)
        ttk.Label(expiry_frame, text="(YYYY-MM-DD)").pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        # Required fields note
        ttk.Label(main_frame, text="* Required fields", font=('Arial', 8), 
                 foreground='red').grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Add Item", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_item(self):
        """Add the new item"""
        # Validate required fields
        name = self.name_var.get().strip()
        category = self.category_var.get().strip()
        unit = self.unit_var.get().strip()
        
        if not all([name, category, unit]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        try:
            quantity = float(self.quantity_var.get())
            reorder_level = float(self.reorder_var.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity and reorder level must be numbers")
            return
        
        supplier = self.supplier_var.get().strip() or None
        expiry_date = self.expiry_var.get().strip() or None
        
        # Validate expiry date format
        if expiry_date:
            try:
                datetime.strptime(expiry_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid expiry date format. Use YYYY-MM-DD")
                return
        
        try:
            InventoryManager.add_item(name, category, quantity, unit, reorder_level, supplier, expiry_date)
            messagebox.showinfo("Success", "Item added successfully")
            self.callback()
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {e}")

class EditItemDialog:
    """Dialog for editing existing inventory item"""
    
    def __init__(self, parent, item_id, callback):
        self.parent = parent
        self.item_id = item_id
        self.callback = callback
        self.load_item_data()
        self.create_dialog()
    
    def load_item_data(self):
        """Load existing item data"""
        query = "SELECT * FROM items WHERE id = ?"
        result = db_manager.execute_query(query, (self.item_id,))
        if result:
            self.item_data = result[0]
        else:
            messagebox.showerror("Error", "Item not found")
            return
    
    def create_dialog(self):
        """Create edit item dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Edit Item - {self.item_data['name']}")
        self.dialog.geometry("400x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Name
        ttk.Label(main_frame, text="Name *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.item_data['name'])
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Category
        ttk.Label(main_frame, text="Category *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(value=self.item_data['category'])
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, width=27)
        category_combo['values'] = ['Foodstuff', 'Cleaning', 'Toiletries', 'Beverages', 'Office Supplies', 'Maintenance', 'Other']
        category_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Quantity
        ttk.Label(main_frame, text="Current Quantity *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar(value=str(self.item_data['quantity']))
        ttk.Entry(main_frame, textvariable=self.quantity_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Unit
        ttk.Label(main_frame, text="Unit *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.unit_var = tk.StringVar(value=self.item_data['unit'])
        unit_combo = ttk.Combobox(main_frame, textvariable=self.unit_var, width=27)
        unit_combo['values'] = ['kg', 'liters', 'packets', 'pieces', 'boxes', 'bottles', 'cans', 'rolls', 'bags']
        unit_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Reorder Level
        ttk.Label(main_frame, text="Reorder Level *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.reorder_var = tk.StringVar(value=str(self.item_data['reorder_level']))
        ttk.Entry(main_frame, textvariable=self.reorder_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Supplier
        ttk.Label(main_frame, text="Supplier:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.supplier_var = tk.StringVar(value=self.item_data['supplier'] or '')
        ttk.Entry(main_frame, textvariable=self.supplier_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Expiry Date
        ttk.Label(main_frame, text="Expiry Date:").grid(row=row, column=0, sticky=tk.W, pady=5)
        expiry_frame = ttk.Frame(main_frame)
        expiry_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        self.expiry_var = tk.StringVar(value=self.item_data['expiry_date'] or '')
        ttk.Entry(expiry_frame, textvariable=self.expiry_var, width=20).pack(side=tk.LEFT)
        ttk.Label(expiry_frame, text="(YYYY-MM-DD)").pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        # Required fields note
        ttk.Label(main_frame, text="* Required fields", font=('Arial', 8), 
                 foreground='red').grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Update Item", command=self.update_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def update_item(self):
        """Update the item"""
        # Validate required fields
        name = self.name_var.get().strip()
        category = self.category_var.get().strip()
        unit = self.unit_var.get().strip()
        
        if not all([name, category, unit]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        try:
            quantity = float(self.quantity_var.get())
            reorder_level = float(self.reorder_var.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity and reorder level must be numbers")
            return
        
        supplier = self.supplier_var.get().strip() or None
        expiry_date = self.expiry_var.get().strip() or None
        
        # Validate expiry date format
        if expiry_date:
            try:
                datetime.strptime(expiry_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid expiry date format. Use YYYY-MM-DD")
                return
        
        try:
            InventoryManager.update_item(self.item_id, name, category, quantity, unit, 
                                       reorder_level, supplier, expiry_date)
            messagebox.showinfo("Success", "Item updated successfully")
            self.callback()
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update item: {e}")

class StockOperationDialog:
    """Dialog for stock operations (IN/OUT)"""
    
    def __init__(self, parent, item_id, item_name, operation_type, current_user, callback):
        self.parent = parent
        self.item_id = item_id
        self.item_name = item_name
        self.operation_type = operation_type  # 'IN' or 'OUT'
        self.current_user = current_user
        self.callback = callback
        self.create_dialog()
    
    def create_dialog(self):
        """Create stock operation dialog"""
        title = f"{'Add' if self.operation_type == 'IN' else 'Use'} Stock - {self.item_name}"
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("350x250")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Item info
        ttk.Label(main_frame, text="Item:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=self.item_name).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Current stock
        current_stock = self.get_current_stock()
        ttk.Label(main_frame, text="Current Stock:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=f"{current_stock:.2f}").grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Quantity
        operation_text = "Add Quantity:" if self.operation_type == 'IN' else "Use Quantity:"
        ttk.Label(main_frame, text=operation_text).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.quantity_var, width=20).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Notes
        ttk.Label(main_frame, text="Notes:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.notes_var, width=20).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        button_text = "Add Stock" if self.operation_type == 'IN' else "Use Stock"
        ttk.Button(buttons_frame, text=button_text, command=self.perform_operation).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on quantity entry
        self.quantity_var.trace('w', self.update_preview)
        self.preview_label = ttk.Label(main_frame, text="", foreground='blue')
        self.preview_label.grid(row=5, column=0, columnspan=2, pady=5)
    
    def get_current_stock(self):
        """Get current stock for the item"""
        query = "SELECT quantity FROM items WHERE id = ?"
        result = db_manager.execute_query(query, (self.item_id,))
        return result[0][0] if result else 0
    
    def update_preview(self, *args):
        """Update preview of new stock level"""
        try:
            quantity = float(self.quantity_var.get())
            current_stock = self.get_current_stock()
            
            if self.operation_type == 'IN':
                new_stock = current_stock + quantity
                self.preview_label.config(text=f"New stock will be: {new_stock:.2f}")
            else:
                new_stock = current_stock - quantity
                if new_stock < 0:
                    self.preview_label.config(text=f"Insufficient stock! Available: {current_stock:.2f}", 
                                            foreground='red')
                else:
                    self.preview_label.config(text=f"New stock will be: {new_stock:.2f}", 
                                            foreground='blue')
        except ValueError:
            self.preview_label.config(text="")
    
    def perform_operation(self):
        """Perform the stock operation"""
        try:
            quantity = float(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
            return
        
        notes = self.notes_var.get().strip() or None
        
        try:
            if self.operation_type == 'IN':
                StockManager.add_stock(self.current_user['id'], self.item_id, quantity, notes)
                messagebox.showinfo("Success", f"Added {quantity} units to stock")
            else:
                StockManager.use_stock(self.current_user['id'], self.item_id, quantity, notes)
                messagebox.showinfo("Success", f"Used {quantity} units from stock")
            
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Operation failed: {e}")

class ItemHistoryDialog:
    """Dialog to view item transaction history"""
    
    def __init__(self, parent, item_id, item_name):
        self.parent = parent
        self.item_id = item_id
        self.item_name = item_name
        self.create_dialog()
    
    def create_dialog(self):
        """Create item history dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Transaction History - {self.item_name}")
        self.dialog.geometry("700x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        ttk.Label(main_frame, text=f"Transaction History: {self.item_name}", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, pady=(0, 10))
        
        # History table
        self.create_history_table(main_frame)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).grid(row=2, column=0, pady=10)
        
        # Load history
        self.load_history()
    
    def create_history_table(self, parent):
        """Create history table"""
        # Table frame
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('Date/Time', 'Type', 'Quantity', 'User', 'Notes')
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure columns
        self.history_tree.heading('Date/Time', text='Date/Time')
        self.history_tree.heading('Type', text='Type')
        self.history_tree.heading('Quantity', text='Quantity')
        self.history_tree.heading('User', text='User')
        self.history_tree.heading('Notes', text='Notes')
        
        self.history_tree.column('Date/Time', width=150)
        self.history_tree.column('Type', width=60)
        self.history_tree.column('Quantity', width=80)
        self.history_tree.column('User', width=100)
        self.history_tree.column('Notes', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def load_history(self):
        """Load transaction history"""
        transactions = StockManager.get_item_transactions(self.item_id)
        
        for trans in transactions:
            # Format date/time
            date_time = trans['date_time'][:19]  # Remove microseconds
            
            # Color code by type
            tags = ['in_transaction'] if trans['type'] == 'IN' else ['out_transaction']
            
            self.history_tree.insert('', tk.END, values=(
                date_time,
                trans['type'],
                f"{trans['quantity']:.2f}",
                trans['username'],
                trans['notes'] or ''
            ), tags=tags)
        
        # Configure tags
        self.history_tree.tag_configure('in_transaction', background='#e6ffe6')
        self.history_tree.tag_configure('out_transaction', background='#ffe6e6')

if __name__ == "__main__":
    # Test inventory window
    root = tk.Tk()
    root.title("Test Inventory")
    
    # Mock user
    current_user = {'id': 1, 'username': 'admin', 'role': 'Admin'}
    
    # Initialize database
    from db import initialize_database
    initialize_database()
    
    # Create inventory window
    inventory_window = InventoryWindow(root, current_user)
    
    root.mainloop()