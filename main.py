"""
Main application entry point for Hotel Inventory Management System
Handles application startup, main window, and navigation between modules
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from datetime import datetime
import logging

# Import application modules
from db import initialize_database, db_manager
from login import LoginWindow, UserManagementDialog
from inventory import InventoryWindow
from alerts import AlertsWindow, AutoAlertChecker, AlertManager
from reports import ReportsWindow
from ui_theme import madit_theme

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hotel_inventory.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HotelInventoryApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize the main application"""
        self.current_user = None
        self.config = self.load_config()
        
        # Initialize database
        try:
            initialize_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            sys.exit(1)
        
        # Show login window
        self.show_login()
    
    def load_config(self):
        """Load application configuration"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Config file not found, using defaults")
            return {
                "app_title": "Hotel Inventory Management System",
                "version": "1.0.0",
                "company_name": "Hotel Management Solutions"
            }
    
    def show_login(self):
        """Show login window"""
        login_window = LoginWindow(self.on_login_success)
        self.current_user = login_window.run()
        
        if self.current_user:
            self.create_main_window()
        else:
            logger.info("Login cancelled or failed")
            sys.exit(0)
    
    def on_login_success(self, user):
        """Handle successful login"""
        self.current_user = user
        logger.info(f"User {user['username']} logged in successfully")
    
    def create_main_window(self):
        """Create the main application window"""
        self.root = tk.Tk()
        self.root.title(f"{self.config.get('app_title', 'Madit Hotel Inventory')} - {self.current_user['username']} ({self.current_user['role']})")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # Maximize window on Windows
        
        # Apply Madit Hotel theme
        self.style = madit_theme.apply_theme(self.root)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main interface
        self.create_main_interface()
        
        # Initialize auto alert checker
        self.alert_manager = AlertManager()
        self.auto_alert_checker = AutoAlertChecker(self.root, self.alert_manager)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Show welcome message
        self.show_welcome_message()
        
        # Start main loop
        self.root.mainloop()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_command(label="Restore Database", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Inventory menu
        inventory_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Inventory", menu=inventory_menu)
        inventory_menu.add_command(label="Manage Items", command=lambda: self.show_tab("Inventory"))
        inventory_menu.add_command(label="View Alerts", command=lambda: self.show_tab("Alerts"))
        
        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Dashboard", command=lambda: self.show_tab("Reports"))
        reports_menu.add_command(label="Usage Reports", command=self.show_usage_reports)
        reports_menu.add_command(label="Export Data", command=self.show_export_options)
        
        # Admin menu (only for admin users)
        if self.current_user['role'] == 'Admin':
            admin_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Admin", menu=admin_menu)
            admin_menu.add_command(label="Manage Users", command=self.manage_users)
            admin_menu.add_command(label="System Settings", command=self.show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
    
    def create_main_interface(self):
        """Create the main application interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header frame
        header_frame = madit_theme.create_gradient_frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status bar
        self.create_status_bar(main_frame)
        
        # Main notebook for different modules
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Dashboard tab
        self.create_dashboard_tab()
        
        # Inventory tab
        self.create_inventory_tab()
        
        # Alerts tab
        self.create_alerts_tab()
        
        # Reports tab
        self.create_reports_tab()
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        status_frame.columnconfigure(1, weight=1)
        
        # User info
        user_info = f"Logged in as: {self.current_user['username']} ({self.current_user['role']})"
        ttk.Label(status_frame, text=user_info, font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        
        # Current time
        self.time_label = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.time_label.grid(row=0, column=2, sticky=tk.E)
        
        # Update time
        self.update_time()
    
    def update_time(self):
        """Update current time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Configure grid
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.rowconfigure(0, weight=1)
        
        # Create dashboard content
        self.create_dashboard_content(dashboard_frame)
    
    def create_dashboard_content(self, parent):
        """Create dashboard content"""
        # Main container
        container = ttk.Frame(parent, padding="20")
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container.columnconfigure(0, weight=1)
        
        # Welcome section with role-specific styling
        welcome_frame = ttk.LabelFrame(container, text="Welcome to Madit Hotel", padding="15")
        welcome_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        welcome_text = f"Welcome back, {self.current_user['username']}!"
        ttk.Label(welcome_frame, text=welcome_text, font=('Arial', 14, 'bold')).pack()
        
        role_color = madit_theme.get_role_color(self.current_user['role'])
        role_text = f"Role: {self.current_user['role']}"
        role_label = tk.Label(welcome_frame, text=role_text, font=('Arial', 11, 'bold'), 
                             fg=role_color, bg=welcome_frame.cget('background'))
        role_label.pack(pady=(5, 0))
        
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        ttk.Label(welcome_frame, text=current_date, font=('Arial', 10)).pack(pady=(5, 0))
        
        # Role-specific permissions info
        permissions = {
            'Admin': "Full system access • Manage users • All operations",
            'Clerk': "Manage inventory • Stock operations • View reports", 
            'Stock User': "Remove stock only • View inventory • Limited access"
        }
        perm_text = permissions.get(self.current_user['role'], "")
        ttk.Label(welcome_frame, text=perm_text, font=('Arial', 9), 
                 foreground='gray').pack(pady=(5, 0))
        
        # Quick stats
        stats_frame = ttk.LabelFrame(container, text="Quick Statistics", padding="15")
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Configure stats grid
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)
        
        # Get statistics
        self.update_dashboard_stats(stats_frame)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(container, text="Quick Actions", padding="15")
        actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Configure actions grid
        for i in range(3):
            actions_frame.columnconfigure(i, weight=1)
        
        # Action buttons
        ttk.Button(actions_frame, text="View Inventory", 
                  command=lambda: self.show_tab("Inventory")).grid(row=0, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(actions_frame, text="Check Alerts", 
                  command=lambda: self.show_tab("Alerts")).grid(row=0, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(actions_frame, text="Generate Reports", 
                  command=lambda: self.show_tab("Reports")).grid(row=0, column=2, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        # Recent activity (placeholder)
        activity_frame = ttk.LabelFrame(container, text="Recent Activity", padding="15")
        activity_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        activity_frame.columnconfigure(0, weight=1)
        activity_frame.rowconfigure(0, weight=1)
        
        # Activity list
        self.create_recent_activity(activity_frame)
    
    def update_dashboard_stats(self, parent):
        """Update dashboard statistics"""
        try:
            # Get inventory summary
            summary_query = '''
                SELECT 
                    COUNT(*) as total_items,
                    SUM(CASE WHEN quantity <= reorder_level THEN 1 ELSE 0 END) as low_stock_items,
                    COUNT(CASE WHEN expiry_date IS NOT NULL AND expiry_date <= date('now', '+5 days') THEN 1 END) as expiring_items
                FROM items
            '''
            summary = db_manager.execute_query(summary_query)[0]
            
            # Get most used item (last 7 days)
            most_used_query = '''
                SELECT i.name, SUM(t.quantity) as total_used
                FROM items i
                JOIN transactions t ON i.id = t.item_id
                WHERE t.type = 'OUT' AND t.date_time >= date('now', '-7 days')
                GROUP BY i.id, i.name
                ORDER BY total_used DESC
                LIMIT 1
            '''
            most_used_result = db_manager.execute_query(most_used_query)
            most_used = most_used_result[0]['name'] if most_used_result else "N/A"
            
            # Create stat cards
            stats = [
                ("Total Items", summary[0], 'blue'),
                ("Low Stock", summary[1], 'red'),
                ("Expiring Soon", summary[2], 'orange'),
                ("Most Used (7d)", most_used, 'green')
            ]
            
            for i, (label, value, color) in enumerate(stats):
                card_frame = ttk.Frame(parent, relief='raised', borderwidth=2)
                card_frame.grid(row=0, column=i, padx=10, pady=10, sticky=(tk.W, tk.E))
                card_frame.columnconfigure(0, weight=1)
                
                ttk.Label(card_frame, text=label, font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
                
                if isinstance(value, str):
                    display_value = value[:15] + "..." if len(str(value)) > 15 else str(value)
                    font_size = 12
                else:
                    display_value = str(value)
                    font_size = 20
                
                ttk.Label(card_frame, text=display_value, 
                         font=('Arial', font_size, 'bold'), foreground=color).grid(row=1, column=0, pady=5)
                
        except Exception as e:
            logger.error(f"Error updating dashboard stats: {e}")
    
    def create_recent_activity(self, parent):
        """Create recent activity list"""
        # Activity treeview
        columns = ('Time', 'Action', 'Item', 'User')
        activity_tree = ttk.Treeview(parent, columns=columns, show='headings', height=8)
        
        # Configure columns
        activity_tree.heading('Time', text='Time')
        activity_tree.heading('Action', text='Action')
        activity_tree.heading('Item', text='Item')
        activity_tree.heading('User', text='User')
        
        activity_tree.column('Time', width=120)
        activity_tree.column('Action', width=80)
        activity_tree.column('Item', width=200)
        activity_tree.column('User', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=activity_tree.yview)
        activity_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        activity_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Load recent transactions
        try:
            recent_query = '''
                SELECT t.date_time, t.type, i.name, u.username
                FROM transactions t
                JOIN items i ON t.item_id = i.id
                JOIN users u ON t.user_id = u.id
                ORDER BY t.date_time DESC
                LIMIT 20
            '''
            recent_transactions = db_manager.execute_query(recent_query)
            
            for trans in recent_transactions:
                time_str = trans['date_time'][:16]  # Remove seconds
                action = "Stock In" if trans['type'] == 'IN' else "Stock Out"
                
                activity_tree.insert('', tk.END, values=(
                    time_str,
                    action,
                    trans['name'],
                    trans['username']
                ))
                
        except Exception as e:
            logger.error(f"Error loading recent activity: {e}")
    
    def create_inventory_tab(self):
        """Create inventory management tab"""
        inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_frame, text="Inventory")
        
        # Create inventory window
        self.inventory_window = InventoryWindow(inventory_frame, self.current_user)
    
    def create_alerts_tab(self):
        """Create alerts tab"""
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="Alerts")
        
        # Create alerts window
        self.alerts_window = AlertsWindow(alerts_frame, self.current_user)
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Create reports window
        self.reports_window = ReportsWindow(reports_frame, self.current_user)
    
    def show_tab(self, tab_name):
        """Show specific tab"""
        tab_mapping = {
            "Dashboard": 0,
            "Inventory": 1,
            "Alerts": 2,
            "Reports": 3
        }
        
        if tab_name in tab_mapping:
            self.notebook.select(tab_mapping[tab_name])
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        logger.info(f"Switched to {selected_tab} tab")
        
        # Refresh data when switching to certain tabs
        if selected_tab == "Alerts":
            self.alerts_window.refresh_alerts()
        elif selected_tab == "Reports":
            self.reports_window.refresh_dashboard()
    
    def show_welcome_message(self):
        """Show welcome message on first run"""
        # Check if this is first run (no items in database)
        try:
            item_count = db_manager.execute_query("SELECT COUNT(*) FROM items")[0][0]
            if item_count == 0:
                welcome_msg = """Welcome to the Hotel Inventory Management System!

This appears to be your first time using the system. Here are some quick tips to get started:

1. Go to the Inventory tab to add your first items
2. Set appropriate reorder levels for low stock alerts
3. Use the Reports tab to analyze your inventory data
4. Check the Alerts tab regularly for low stock and expiring items

For detailed instructions, use Help > User Guide from the menu.

Would you like to add your first inventory item now?"""
                
                if messagebox.askyesno("Welcome!", welcome_msg):
                    self.show_tab("Inventory")
                    
        except Exception as e:
            logger.error(f"Error checking first run: {e}")
    
    def backup_database(self):
        """Backup database"""
        try:
            backup_path = db_manager.backup_database()
            messagebox.showinfo("Backup Successful", f"Database backed up to:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Failed to backup database:\n{e}")
    
    def restore_database(self):
        """Restore database from backup"""
        from tkinter import filedialog
        
        backup_file = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if backup_file:
            if messagebox.askyesno("Confirm Restore", 
                                 "This will replace the current database with the backup.\n"
                                 "Are you sure you want to continue?"):
                try:
                    db_manager.restore_database(backup_file)
                    messagebox.showinfo("Restore Successful", 
                                      "Database restored successfully.\n"
                                      "Please restart the application.")
                    self.on_closing()
                except Exception as e:
                    messagebox.showerror("Restore Failed", f"Failed to restore database:\n{e}")
    
    def manage_users(self):
        """Open user management dialog"""
        UserManagementDialog(self.root, self.current_user)
    
    def show_settings(self):
        """Show system settings"""
        SettingsDialog(self.root, self.config)
    
    def show_usage_reports(self):
        """Show usage reports tab"""
        self.show_tab("Reports")
        # Switch to usage reports tab within reports
        if hasattr(self.reports_window, 'notebook'):
            self.reports_window.notebook.select(1)  # Usage reports tab
    
    def show_export_options(self):
        """Show export options tab"""
        self.show_tab("Reports")
        # Switch to export tab within reports
        if hasattr(self.reports_window, 'notebook'):
            self.reports_window.notebook.select(3)  # Export tab
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""{self.config.get('app_title', 'Hotel Inventory Management System')}
Version: {self.config.get('version', '1.0.0')}

A comprehensive inventory management solution for hotels and hospitality businesses.

Features:
• Complete inventory tracking
• Low stock and expiry alerts
• Usage reports and analytics
• User management and access control
• Data backup and restore
• Export capabilities

Developed by: {self.config.get('company_name', 'Hotel Management Solutions')}
© 2024 All rights reserved."""
        
        messagebox.showinfo("About", about_text)
    
    def show_user_guide(self):
        """Show user guide"""
        guide_text = """Hotel Inventory Management System - User Guide

GETTING STARTED:
1. Login with your username and password
2. Default admin credentials: admin / admin123

INVENTORY MANAGEMENT:
• Add items: Click "Add Item" in Inventory tab
• Update stock: Select item and click "Add Stock" or "Use Stock"
• Edit items: Double-click item or use "Edit Item" button
• Search: Use search box to find items quickly

ALERTS:
• Low stock alerts appear when quantity ≤ reorder level
• Expiry alerts show items expiring within 5 days
• Check Alerts tab regularly for notifications

REPORTS:
• Dashboard: Overview of inventory status
• Usage Reports: Track item consumption over time
• Analytics: Category and supplier analysis
• Export: Save data to CSV or PDF files

ADMIN FUNCTIONS:
• Manage Users: Add/edit/delete user accounts
• Backup/Restore: Protect your data
• Settings: Configure system preferences

For technical support, contact your system administrator."""
        
        # Create a scrollable text window for the guide
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("600x500")
        guide_window.transient(self.root)
        
        text_frame = ttk.Frame(guide_window, padding="10")
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        guide_window.columnconfigure(0, weight=1)
        guide_window.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(text_frame, text="Close", 
                  command=guide_window.destroy).grid(row=1, column=0, pady=10)
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            logger.info(f"User {self.current_user['username']} logged out")
            db_manager.disconnect()
            self.root.destroy()

class SettingsDialog:
    """System settings dialog"""
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.create_dialog()
    
    def create_dialog(self):
        """Create settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("System Settings")
        self.dialog.geometry("400x300")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Settings
        row = 0
        
        # App title
        ttk.Label(main_frame, text="Application Title:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.app_title_var = tk.StringVar(value=self.config.get('app_title', ''))
        ttk.Entry(main_frame, textvariable=self.app_title_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Company name
        ttk.Label(main_frame, text="Company Name:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.company_var = tk.StringVar(value=self.config.get('company_name', ''))
        ttk.Entry(main_frame, textvariable=self.company_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Backup path
        ttk.Label(main_frame, text="Backup Path:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.backup_path_var = tk.StringVar(value=self.config.get('backup_path', './backups'))
        ttk.Entry(main_frame, textvariable=self.backup_path_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Export path
        ttk.Label(main_frame, text="Export Path:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.export_path_var = tk.StringVar(value=self.config.get('report_export_path', './reports'))
        ttk.Entry(main_frame, textvariable=self.export_path_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Alert settings
        ttk.Label(main_frame, text="Expiry Alert Days:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.expiry_days_var = tk.StringVar(value=str(self.config.get('expiry_alert_days', 5)))
        ttk.Entry(main_frame, textvariable=self.expiry_days_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Sound alerts
        self.sound_var = tk.BooleanVar(value=self.config.get('alert_sound_enabled', True))
        ttk.Checkbutton(main_frame, text="Enable Alert Sounds", 
                       variable=self.sound_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        row += 1
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_settings(self):
        """Save settings to config file"""
        try:
            # Update config
            self.config['app_title'] = self.app_title_var.get()
            self.config['company_name'] = self.company_var.get()
            self.config['backup_path'] = self.backup_path_var.get()
            self.config['report_export_path'] = self.export_path_var.get()
            self.config['expiry_alert_days'] = int(self.expiry_days_var.get())
            self.config['alert_sound_enabled'] = self.sound_var.get()
            
            # Save to file
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
            
            messagebox.showinfo("Success", "Settings saved successfully.\nRestart the application to apply changes.")
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid expiry alert days. Please enter a number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

def main():
    """Main application entry point"""
    try:
        # Create application instance
        app = HotelInventoryApp()
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()