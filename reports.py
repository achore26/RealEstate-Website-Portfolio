"""
Reports and Analytics module for Hotel Inventory Management System
Handles report generation, data visualization, and export functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from db import db_manager
import os
import json
import logging

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: reportlab not available. PDF export disabled.")

logger = logging.getLogger(__name__)

class ReportsManager:
    """Main reports and analytics manager"""
    
    def __init__(self, config_file='config.json'):
        """Initialize reports manager"""
        self.config = self.load_config(config_file)
        self.export_path = self.config.get('report_export_path', './reports')
        
        # Ensure export directory exists
        os.makedirs(self.export_path, exist_ok=True)
    
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"report_export_path": "./reports"}
    
    def get_inventory_summary(self):
        """Get overall inventory summary"""
        query = '''
            SELECT 
                COUNT(*) as total_items,
                SUM(CASE WHEN quantity <= reorder_level THEN 1 ELSE 0 END) as low_stock_items,
                COUNT(DISTINCT category) as total_categories,
                COUNT(DISTINCT supplier) as total_suppliers
            FROM items
        '''
        result = db_manager.execute_query(query)
        return result[0] if result else {}
    
    def get_usage_report(self, start_date, end_date):
        """Get usage report for date range"""
        query = '''
            SELECT 
                i.name,
                i.category,
                i.unit,
                SUM(CASE WHEN t.type = 'OUT' THEN t.quantity ELSE 0 END) as total_used,
                COUNT(CASE WHEN t.type = 'OUT' THEN 1 END) as usage_count,
                AVG(CASE WHEN t.type = 'OUT' THEN t.quantity END) as avg_usage
            FROM items i
            LEFT JOIN transactions t ON i.id = t.item_id
            WHERE t.date_time BETWEEN ? AND ?
            GROUP BY i.id, i.name, i.category, i.unit
            HAVING total_used > 0
            ORDER BY total_used DESC
        '''
        return db_manager.execute_query(query, (start_date, end_date))
    
    def get_top_used_items(self, days=7, limit=5):
        """Get top used items in the last N days"""
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        query = '''
            SELECT 
                i.name,
                i.category,
                SUM(t.quantity) as total_used
            FROM items i
            JOIN transactions t ON i.id = t.item_id
            WHERE t.type = 'OUT' AND t.date_time BETWEEN ? AND ?
            GROUP BY i.id, i.name, i.category
            ORDER BY total_used DESC
            LIMIT ?
        '''
        return db_manager.execute_query(query, (start_date, end_date, limit))
    
    def get_stock_movements(self, start_date, end_date):
        """Get all stock movements for date range"""
        query = '''
            SELECT 
                t.date_time,
                i.name,
                i.category,
                t.type,
                t.quantity,
                u.username,
                t.notes
            FROM transactions t
            JOIN items i ON t.item_id = i.id
            JOIN users u ON t.user_id = u.id
            WHERE t.date_time BETWEEN ? AND ?
            ORDER BY t.date_time DESC
        '''
        return db_manager.execute_query(query, (start_date, end_date))
    
    def get_category_analysis(self):
        """Get analysis by category"""
        query = '''
            SELECT 
                category,
                COUNT(*) as item_count,
                SUM(quantity) as total_stock,
                AVG(quantity) as avg_stock,
                SUM(CASE WHEN quantity <= reorder_level THEN 1 ELSE 0 END) as low_stock_count
            FROM items
            GROUP BY category
            ORDER BY item_count DESC
        '''
        return db_manager.execute_query(query)
    
    def get_supplier_analysis(self):
        """Get analysis by supplier"""
        query = '''
            SELECT 
                COALESCE(supplier, 'Unknown') as supplier,
                COUNT(*) as item_count,
                SUM(quantity) as total_stock,
                SUM(CASE WHEN quantity <= reorder_level THEN 1 ELSE 0 END) as low_stock_count
            FROM items
            GROUP BY supplier
            ORDER BY item_count DESC
        '''
        return db_manager.execute_query(query)
    
    def export_to_csv(self, data, filename, headers):
        """Export data to CSV file"""
        try:
            filepath = os.path.join(self.export_path, f"{filename}.csv")
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            # Export to CSV
            df.to_csv(filepath, index=False)
            
            logger.info(f"Report exported to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise
    
    def export_to_pdf(self, data, filename, title, headers):
        """Export data to PDF file"""
        if not PDF_AVAILABLE:
            raise ImportError("PDF export not available. Install reportlab package.")
        
        try:
            filepath = os.path.join(self.export_path, f"{filename}.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            # Title
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 12))
            
            # Generation info
            generation_info = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            elements.append(Paragraph(generation_info, styles['Normal']))
            elements.append(Spacer(1, 12))
            
            # Data table
            if data:
                # Prepare table data
                table_data = [headers] + [list(row) for row in data]
                
                # Create table
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
            else:
                elements.append(Paragraph("No data available for the selected criteria.", styles['Normal']))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"Report exported to PDF: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            raise

class ReportsWindow:
    """Main reports and analytics window"""
    
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        self.reports_manager = ReportsManager()
        self.create_reports_interface()
    
    def create_reports_interface(self):
        """Create the reports interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Reports & Analytics", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Create notebook for different report types
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Dashboard tab
        self.create_dashboard_tab()
        
        # Usage reports tab
        self.create_usage_reports_tab()
        
        # Analytics tab
        self.create_analytics_tab()
        
        # Export tab
        self.create_export_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard tab with summary information"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Configure grid
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.rowconfigure(1, weight=1)
        
        # Summary cards
        self.create_summary_cards(dashboard_frame)
        
        # Charts frame
        charts_frame = ttk.Frame(dashboard_frame)
        charts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)
        charts_frame.rowconfigure(0, weight=1)
        
        # Top used items chart
        self.create_top_items_chart(charts_frame)
        
        # Category distribution chart
        self.create_category_chart(charts_frame)
        
        # Refresh button
        ttk.Button(dashboard_frame, text="Refresh Dashboard", 
                  command=self.refresh_dashboard).grid(row=2, column=0, pady=10)
    
    def create_summary_cards(self, parent):
        """Create summary information cards"""
        cards_frame = ttk.LabelFrame(parent, text="Inventory Summary", padding="10")
        cards_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        # Configure grid
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
        
        # Get summary data
        summary = self.reports_manager.get_inventory_summary()
        
        # Total items card
        total_frame = ttk.Frame(cards_frame, relief='raised', borderwidth=2)
        total_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        total_frame.columnconfigure(0, weight=1)
        
        ttk.Label(total_frame, text="Total Items", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
        self.total_items_label = ttk.Label(total_frame, text=str(summary[0] if summary else 0), 
                                          font=('Arial', 20, 'bold'), foreground='blue')
        self.total_items_label.grid(row=1, column=0, pady=5)
        
        # Low stock card
        low_stock_frame = ttk.Frame(cards_frame, relief='raised', borderwidth=2)
        low_stock_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        low_stock_frame.columnconfigure(0, weight=1)
        
        ttk.Label(low_stock_frame, text="Low Stock", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
        self.low_stock_label = ttk.Label(low_stock_frame, text=str(summary[1] if summary else 0), 
                                        font=('Arial', 20, 'bold'), foreground='red')
        self.low_stock_label.grid(row=1, column=0, pady=5)
        
        # Categories card
        categories_frame = ttk.Frame(cards_frame, relief='raised', borderwidth=2)
        categories_frame.grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        categories_frame.columnconfigure(0, weight=1)
        
        ttk.Label(categories_frame, text="Categories", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
        self.categories_label = ttk.Label(categories_frame, text=str(summary[2] if summary else 0), 
                                         font=('Arial', 20, 'bold'), foreground='green')
        self.categories_label.grid(row=1, column=0, pady=5)
        
        # Suppliers card
        suppliers_frame = ttk.Frame(cards_frame, relief='raised', borderwidth=2)
        suppliers_frame.grid(row=0, column=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        suppliers_frame.columnconfigure(0, weight=1)
        
        ttk.Label(suppliers_frame, text="Suppliers", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
        self.suppliers_label = ttk.Label(suppliers_frame, text=str(summary[3] if summary else 0), 
                                        font=('Arial', 20, 'bold'), foreground='purple')
        self.suppliers_label.grid(row=1, column=0, pady=5)
    
    def create_top_items_chart(self, parent):
        """Create top used items chart"""
        chart_frame = ttk.LabelFrame(parent, text="Top 5 Most Used Items (Last 7 Days)", padding="5")
        chart_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.top_items_fig, self.top_items_ax = plt.subplots(figsize=(6, 4))
        self.top_items_canvas = FigureCanvasTkAgg(self.top_items_fig, chart_frame)
        self.top_items_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.update_top_items_chart()
    
    def create_category_chart(self, parent):
        """Create category distribution chart"""
        chart_frame = ttk.LabelFrame(parent, text="Items by Category", padding="5")
        chart_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.category_fig, self.category_ax = plt.subplots(figsize=(6, 4))
        self.category_canvas = FigureCanvasTkAgg(self.category_fig, chart_frame)
        self.category_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.update_category_chart()
    
    def update_top_items_chart(self):
        """Update top items chart"""
        self.top_items_ax.clear()
        
        try:
            data = self.reports_manager.get_top_used_items()
            
            if data:
                items = [row['name'][:15] + '...' if len(row['name']) > 15 else row['name'] for row in data]
                quantities = [row['total_used'] for row in data]
                
                bars = self.top_items_ax.bar(items, quantities, color='skyblue')
                self.top_items_ax.set_ylabel('Quantity Used')
                self.top_items_ax.set_title('Top 5 Most Used Items')
                
                # Rotate x-axis labels for better readability
                plt.setp(self.top_items_ax.get_xticklabels(), rotation=45, ha='right')
                
                # Add value labels on bars
                for bar, qty in zip(bars, quantities):
                    height = bar.get_height()
                    self.top_items_ax.text(bar.get_x() + bar.get_width()/2., height,
                                          f'{qty:.1f}', ha='center', va='bottom')
            else:
                self.top_items_ax.text(0.5, 0.5, 'No usage data available', 
                                      ha='center', va='center', transform=self.top_items_ax.transAxes)
            
            self.top_items_fig.tight_layout()
            self.top_items_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating top items chart: {e}")
    
    def update_category_chart(self):
        """Update category distribution chart"""
        self.category_ax.clear()
        
        try:
            data = self.reports_manager.get_category_analysis()
            
            if data:
                categories = [row['category'] for row in data]
                counts = [row['item_count'] for row in data]
                
                # Create pie chart
                wedges, texts, autotexts = self.category_ax.pie(counts, labels=categories, autopct='%1.1f%%', 
                                                               startangle=90)
                self.category_ax.set_title('Items Distribution by Category')
                
                # Make percentage text more readable
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            else:
                self.category_ax.text(0.5, 0.5, 'No category data available', 
                                     ha='center', va='center', transform=self.category_ax.transAxes)
            
            self.category_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating category chart: {e}")
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Update summary cards
        summary = self.reports_manager.get_inventory_summary()
        self.total_items_label.config(text=str(summary[0] if summary else 0))
        self.low_stock_label.config(text=str(summary[1] if summary else 0))
        self.categories_label.config(text=str(summary[2] if summary else 0))
        self.suppliers_label.config(text=str(summary[3] if summary else 0))
        
        # Update charts
        self.update_top_items_chart()
        self.update_category_chart()
    
    def create_usage_reports_tab(self):
        """Create usage reports tab"""
        usage_frame = ttk.Frame(self.notebook)
        self.notebook.add(usage_frame, text="Usage Reports")
        
        # Configure grid
        usage_frame.columnconfigure(0, weight=1)
        usage_frame.rowconfigure(2, weight=1)
        
        # Date selection frame
        date_frame = ttk.LabelFrame(usage_frame, text="Report Period", padding="10")
        date_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        # Start date
        ttk.Label(date_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        ttk.Entry(date_frame, textvariable=self.start_date_var, width=12).grid(row=0, column=1, padx=5)
        
        # End date
        ttk.Label(date_frame, text="To:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.end_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(date_frame, textvariable=self.end_date_var, width=12).grid(row=0, column=3, padx=5)
        
        # Generate button
        ttk.Button(date_frame, text="Generate Report", 
                  command=self.generate_usage_report).grid(row=0, column=4, padx=10)
        
        # Quick date buttons
        quick_frame = ttk.Frame(date_frame)
        quick_frame.grid(row=1, column=0, columnspan=5, pady=10)
        
        ttk.Button(quick_frame, text="Last 7 Days", 
                  command=lambda: self.set_quick_dates(7)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Last 30 Days", 
                  command=lambda: self.set_quick_dates(30)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Last 90 Days", 
                  command=lambda: self.set_quick_dates(90)).pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(usage_frame, text="Usage Report Results", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results table
        self.create_usage_results_table(results_frame)
    
    def create_usage_results_table(self, parent):
        """Create usage results table"""
        # Table frame
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('Item Name', 'Category', 'Unit', 'Total Used', 'Usage Count', 'Avg Usage')
        self.usage_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure columns
        column_widths = {'Item Name': 150, 'Category': 100, 'Unit': 60, 
                        'Total Used': 100, 'Usage Count': 100, 'Avg Usage': 100}
        
        for col in columns:
            self.usage_tree.heading(col, text=col)
            self.usage_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.usage_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.usage_tree.xview)
        self.usage_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid
        self.usage_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Export buttons
        export_frame = ttk.Frame(parent)
        export_frame.grid(row=1, column=0, pady=10)
        
        ttk.Button(export_frame, text="Export to CSV", 
                  command=self.export_usage_csv).pack(side=tk.LEFT, padx=5)
        if PDF_AVAILABLE:
            ttk.Button(export_frame, text="Export to PDF", 
                      command=self.export_usage_pdf).pack(side=tk.LEFT, padx=5)
    
    def set_quick_dates(self, days):
        """Set quick date ranges"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
    
    def generate_usage_report(self):
        """Generate usage report for selected date range"""
        try:
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            # Validate dates
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            
            # Clear existing data
            for item in self.usage_tree.get_children():
                self.usage_tree.delete(item)
            
            # Get usage data
            usage_data = self.reports_manager.get_usage_report(start_date, end_date)
            
            # Populate table
            for row in usage_data:
                self.usage_tree.insert('', tk.END, values=(
                    row['name'],
                    row['category'],
                    row['unit'],
                    f"{row['total_used']:.2f}",
                    row['usage_count'],
                    f"{row['avg_usage']:.2f}" if row['avg_usage'] else "0.00"
                ))
            
            # Store current data for export
            self.current_usage_data = usage_data
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def export_usage_csv(self):
        """Export usage report to CSV"""
        if not hasattr(self, 'current_usage_data') or not self.current_usage_data:
            messagebox.showwarning("No Data", "Please generate a report first")
            return
        
        try:
            filename = f"usage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            headers = ['Item Name', 'Category', 'Unit', 'Total Used', 'Usage Count', 'Average Usage']
            
            # Prepare data for export
            export_data = []
            for row in self.current_usage_data:
                export_data.append([
                    row['name'],
                    row['category'],
                    row['unit'],
                    row['total_used'],
                    row['usage_count'],
                    row['avg_usage'] or 0
                ])
            
            filepath = self.reports_manager.export_to_csv(export_data, filename, headers)
            messagebox.showinfo("Success", f"Report exported to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_usage_pdf(self):
        """Export usage report to PDF"""
        if not hasattr(self, 'current_usage_data') or not self.current_usage_data:
            messagebox.showwarning("No Data", "Please generate a report first")
            return
        
        try:
            filename = f"usage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            title = f"Usage Report ({self.start_date_var.get()} to {self.end_date_var.get()})"
            headers = ['Item Name', 'Category', 'Unit', 'Total Used', 'Usage Count', 'Avg Usage']
            
            # Prepare data for export
            export_data = []
            for row in self.current_usage_data:
                export_data.append([
                    row['name'],
                    row['category'],
                    row['unit'],
                    f"{row['total_used']:.2f}",
                    str(row['usage_count']),
                    f"{row['avg_usage']:.2f}" if row['avg_usage'] else "0.00"
                ])
            
            filepath = self.reports_manager.export_to_pdf(export_data, filename, title, headers)
            messagebox.showinfo("Success", f"Report exported to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def create_analytics_tab(self):
        """Create analytics tab"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="Analytics")
        
        # Configure grid
        analytics_frame.columnconfigure(0, weight=1)
        analytics_frame.rowconfigure(0, weight=1)
        
        # Create sub-notebook for different analytics
        analytics_notebook = ttk.Notebook(analytics_frame)
        analytics_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Category analysis
        self.create_category_analysis_tab(analytics_notebook)
        
        # Supplier analysis
        self.create_supplier_analysis_tab(analytics_notebook)
    
    def create_category_analysis_tab(self, parent):
        """Create category analysis tab"""
        category_frame = ttk.Frame(parent)
        parent.add(category_frame, text="By Category")
        
        # Configure grid
        category_frame.columnconfigure(0, weight=1)
        category_frame.rowconfigure(1, weight=1)
        
        # Refresh button
        ttk.Button(category_frame, text="Refresh Analysis", 
                  command=self.refresh_category_analysis).grid(row=0, column=0, pady=10)
        
        # Results table
        table_frame = ttk.Frame(category_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('Category', 'Item Count', 'Total Stock', 'Avg Stock', 'Low Stock Items')
        self.category_analysis_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            self.category_analysis_tree.heading(col, text=col)
            self.category_analysis_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.category_analysis_tree.yview)
        self.category_analysis_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.category_analysis_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Load initial data
        self.refresh_category_analysis()
    
    def create_supplier_analysis_tab(self, parent):
        """Create supplier analysis tab"""
        supplier_frame = ttk.Frame(parent)
        parent.add(supplier_frame, text="By Supplier")
        
        # Configure grid
        supplier_frame.columnconfigure(0, weight=1)
        supplier_frame.rowconfigure(1, weight=1)
        
        # Refresh button
        ttk.Button(supplier_frame, text="Refresh Analysis", 
                  command=self.refresh_supplier_analysis).grid(row=0, column=0, pady=10)
        
        # Results table
        table_frame = ttk.Frame(supplier_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('Supplier', 'Item Count', 'Total Stock', 'Low Stock Items')
        self.supplier_analysis_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            self.supplier_analysis_tree.heading(col, text=col)
            self.supplier_analysis_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.supplier_analysis_tree.yview)
        self.supplier_analysis_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.supplier_analysis_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Load initial data
        self.refresh_supplier_analysis()
    
    def refresh_category_analysis(self):
        """Refresh category analysis"""
        # Clear existing data
        for item in self.category_analysis_tree.get_children():
            self.category_analysis_tree.delete(item)
        
        # Get category data
        category_data = self.reports_manager.get_category_analysis()
        
        # Populate table
        for row in category_data:
            self.category_analysis_tree.insert('', tk.END, values=(
                row['category'],
                row['item_count'],
                f"{row['total_stock']:.2f}",
                f"{row['avg_stock']:.2f}",
                row['low_stock_count']
            ))
    
    def refresh_supplier_analysis(self):
        """Refresh supplier analysis"""
        # Clear existing data
        for item in self.supplier_analysis_tree.get_children():
            self.supplier_analysis_tree.delete(item)
        
        # Get supplier data
        supplier_data = self.reports_manager.get_supplier_analysis()
        
        # Populate table
        for row in supplier_data:
            self.supplier_analysis_tree.insert('', tk.END, values=(
                row['supplier'],
                row['item_count'],
                f"{row['total_stock']:.2f}",
                row['low_stock_count']
            ))
    
    def create_export_tab(self):
        """Create export options tab"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="Export")
        
        # Configure grid
        export_frame.columnconfigure(0, weight=1)
        
        # Title
        ttk.Label(export_frame, text="Export Options", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=20)
        
        # Export options
        options_frame = ttk.LabelFrame(export_frame, text="Available Exports", padding="20")
        options_frame.grid(row=1, column=0, padx=20, pady=20, sticky=(tk.W, tk.E))
        
        # Full inventory export
        ttk.Button(options_frame, text="Export Full Inventory (CSV)", 
                  command=self.export_full_inventory_csv).grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))
        
        if PDF_AVAILABLE:
            ttk.Button(options_frame, text="Export Full Inventory (PDF)", 
                      command=self.export_full_inventory_pdf).grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Transaction history export
        ttk.Button(options_frame, text="Export Transaction History (CSV)", 
                  command=self.export_transactions_csv).grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Export path info
        info_frame = ttk.LabelFrame(export_frame, text="Export Information", padding="20")
        info_frame.grid(row=2, column=0, padx=20, pady=20, sticky=(tk.W, tk.E))
        
        ttk.Label(info_frame, text=f"Export Path: {self.reports_manager.export_path}").grid(row=0, column=0, sticky=tk.W)
        ttk.Button(info_frame, text="Open Export Folder", 
                  command=self.open_export_folder).grid(row=1, column=0, pady=10)
    
    def export_full_inventory_csv(self):
        """Export full inventory to CSV"""
        try:
            # Get all items
            items = self.reports_manager.db_manager.execute_query("SELECT * FROM items ORDER BY name")
            
            if not items:
                messagebox.showwarning("No Data", "No inventory items to export")
                return
            
            filename = f"full_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            headers = ['ID', 'Name', 'Category', 'Quantity', 'Unit', 'Reorder Level', 
                      'Supplier', 'Expiry Date', 'Created Date', 'Updated Date']
            
            # Prepare data
            export_data = []
            for item in items:
                export_data.append([
                    item['id'],
                    item['name'],
                    item['category'],
                    item['quantity'],
                    item['unit'],
                    item['reorder_level'],
                    item['supplier'] or '',
                    item['expiry_date'] or '',
                    item['created_date'] or '',
                    item['updated_date'] or ''
                ])
            
            filepath = self.reports_manager.export_to_csv(export_data, filename, headers)
            messagebox.showinfo("Success", f"Inventory exported to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_full_inventory_pdf(self):
        """Export full inventory to PDF"""
        try:
            # Get all items
            items = self.reports_manager.db_manager.execute_query("SELECT * FROM items ORDER BY name")
            
            if not items:
                messagebox.showwarning("No Data", "No inventory items to export")
                return
            
            filename = f"full_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            title = "Complete Inventory Report"
            headers = ['Name', 'Category', 'Quantity', 'Unit', 'Reorder Level', 'Supplier']
            
            # Prepare data (simplified for PDF)
            export_data = []
            for item in items:
                export_data.append([
                    item['name'],
                    item['category'],
                    f"{item['quantity']:.2f}",
                    item['unit'],
                    f"{item['reorder_level']:.2f}",
                    item['supplier'] or 'N/A'
                ])
            
            filepath = self.reports_manager.export_to_pdf(export_data, filename, title, headers)
            messagebox.showinfo("Success", f"Inventory exported to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_transactions_csv(self):
        """Export transaction history to CSV"""
        try:
            # Get date range from user
            date_dialog = DateRangeDialog(self.parent)
            if not date_dialog.result:
                return
            
            start_date, end_date = date_dialog.result
            
            # Get transactions
            transactions = self.reports_manager.get_stock_movements(start_date, end_date)
            
            if not transactions:
                messagebox.showwarning("No Data", "No transactions found for the selected period")
                return
            
            filename = f"transactions_{start_date}_{end_date}"
            headers = ['Date/Time', 'Item Name', 'Category', 'Type', 'Quantity', 'User', 'Notes']
            
            # Prepare data
            export_data = []
            for trans in transactions:
                export_data.append([
                    trans['date_time'],
                    trans['name'],
                    trans['category'],
                    trans['type'],
                    trans['quantity'],
                    trans['username'],
                    trans['notes'] or ''
                ])
            
            filepath = self.reports_manager.export_to_csv(export_data, filename, headers)
            messagebox.showinfo("Success", f"Transactions exported to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def open_export_folder(self):
        """Open export folder in file manager"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.Popen(f'explorer "{self.reports_manager.export_path}"')
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.reports_manager.export_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", self.reports_manager.export_path])
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")

class DateRangeDialog:
    """Dialog for selecting date range"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.create_dialog()
    
    def create_dialog(self):
        """Create date range dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Date Range")
        self.dialog.geometry("300x150")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Start date
        ttk.Label(main_frame, text="From:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        ttk.Entry(main_frame, textvariable=self.start_date_var, width=15).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # End date
        ttk.Label(main_frame, text="To:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(main_frame, textvariable=self.end_date_var, width=15).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def ok_clicked(self):
        """Handle OK button click"""
        try:
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            # Validate dates
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            
            self.result = (start_date, end_date)
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")

if __name__ == "__main__":
    # Test reports window
    root = tk.Tk()
    root.title("Test Reports")
    
    # Mock user
    current_user = {'id': 1, 'username': 'admin', 'role': 'Admin'}
    
    # Initialize database
    from db import initialize_database
    initialize_database()
    
    # Create reports window
    reports_window = ReportsWindow(root, current_user)
    
    root.mainloop()