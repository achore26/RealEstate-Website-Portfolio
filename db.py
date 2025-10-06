"""
Database module for Hotel Inventory Management System
Handles SQLite database connection, table creation, and basic operations
"""

import sqlite3
import os
import json
import bcrypt
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, config_file='config.json'):
        """Initialize database manager with configuration"""
        self.config = self.load_config(config_file)
        self.db_name = self.config.get('database_name', 'hotel_inventory.db')
        self.connection = None
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using defaults.")
            return {
                "database_name": "hotel_inventory.db",
                "backup_path": "./backups",
                "alert_sound_enabled": True,
                "report_export_path": "./reports",
                "expiry_alert_days": 5
            }
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Connected to database: {self.db_name}")
            return self.connection
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def create_tables(self):
        """Create all required tables if they don't exist"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('Admin', 'Clerk', 'Stock User')),
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Items table
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
        
        # Transactions table (audit log)
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
        
        self.connection.commit()
        logger.info("Database tables created successfully")
        
        # Create default admin user if no users exist
        self.create_default_admin()
    
    def create_default_admin(self):
        """Create default admin user if no users exist"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # Hash the default password
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', ("admin", password_hash, "Admin"))
            
            self.connection.commit()
            logger.info("Default admin user created (username: admin, password: admin123)")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.connection.commit()
                return cursor.rowcount
            else:
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Query execution error: {e}")
            self.connection.rollback()
            raise
    
    def get_user_by_username(self, username):
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = ?"
        result = self.execute_query(query, (username,))
        return result[0] if result else None
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        query = "UPDATE users SET last_login = ? WHERE id = ?"
        self.execute_query(query, (datetime.now(), user_id))
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        if not backup_path:
            backup_path = self.config.get('backup_path', './backups')
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_path, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"hotel_inventory_backup_{timestamp}.db"
        backup_full_path = os.path.join(backup_path, backup_filename)
        
        try:
            # Copy database file
            import shutil
            shutil.copy2(self.db_name, backup_full_path)
            logger.info(f"Database backed up to: {backup_full_path}")
            return backup_full_path
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    def restore_database(self, backup_file_path):
        """Restore database from backup"""
        try:
            if self.connection:
                self.disconnect()
            
            import shutil
            shutil.copy2(backup_file_path, self.db_name)
            logger.info(f"Database restored from: {backup_file_path}")
            
            # Reconnect to the restored database
            self.connect()
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise

# Global database instance
db_manager = DatabaseManager()

def initialize_database():
    """Initialize database with tables and default data"""
    db_manager.connect()
    db_manager.create_tables()
    return db_manager

if __name__ == "__main__":
    # Test database initialization
    print("Initializing database...")
    db = initialize_database()
    print("Database initialized successfully!")
    db.disconnect()