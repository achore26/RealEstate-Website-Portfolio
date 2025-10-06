# Hotel Inventory Management System

A comprehensive desktop inventory management system designed for small-to-mid-sized hotel stores. Built with Python, Tkinter, and SQLite for offline-first operation.

## 🌟 Features

### 🔐 Authentication & User Management
- **Role-based access control** (Admin, Clerk)
- **Secure password hashing** with bcrypt
- **User management** (Admin only)
- **Default admin account**: `admin` / `admin123`

### 📦 Inventory Management
- **Complete item management** (Add, Edit, Delete)
- **Stock operations** (Add Stock, Use Stock)
- **Item fields**: Name, Category, Quantity, Unit, Reorder Level, Supplier, Expiry Date
- **Search and filtering** by name, category, supplier
- **Transaction audit log** for all stock movements

### 🚨 Smart Alerts System
- **Low stock alerts** when quantity ≤ reorder level
- **Expiry alerts** for items expiring within 5 days (configurable)
- **Visual indicators** in inventory table (red/yellow highlighting)
- **Popup notifications** with sound alerts (optional)
- **Auto-alert checker** runs in background

### 📊 Reports & Analytics
- **Interactive dashboard** with real-time statistics
- **Usage reports** (daily, weekly, monthly)
- **Top 5 most used items** analysis
- **Category and supplier analytics**
- **Visual charts** using Matplotlib
- **Export to CSV and PDF** formats

### 💾 Data Management
- **SQLite database** for reliable offline storage
- **Automatic backup** functionality
- **Database restore** from backup files
- **Data export** capabilities
- **Transaction history** tracking

### 🎨 User Interface
- **Modern Tkinter interface** with ttk widgets
- **Tabbed navigation** for different modules
- **Responsive design** with proper grid layouts
- **Status bar** with user info and current time
- **Context menus** and keyboard shortcuts

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
# Navigate to the project directory
cd hotel_inventory_system

# Install required packages
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
# Start the application
python main.py
```

### Step 3: First Login
- **Username**: `admin`
- **Password**: `admin123`
- Change the default password after first login!

## 📁 Project Structure

```
hotel_inventory_system/
├── main.py                 # Main application entry point
├── db.py                   # Database management and setup
├── login.py                # Authentication and user management
├── inventory.py            # Inventory management module
├── alerts.py               # Alerts and notifications system
├── reports.py              # Reports and analytics module
├── config.json             # Application configuration
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── backups/               # Database backups (auto-created)
├── reports/               # Exported reports (auto-created)
└── hotel_inventory.log    # Application log file
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('Admin', 'Clerk')),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Items Table
```sql
CREATE TABLE items (
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
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('IN', 'OUT')),
    quantity REAL NOT NULL,
    notes TEXT,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (item_id) REFERENCES items (id)
);
```

## 🎯 Usage Guide

### Adding Inventory Items
1. Go to **Inventory** tab
2. Click **Add Item** button
3. Fill in required fields:
   - Name (required)
   - Category (required)
   - Initial Quantity (required)
   - Unit (required)
   - Reorder Level (required)
   - Supplier (optional)
   - Expiry Date (optional, format: YYYY-MM-DD)
4. Click **Add Item**

### Stock Operations
1. Select an item in the inventory table
2. Click **Add Stock** (for deliveries/purchases)
3. Click **Use Stock** (for consumption/sales)
4. Enter quantity and optional notes
5. Confirm the operation

### Managing Alerts
1. Go to **Alerts** tab to view current alerts
2. Low stock items appear in red
3. Expiring items appear in yellow/orange
4. Configure alert settings via **Alert Settings** button

### Generating Reports
1. Go to **Reports** tab
2. **Dashboard**: View real-time statistics and charts
3. **Usage Reports**: Generate consumption reports for date ranges
4. **Analytics**: Analyze by category or supplier
5. **Export**: Save data to CSV or PDF files

### User Management (Admin Only)
1. Go to **Admin** → **Manage Users**
2. Add new users with appropriate roles
3. Change passwords or delete users
4. Cannot delete the last admin user

### Backup & Restore
1. **File** → **Backup Database** to create backup
2. **File** → **Restore Database** to restore from backup
3. Backups are saved in the `backups/` folder

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
    "backup_path": "./backups",
    "alert_sound_enabled": true,
    "report_export_path": "./reports",
    "expiry_alert_days": 5,
    "database_name": "hotel_inventory.db",
    "app_title": "Hotel Inventory Management System",
    "version": "1.0.0",
    "company_name": "Hotel Management Solutions"
}
```

## 📦 Creating Executable

To create a standalone executable using PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable (Windows)
pyinstaller --onefile --windowed --name "HotelInventory" main.py

# Create executable (Linux/Mac)
pyinstaller --onefile --name "HotelInventory" main.py
```

The executable will be created in the `dist/` folder.

## 🔧 Troubleshooting

### Common Issues

**Database Error on Startup**
- Ensure the application has write permissions in the directory
- Check if `hotel_inventory.db` file is corrupted
- Try restoring from a backup

**Import Errors**
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.7+)

**Charts Not Displaying**
- Ensure matplotlib is properly installed
- Try: `pip install --upgrade matplotlib`

**PDF Export Not Working**
- Install reportlab: `pip install reportlab`
- Check if the reports folder has write permissions

**Sound Alerts Not Working**
- Install playsound: `pip install playsound`
- Disable sound alerts in settings if issues persist

### Log Files
Check `hotel_inventory.log` for detailed error messages and debugging information.

## 🛡️ Security Features

- **Password hashing** using bcrypt
- **Role-based access control**
- **SQL injection prevention** using parameterized queries
- **Session management** with proper logout
- **Audit trail** for all inventory operations

## 🔄 Backup Strategy

- **Manual backups** via File menu
- **Automatic backup naming** with timestamps
- **Full database backup** including all tables
- **Easy restore** functionality
- **Backup verification** before restore

## 📈 Performance Optimization

- **Efficient database queries** with proper indexing
- **Lazy loading** for large datasets
- **Background alert checking** without blocking UI
- **Optimized chart rendering** with matplotlib
- **Memory management** for large reports

## 🤝 Contributing

This is a complete, production-ready system. For customizations:

1. **Fork the repository**
2. **Create feature branches**
3. **Test thoroughly**
4. **Document changes**
5. **Submit pull requests**

## 📄 License

This project is developed for educational and commercial use. Modify as needed for your specific requirements.

## 📞 Support

For technical support or questions:
- Check the **Help** → **User Guide** in the application
- Review log files for error details
- Consult the troubleshooting section above

---

**🏨 Built for Hotel Management Excellence 🏨**

*A complete inventory solution designed to streamline hotel operations and improve efficiency.*