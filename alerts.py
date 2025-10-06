"""
Alerts module for Hotel Inventory Management System
Handles low stock alerts, expiry alerts, and notification system
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from db import db_manager
from inventory import InventoryManager
import json
import logging

# Try to import playsound for audio alerts
try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    print("Warning: playsound not available. Audio alerts disabled.")

logger = logging.getLogger(__name__)

class AlertManager:
    """Manage all types of alerts and notifications"""
    
    def __init__(self, config_file='config.json'):
        """Initialize alert manager with configuration"""
        self.config = self.load_config(config_file)
        self.sound_enabled = self.config.get('alert_sound_enabled', True) and SOUND_AVAILABLE
        self.expiry_alert_days = self.config.get('expiry_alert_days', 5)
    
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "alert_sound_enabled": True,
                "expiry_alert_days": 5
            }
    
    def play_alert_sound(self):
        """Play alert sound if enabled"""
        if self.sound_enabled:
            try:
                # You can replace this with a custom sound file
                # For now, we'll use the system beep
                print('\a')  # System beep
                # Uncomment below if you have a sound file
                # playsound('alert.wav', block=False)
            except Exception as e:
                logger.warning(f"Could not play alert sound: {e}")
    
    def get_low_stock_items(self):
        """Get items with stock below reorder level"""
        return InventoryManager.get_low_stock_items()
    
    def get_expiring_items(self, days=None):
        """Get items expiring within specified days"""
        if days is None:
            days = self.expiry_alert_days
        return InventoryManager.get_expiring_items(days)
    
    def check_all_alerts(self):
        """Check all alert conditions and return summary"""
        low_stock_items = self.get_low_stock_items()
        expiring_items = self.get_expiring_items()
        
        alerts = {
            'low_stock': low_stock_items,
            'expiring': expiring_items,
            'total_alerts': len(low_stock_items) + len(expiring_items)
        }
        
        return alerts
    
    def show_alert_popup(self, parent=None):
        """Show popup with current alerts"""
        alerts = self.check_all_alerts()
        
        if alerts['total_alerts'] == 0:
            messagebox.showinfo("Alerts", "No alerts at this time.")
            return
        
        # Play sound if there are alerts
        if alerts['total_alerts'] > 0:
            self.play_alert_sound()
        
        # Show alert dialog
        AlertDialog(parent, alerts)

class AlertDialog:
    """Dialog to display current alerts"""
    
    def __init__(self, parent, alerts):
        self.parent = parent
        self.alerts = alerts
        self.create_dialog()
    
    def create_dialog(self):
        """Create alert dialog"""
        self.dialog = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.dialog.title("Inventory Alerts")
        self.dialog.geometry("600x400")
        
        if self.parent:
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
        title_text = f"Inventory Alerts ({self.alerts['total_alerts']} items need attention)"
        ttk.Label(main_frame, text=title_text, font=('Arial', 14, 'bold'), 
                 foreground='red').grid(row=0, column=0, pady=(0, 10))
        
        # Notebook for different alert types
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Low stock tab
        if self.alerts['low_stock']:
            low_stock_frame = ttk.Frame(notebook)
            notebook.add(low_stock_frame, text=f"Low Stock ({len(self.alerts['low_stock'])})")
            self.create_low_stock_tab(low_stock_frame)
        
        # Expiring items tab
        if self.alerts['expiring']:
            expiring_frame = ttk.Frame(notebook)
            notebook.add(expiring_frame, text=f"Expiring Soon ({len(self.alerts['expiring'])})")
            self.create_expiring_tab(expiring_frame)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).grid(row=2, column=0, pady=10)
    
    def create_low_stock_tab(self, parent):
        """Create low stock items tab"""
        # Frame for table
        table_frame = ttk.Frame(parent, padding="10")
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('Name', 'Category', 'Current Stock', 'Reorder Level', 'Supplier')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Populate data
        for item in self.alerts['low_stock']:
            tree.insert('', tk.END, values=(
                item['name'],
                item['category'],
                f"{item['quantity']:.2f} {item['unit']}",
                f"{item['reorder_level']:.2f} {item['unit']}",
                item['supplier'] or 'N/A'
            ))
        
        # Configure row colors
        tree.tag_configure('low_stock', background='#ffcccc')
        for child in tree.get_children():
            tree.set(child, tags=('low_stock',))
    
    def create_expiring_tab(self, parent):
        """Create expiring items tab"""
        # Frame for table
        table_frame = ttk.Frame(parent, padding="10")
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('Name', 'Category', 'Expiry Date', 'Days Left', 'Current Stock')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Populate data
        today = date.today()
        for item in self.alerts['expiring']:
            expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - today).days
            
            # Determine tag based on urgency
            if days_left <= 0:
                tag = 'expired'
            elif days_left <= 2:
                tag = 'critical'
            else:
                tag = 'warning'
            
            tree.insert('', tk.END, values=(
                item['name'],
                item['category'],
                item['expiry_date'],
                f"{days_left} days" if days_left > 0 else "EXPIRED",
                f"{item['quantity']:.2f} {item['unit']}"
            ), tags=(tag,))
        
        # Configure row colors
        tree.tag_configure('expired', background='#ff9999')
        tree.tag_configure('critical', background='#ffcc99')
        tree.tag_configure('warning', background='#ffffcc')

class AlertsWindow:
    """Main alerts management window"""
    
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        self.alert_manager = AlertManager()
        self.create_alerts_interface()
    
    def create_alerts_interface(self):
        """Create the alerts interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Inventory Alerts", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Alert summary
        self.create_alert_summary()
        
        # Alert details
        self.create_alert_details()
        
        # Buttons
        self.create_buttons_frame()
        
        # Load alerts
        self.refresh_alerts()
    
    def create_alert_summary(self):
        """Create alert summary cards"""
        summary_frame = ttk.LabelFrame(self.main_frame, text="Alert Summary", padding="10")
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configure grid
        for i in range(3):
            summary_frame.columnconfigure(i, weight=1)
        
        # Low stock card
        low_stock_frame = ttk.Frame(summary_frame, relief='raised', borderwidth=2)
        low_stock_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        low_stock_frame.columnconfigure(0, weight=1)
        
        ttk.Label(low_stock_frame, text="Low Stock Items", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
        self.low_stock_count_label = ttk.Label(low_stock_frame, text="0", 
                                              font=('Arial', 20, 'bold'), foreground='red')
        self.low_stock_count_label.grid(row=1, column=0, pady=5)
        
        # Expiring items card
        expiring_frame = ttk.Frame(summary_frame, relief='raised', borderwidth=2)
        expiring_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        expiring_frame.columnconfigure(0, weight=1)
        
        ttk.Label(expiring_frame, text="Expiring Soon", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
        self.expiring_count_label = ttk.Label(expiring_frame, text="0", 
                                             font=('Arial', 20, 'bold'), foreground='orange')
        self.expiring_count_label.grid(row=1, column=0, pady=5)
        
        # Total alerts card
        total_frame = ttk.Frame(summary_frame, relief='raised', borderwidth=2)
        total_frame.grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        total_frame.columnconfigure(0, weight=1)
        
        ttk.Label(total_frame, text="Total Alerts", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
        self.total_alerts_label = ttk.Label(total_frame, text="0", 
                                           font=('Arial', 20, 'bold'), foreground='blue')
        self.total_alerts_label.grid(row=1, column=0, pady=5)
    
    def create_alert_details(self):
        """Create detailed alerts view"""
        details_frame = ttk.LabelFrame(self.main_frame, text="Alert Details", padding="10")
        details_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        # Notebook for different alert types
        self.notebook = ttk.Notebook(details_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Low stock tab
        self.low_stock_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.low_stock_frame, text="Low Stock")
        self.create_low_stock_table()
        
        # Expiring items tab
        self.expiring_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.expiring_frame, text="Expiring Soon")
        self.create_expiring_table()
    
    def create_low_stock_table(self):
        """Create low stock items table"""
        # Table frame
        table_frame = ttk.Frame(self.low_stock_frame, padding="5")
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('Name', 'Category', 'Current Stock', 'Reorder Level', 'Supplier', 'Last Updated')
        self.low_stock_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure columns
        column_widths = {'Name': 150, 'Category': 100, 'Current Stock': 100, 
                        'Reorder Level': 100, 'Supplier': 120, 'Last Updated': 120}
        
        for col in columns:
            self.low_stock_tree.heading(col, text=col)
            self.low_stock_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar1 = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.low_stock_tree.yview)
        self.low_stock_tree.configure(yscrollcommand=scrollbar1.set)
        
        # Grid
        self.low_stock_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar1.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def create_expiring_table(self):
        """Create expiring items table"""
        # Table frame
        table_frame = ttk.Frame(self.expiring_frame, padding="5")
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('Name', 'Category', 'Expiry Date', 'Days Left', 'Current Stock', 'Supplier')
        self.expiring_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure columns
        column_widths = {'Name': 150, 'Category': 100, 'Expiry Date': 100, 
                        'Days Left': 80, 'Current Stock': 100, 'Supplier': 120}
        
        for col in columns:
            self.expiring_tree.heading(col, text=col)
            self.expiring_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar2 = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.expiring_tree.yview)
        self.expiring_tree.configure(yscrollcommand=scrollbar2.set)
        
        # Grid
        self.expiring_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar2.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def create_buttons_frame(self):
        """Create buttons frame"""
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Left side buttons
        left_frame = ttk.Frame(buttons_frame)
        left_frame.pack(side=tk.LEFT)
        
        ttk.Button(left_frame, text="Refresh Alerts", command=self.refresh_alerts).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_frame, text="Show Alert Popup", command=self.show_alert_popup).pack(side=tk.LEFT, padx=5)
        
        # Right side buttons
        right_frame = ttk.Frame(buttons_frame)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Button(right_frame, text="Alert Settings", command=self.show_alert_settings).pack(side=tk.LEFT, padx=5)
    
    def refresh_alerts(self):
        """Refresh all alerts"""
        alerts = self.alert_manager.check_all_alerts()
        
        # Update summary
        self.low_stock_count_label.config(text=str(len(alerts['low_stock'])))
        self.expiring_count_label.config(text=str(len(alerts['expiring'])))
        self.total_alerts_label.config(text=str(alerts['total_alerts']))
        
        # Update low stock table
        for item in self.low_stock_tree.get_children():
            self.low_stock_tree.delete(item)
        
        for item in alerts['low_stock']:
            self.low_stock_tree.insert('', tk.END, values=(
                item['name'],
                item['category'],
                f"{item['quantity']:.2f} {item['unit']}",
                f"{item['reorder_level']:.2f} {item['unit']}",
                item['supplier'] or 'N/A',
                item['updated_date'][:10] if item['updated_date'] else 'N/A'
            ), tags=('low_stock',))
        
        # Update expiring table
        for item in self.expiring_tree.get_children():
            self.expiring_tree.delete(item)
        
        today = date.today()
        for item in alerts['expiring']:
            expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - today).days
            
            # Determine tag based on urgency
            if days_left <= 0:
                tag = 'expired'
            elif days_left <= 2:
                tag = 'critical'
            else:
                tag = 'warning'
            
            self.expiring_tree.insert('', tk.END, values=(
                item['name'],
                item['category'],
                item['expiry_date'],
                f"{days_left} days" if days_left > 0 else "EXPIRED",
                f"{item['quantity']:.2f} {item['unit']}",
                item['supplier'] or 'N/A'
            ), tags=(tag,))
        
        # Configure tags
        self.low_stock_tree.tag_configure('low_stock', background='#ffcccc')
        self.expiring_tree.tag_configure('expired', background='#ff9999')
        self.expiring_tree.tag_configure('critical', background='#ffcc99')
        self.expiring_tree.tag_configure('warning', background='#ffffcc')
    
    def show_alert_popup(self):
        """Show alert popup dialog"""
        self.alert_manager.show_alert_popup(self.parent)
    
    def show_alert_settings(self):
        """Show alert settings dialog"""
        AlertSettingsDialog(self.parent, self.alert_manager)

