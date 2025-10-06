"""
UI Theme and Styling module for Madit Hotel Inventory System
Provides enhanced styling and theming for the application
"""

import tkinter as tk
from tkinter import ttk
import json

class MaditTheme:
    """Enhanced theme for Madit Hotel Inventory System"""
    
    def __init__(self, config_file='config.json'):
        """Initialize theme with configuration"""
        self.config = self.load_config(config_file)
        self.colors = self.config.get('theme', {
            "primary_color": "#2E86AB",
            "secondary_color": "#A23B72", 
            "accent_color": "#F18F01",
            "success_color": "#C73E1D",
            "background_color": "#F5F5F5",
            "text_color": "#2C3E50"
        })
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def apply_theme(self, root):
        """Apply the Madit Hotel theme to the application"""
        # Configure ttk styles
        style = ttk.Style()
        
        # Set theme
        style.theme_use('clam')  # Use clam as base theme
        
        # Configure colors
        style.configure('Title.TLabel', 
                       font=('Arial', 18, 'bold'),
                       foreground=self.colors['primary_color'],
                       background=self.colors['background_color'])
        
        style.configure('Heading.TLabel',
                       font=('Arial', 14, 'bold'),
                       foreground=self.colors['secondary_color'],
                       background=self.colors['background_color'])
        
        style.configure('Info.TLabel',
                       font=('Arial', 10),
                       foreground=self.colors['text_color'],
                       background=self.colors['background_color'])
        
        # Button styles
        style.configure('Primary.TButton',
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background=self.colors['primary_color'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['secondary_color']),
                           ('pressed', self.colors['accent_color'])])
        
        style.configure('Success.TButton',
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background=self.colors['success_color'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Accent.TButton',
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background=self.colors['accent_color'],
                       borderwidth=0,
                       focuscolor='none')
        
        # Frame styles
        style.configure('Card.TFrame',
                       background='white',
                       relief='raised',
                       borderwidth=1)
        
        style.configure('Header.TFrame',
                       background=self.colors['primary_color'])
        
        # Notebook styles
        style.configure('TNotebook',
                       background=self.colors['background_color'],
                       borderwidth=0)
        
        style.configure('TNotebook.Tab',
                       font=('Arial', 11, 'bold'),
                       padding=[20, 10],
                       background=self.colors['background_color'],
                       foreground=self.colors['text_color'])
        
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary_color']),
                           ('active', self.colors['secondary_color'])],
                 foreground=[('selected', 'white'),
                           ('active', 'white')])
        
        # Treeview styles
        style.configure('Treeview',
                       font=('Arial', 10),
                       background='white',
                       foreground=self.colors['text_color'],
                       fieldbackground='white',
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Treeview.Heading',
                       font=('Arial', 11, 'bold'),
                       background=self.colors['primary_color'],
                       foreground='white',
                       borderwidth=1,
                       relief='raised')
        
        # Entry styles
        style.configure('TEntry',
                       font=('Arial', 10),
                       borderwidth=2,
                       relief='solid',
                       focuscolor=self.colors['accent_color'])
        
        # Combobox styles
        style.configure('TCombobox',
                       font=('Arial', 10),
                       borderwidth=2,
                       relief='solid')
        
        # LabelFrame styles
        style.configure('TLabelframe',
                       background=self.colors['background_color'],
                       borderwidth=2,
                       relief='groove')
        
        style.configure('TLabelframe.Label',
                       font=('Arial', 11, 'bold'),
                       foreground=self.colors['primary_color'],
                       background=self.colors['background_color'])
        
        # Configure root window
        root.configure(bg=self.colors['background_color'])
        
        return style
    
    def create_gradient_frame(self, parent, height=60):
        """Create a gradient header frame"""
        frame = tk.Frame(parent, height=height, bg=self.colors['primary_color'])
        
        # Add hotel name label
        hotel_label = tk.Label(frame, 
                              text="🏨 MADIT HOTEL INVENTORY",
                              font=('Arial', 16, 'bold'),
                              fg='white',
                              bg=self.colors['primary_color'])
        hotel_label.pack(expand=True)
        
        return frame
    
    def create_status_card(self, parent, title, value, color_key='primary_color'):
        """Create a status card widget"""
        card_frame = tk.Frame(parent, bg='white', relief='raised', bd=2, padx=15, pady=10)
        
        # Title
        title_label = tk.Label(card_frame,
                              text=title,
                              font=('Arial', 10, 'bold'),
                              fg=self.colors['text_color'],
                              bg='white')
        title_label.pack()
        
        # Value
        value_label = tk.Label(card_frame,
                              text=str(value),
                              font=('Arial', 24, 'bold'),
                              fg=self.colors[color_key],
                              bg='white')
        value_label.pack(pady=(5, 0))
        
        return card_frame
    
    def create_action_button(self, parent, text, command, style='Primary'):
        """Create a styled action button"""
        button = ttk.Button(parent, 
                           text=text, 
                           command=command,
                           style=f'{style}.TButton')
        return button
    
    def create_icon_button(self, parent, text, icon, command):
        """Create a button with icon and text"""
        button_frame = tk.Frame(parent, bg=self.colors['background_color'])
        
        button = tk.Button(button_frame,
                          text=f"{icon} {text}",
                          font=('Arial', 10, 'bold'),
                          fg='white',
                          bg=self.colors['primary_color'],
                          activebackground=self.colors['secondary_color'],
                          activeforeground='white',
                          border=0,
                          padx=15,
                          pady=8,
                          cursor='hand2',
                          command=command)
        button.pack()
        
        return button_frame
    
    def get_role_color(self, role):
        """Get color for user role"""
        role_colors = {
            'Admin': '#e74c3c',
            'Clerk': '#3498db', 
            'Stock User': '#f39c12'
        }
        return role_colors.get(role, self.colors['text_color'])

# Global theme instance
madit_theme = MaditTheme()