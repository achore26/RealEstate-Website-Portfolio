"""
Login and Authentication module for Hotel Inventory Management System
Handles user authentication, login screen, and session management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
from db import db_manager
import logging

logger = logging.getLogger(__name__)

class LoginWindow:
    def __init__(self, on_login_success=None):
        """Initialize login window"""
        self.on_login_success = on_login_success
        self.current_user = None
        
        # Create login window
        self.root = tk.Tk()
        self.root.title("Hotel Inventory - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Create login interface
        self.create_login_interface()
        
        # Initialize database connection
        db_manager.connect()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"400x300+{x}+{y}")
    
    def create_login_interface(self):
        """Create the login form interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏨 Madit Hotel Inventory", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Please login to continue", 
                                  font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Username field
        ttk.Label(main_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=25)
        self.username_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Password field
        ttk.Label(main_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                       show="*", width=25)
        self.password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Login button
        self.login_button = ttk.Button(main_frame, text="Login", command=self.login)
        self.login_button.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Default credentials info
        info_frame = ttk.LabelFrame(main_frame, text="Default Credentials", padding="10")
        info_frame.grid(row=6, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        
        ttk.Label(info_frame, text="Username: admin").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text="Password: admin123").grid(row=1, column=0, sticky=tk.W)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())
        
        # Focus on username entry
        self.username_entry.focus()
    
    def login(self):
        """Handle login attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        # Validate input
        if not username or not password:
            self.show_status("Please enter both username and password", "red")
            return
        
        try:
            # Get user from database
            user = db_manager.get_user_by_username(username)
            
            if user and db_manager.verify_password(password, user['password_hash']):
                # Successful login
                self.current_user = {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
                
                # Update last login
                db_manager.update_last_login(user['id'])
                
                self.show_status("Login successful!", "green")
                logger.info(f"User {username} logged in successfully")
                
                # Close login window and call success callback
                self.root.after(1000, self.on_successful_login)
                
            else:
                self.show_status("Invalid username or password", "red")
                logger.warning(f"Failed login attempt for username: {username}")
                
        except Exception as e:
            self.show_status("Login error occurred", "red")
            logger.error(f"Login error: {e}")
    
    def show_status(self, message, color="black"):
        """Show status message"""
        self.status_label.config(text=message, foreground=color)
    
    def on_successful_login(self):
        """Handle successful login"""
        if self.on_login_success:
            self.on_login_success(self.current_user)
        self.root.destroy()
    
    def run(self):
        """Start the login window"""
        self.root.mainloop()
        return self.current_user

class UserManager:
    """Manage user operations (for admin users)"""
    
    @staticmethod
    def create_user(username, password, role):
        """Create a new user"""
        try:
            # Check if username already exists
            existing_user = db_manager.get_user_by_username(username)
            if existing_user:
                raise ValueError("Username already exists")
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Insert user
            query = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
            db_manager.execute_query(query, (username, password_hash, role))
            
            logger.info(f"User {username} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        query = "SELECT id, username, role, created_date, last_login FROM users ORDER BY username"
        return db_manager.execute_query(query)
    
    @staticmethod
    def update_user_password(user_id, new_password):
        """Update user password"""
        try:
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            query = "UPDATE users SET password_hash = ? WHERE id = ?"
            db_manager.execute_query(query, (password_hash, user_id))
            logger.info(f"Password updated for user ID: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            raise
    
    @staticmethod
    def delete_user(user_id):
        """Delete a user (cannot delete admin if it's the only admin)"""
        try:
            # Check if this is the last admin
            admin_count_query = "SELECT COUNT(*) FROM users WHERE role = 'Admin'"
            admin_count = db_manager.execute_query(admin_count_query)[0][0]
            
            user_query = "SELECT role FROM users WHERE id = ?"
            user_role = db_manager.execute_query(user_query, (user_id,))[0]['role']
            
            if user_role == 'Admin' and admin_count <= 1:
                raise ValueError("Cannot delete the last admin user")
            
            # Delete user
            query = "DELETE FROM users WHERE id = ?"
            db_manager.execute_query(query, (user_id,))
            logger.info(f"User ID {user_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise

class UserManagementDialog:
    """Dialog for managing users (Admin only)"""
    
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        
        # Check if user is admin
        if current_user['role'] != 'Admin':
            messagebox.showerror("Access Denied", "Only administrators can manage users")
            return
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create user management dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("User Management")
        self.dialog.geometry("600x400")
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
        ttk.Label(main_frame, text="User Management", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=(0, 10))
        
        # Users list
        self.create_users_list(main_frame)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(buttons_frame, text="Add User", 
                  command=self.add_user_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Change Password", 
                  command=self.change_password_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete User", 
                  command=self.delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", 
                  command=self.refresh_users).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Close", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def create_users_list(self, parent):
        """Create users list with treeview"""
        # Treeview frame
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('ID', 'Username', 'Role', 'Created', 'Last Login')
        self.users_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Configure columns
        self.users_tree.heading('ID', text='ID')
        self.users_tree.heading('Username', text='Username')
        self.users_tree.heading('Role', text='Role')
        self.users_tree.heading('Created', text='Created')
        self.users_tree.heading('Last Login', text='Last Login')
        
        self.users_tree.column('ID', width=50)
        self.users_tree.column('Username', width=120)
        self.users_tree.column('Role', width=80)
        self.users_tree.column('Created', width=120)
        self.users_tree.column('Last Login', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.users_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Load users
        self.refresh_users()
    
    def refresh_users(self):
        """Refresh users list"""
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Load users
        users = UserManager.get_all_users()
        for user in users:
            self.users_tree.insert('', tk.END, values=(
                user['id'],
                user['username'],
                user['role'],
                user['created_date'][:10] if user['created_date'] else '',
                user['last_login'][:10] if user['last_login'] else 'Never'
            ))
    
    def add_user_dialog(self):
        """Show add user dialog"""
        AddUserDialog(self.dialog, self.refresh_users)
    
    def change_password_dialog(self):
        """Show change password dialog"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user")
            return
        
        user_id = self.users_tree.item(selection[0])['values'][0]
        username = self.users_tree.item(selection[0])['values'][1]
        
        ChangePasswordDialog(self.dialog, user_id, username, self.refresh_users)
    
    def delete_user(self):
        """Delete selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user")
            return
        
        user_id = self.users_tree.item(selection[0])['values'][0]
        username = self.users_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Delete user '{username}'?"):
            try:
                UserManager.delete_user(user_id)
                messagebox.showinfo("Success", "User deleted successfully")
                self.refresh_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {e}")

class AddUserDialog:
    """Dialog for adding new user"""
    
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.create_dialog()
    
    def create_dialog(self):
        """Create add user dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add New User")
        self.dialog.geometry("300x200")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.username_var).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(main_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Role
        ttk.Label(main_frame, text="Role:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.role_var = tk.StringVar(value="Clerk")
        role_combo = ttk.Combobox(main_frame, textvariable=self.role_var, 
                                 values=["Admin", "Clerk", "Stock User"], state="readonly")
        role_combo.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Create", command=self.create_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def create_user(self):
        """Create new user"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            UserManager.create_user(username, password, role)
            messagebox.showinfo("Success", "User created successfully")
            self.callback()
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create user: {e}")

class ChangePasswordDialog:
    """Dialog for changing user password"""
    
    def __init__(self, parent, user_id, username, callback):
        self.parent = parent
        self.user_id = user_id
        self.username = username
        self.callback = callback
        self.create_dialog()
    
    def create_dialog(self):
        """Create change password dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Change Password - {self.username}")
        self.dialog.geometry("300x150")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # New password
        ttk.Label(main_frame, text="New Password:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.password_var, show="*").grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Confirm password
        ttk.Label(main_frame, text="Confirm:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.confirm_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.confirm_var, show="*").grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Change", command=self.change_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def change_password(self):
        """Change user password"""
        password = self.password_var.get()
        confirm = self.confirm_var.get()
        
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        try:
            UserManager.update_user_password(self.user_id, password)
            messagebox.showinfo("Success", "Password changed successfully")
            self.callback()
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change password: {e}")

if __name__ == "__main__":
    # Test login window
    def on_login(user):
        print(f"Logged in as: {user}")
    
    login_window = LoginWindow(on_login)
    user = login_window.run()
    print(f"Login result: {user}")