class AlertSettingsDialog:
    """Dialog for configuring alert settings"""
    
    def __init__(self, parent, alert_manager):
        self.parent = parent
        self.alert_manager = alert_manager
        self.create_dialog()
    
    def create_dialog(self):
        """Create alert settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Alert Settings")
        self.dialog.geometry("350x200")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Sound alerts
        ttk.Label(main_frame, text="Sound Alerts:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sound_var = tk.BooleanVar(value=self.alert_manager.sound_enabled)
        sound_check = ttk.Checkbutton(main_frame, variable=self.sound_var)
        sound_check.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        if not SOUND_AVAILABLE:
            sound_check.config(state='disabled')
            ttk.Label(main_frame, text="(Sound library not available)", 
                     font=('Arial', 8), foreground='gray').grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        # Expiry alert days
        ttk.Label(main_frame, text="Expiry Alert Days:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.expiry_days_var = tk.StringVar(value=str(self.alert_manager.expiry_alert_days))
        ttk.Entry(main_frame, textvariable=self.expiry_days_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        ttk.Button(buttons_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_settings(self):
        """Save alert settings"""
        try:
            expiry_days = int(self.expiry_days_var.get())
            if expiry_days < 1:
                raise ValueError("Expiry alert days must be at least 1")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid expiry days: {e}")
            return
        
        # Update configuration
        self.alert_manager.sound_enabled = self.sound_var.get() and SOUND_AVAILABLE
        self.alert_manager.expiry_alert_days = expiry_days
        
        # Save to config file
        self.alert_manager.config['alert_sound_enabled'] = self.alert_manager.sound_enabled
        self.alert_manager.config['expiry_alert_days'] = expiry_days
        
        try:
            with open('config.json', 'w') as f:
                json.dump(self.alert_manager.config, f, indent=4)
            
            messagebox.showinfo("Success", "Settings saved successfully")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

# Auto-alert checker for background monitoring
class AutoAlertChecker:
    """Automatically check for alerts at regular intervals"""
    
    def __init__(self, parent, alert_manager, check_interval=300000):  # 5 minutes default
        self.parent = parent
        self.alert_manager = alert_manager
        self.check_interval = check_interval
        self.last_alert_count = 0
        self.start_checking()
    
    def start_checking(self):
        """Start automatic alert checking"""
        self.check_alerts()
        self.parent.after(self.check_interval, self.start_checking)
    
    def check_alerts(self):
        """Check for new alerts"""
        alerts = self.alert_manager.check_all_alerts()
        current_alert_count = alerts['total_alerts']
        
        # Show notification if new alerts appeared
        if current_alert_count > self.last_alert_count:
            new_alerts = current_alert_count - self.last_alert_count
            self.show_notification(f"{new_alerts} new alert(s) detected!")
            
            # Play sound for new alerts
            if self.alert_manager.sound_enabled:
                self.alert_manager.play_alert_sound()
        
        self.last_alert_count = current_alert_count
    
    def show_notification(self, message):
        """Show a brief notification"""
        # Create a temporary notification window
        notification = tk.Toplevel(self.parent)
        notification.title("Alert Notification")
        notification.geometry("300x100")
        notification.attributes('-topmost', True)
        
        # Position in bottom right
        x = notification.winfo_screenwidth() - 320
        y = notification.winfo_screenheight() - 150
        notification.geometry(f"300x100+{x}+{y}")
        
        # Content
        ttk.Label(notification, text="⚠️ Inventory Alert", 
                 font=('Arial', 12, 'bold')).pack(pady=5)
        ttk.Label(notification, text=message).pack(pady=5)
        
        ttk.Button(notification, text="View Alerts", 
                  command=lambda: [notification.destroy(), 
                                 self.alert_manager.show_alert_popup(self.parent)]).pack(side=tk.LEFT, padx=5)
        ttk.Button(notification, text="Dismiss", 
                  command=notification.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Auto-close after 10 seconds
        notification.after(10000, notification.destroy)

if __name__ == "__main__":
    # Test alerts window
    root = tk.Tk()
    root.title("Test Alerts")
    
    # Mock user
    current_user = {'id': 1, 'username': 'admin', 'role': 'Admin'}
    
    # Initialize database
    from db import initialize_database
    initialize_database()
    
    # Create alerts window
    alerts_window = AlertsWindow(root, current_user)
    
    root.mainloop()