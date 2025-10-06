#!/usr/bin/env python3
"""
Build script for creating standalone executable of Hotel Inventory Management System
This script uses PyInstaller to create a distributable executable
"""

import os
import sys
import subprocess
import shutil
import platform

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("📦 Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install PyInstaller")
        return False

def create_spec_file():
    """Create PyInstaller spec file for better control"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'sqlite3',
        'bcrypt',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'pandas',
        'reportlab',
        'playsound'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HotelInventorySystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one
)
'''
    
    with open('HotelInventorySystem.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Spec file created: HotelInventorySystem.spec")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # Create spec file for better control
    create_spec_file()
    
    try:
        # Build using spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "HotelInventorySystem.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        
        print("✅ Executable built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_distribution_package():
    """Create a distribution package with executable and necessary files"""
    print("📦 Creating distribution package...")
    
    # Determine platform
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # Create distribution directory
    dist_name = f"HotelInventorySystem_{system}_{arch}"
    dist_dir = f"dist/{dist_name}"
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    os.makedirs(dist_dir, exist_ok=True)
    
    # Copy executable
    exe_name = "HotelInventorySystem.exe" if system == "windows" else "HotelInventorySystem"
    exe_source = f"dist/{exe_name}"
    
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, dist_dir)
        print(f"✅ Copied executable: {exe_name}")
    else:
        print(f"❌ Executable not found: {exe_source}")
        return False
    
    # Copy essential files
    essential_files = [
        "README.md",
        "config.json",
        "requirements.txt"
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir)
            print(f"✅ Copied: {file}")
    
    # Create directories
    os.makedirs(f"{dist_dir}/backups", exist_ok=True)
    os.makedirs(f"{dist_dir}/reports", exist_ok=True)
    
    # Create startup script
    if system == "windows":
        startup_script = f"{dist_dir}/start.bat"
        with open(startup_script, 'w') as f:
            f.write(f'''@echo off
echo Starting Hotel Inventory Management System...
{exe_name}
pause
''')
    else:
        startup_script = f"{dist_dir}/start.sh"
        with open(startup_script, 'w') as f:
            f.write(f'''#!/bin/bash
echo "Starting Hotel Inventory Management System..."
./{exe_name}
''')
        os.chmod(startup_script, 0o755)
    
    print(f"✅ Created startup script: {os.path.basename(startup_script)}")
    
    # Create installation instructions
    install_instructions = f"{dist_dir}/INSTALL.txt"
    with open(install_instructions, 'w') as f:
        f.write(f'''Hotel Inventory Management System - Installation Instructions

SYSTEM REQUIREMENTS:
- Operating System: {system.title()} ({arch})
- No additional software required (standalone executable)

INSTALLATION:
1. Extract all files to a folder of your choice
2. Run the executable:
   - Windows: Double-click HotelInventorySystem.exe or run start.bat
   - Linux/Mac: Run ./HotelInventorySystem or ./start.sh

FIRST RUN:
- Default login credentials:
  Username: admin
  Password: admin123
- Please change the default password after first login!

FOLDERS:
- backups/: Database backup files will be stored here
- reports/: Exported reports will be saved here

CONFIGURATION:
- Edit config.json to customize application settings
- Backup your data regularly using the built-in backup feature

SUPPORT:
- Refer to README.md for detailed usage instructions
- Check the application logs for troubleshooting

VERSION: 1.0.0
BUILD DATE: {subprocess.check_output(['date'], shell=True, text=True).strip() if system != 'windows' else 'N/A'}
''')
    
    print(f"✅ Created installation instructions: INSTALL.txt")
    
    # Create archive
    archive_name = f"{dist_name}"
    print(f"📦 Creating archive: {archive_name}")
    
    try:
        if system == "windows":
            # Create ZIP archive
            shutil.make_archive(f"dist/{archive_name}", 'zip', dist_dir)
            print(f"✅ Created ZIP archive: {archive_name}.zip")
        else:
            # Create TAR.GZ archive
            shutil.make_archive(f"dist/{archive_name}", 'gztar', dist_dir)
            print(f"✅ Created TAR.GZ archive: {archive_name}.tar.gz")
    except Exception as e:
        print(f"⚠️ Archive creation failed: {e}")
    
    print(f"✅ Distribution package created: {dist_dir}")
    return True

def cleanup():
    """Clean up build artifacts"""
    print("🧹 Cleaning up build artifacts...")
    
    cleanup_items = [
        "build",
        "__pycache__",
        "*.pyc",
        "HotelInventorySystem.spec"
    ]
    
    for item in cleanup_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
            print(f"✅ Removed: {item}")

def main():
    """Main build function"""
    print("🏨 Hotel Inventory Management System - Build Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found")
        print("Please run this script from the hotel_inventory_system directory")
        return
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("📦 PyInstaller not found. Installing...")
        if not install_pyinstaller():
            print("❌ Cannot proceed without PyInstaller")
            return
    
    print("✅ PyInstaller is available")
    
    # Build executable
    if not build_executable():
        print("❌ Build failed")
        return
    
    # Create distribution package
    if not create_distribution_package():
        print("❌ Distribution package creation failed")
        return
    
    # Cleanup
    cleanup()
    
    print("\n🎉 Build completed successfully!")
    print("📁 Check the 'dist' folder for your executable and distribution package")
    print("\n📋 Next steps:")
    print("1. Test the executable on your target system")
    print("2. Distribute the package to end users")
    print("3. Provide installation instructions (included in package)")

if __name__ == "__main__":
    main()