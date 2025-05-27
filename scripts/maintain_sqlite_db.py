"""
Script to maintain and optimize the SQLite database for the Intelligent FIR System.
This script provides utilities for:
1. Creating database backups
2. Vacuuming the database to reclaim space
3. Analyzing the database for statistics
4. Checking database integrity
5. Displaying database information
"""

import os
import sys
import sqlite3
import time
from datetime import datetime
import shutil

# Database file path
DB_PATH = "fir_system.db"
BACKUP_DIR = "backups"

def create_backup():
    """Create a backup of the database"""
    # Create backups directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}/fir_system_{timestamp}.db"
    
    try:
        # Check if database file exists
        if not os.path.exists(DB_PATH):
            print(f"❌ Database file not found: {DB_PATH}")
            return False
            
        # Copy the database file
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Database backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating database backup: {e}")
        return False

def vacuum_database():
    """Vacuum the database to reclaim space and defragment"""
    try:
        print("Vacuuming database (this may take a while)...")
        start_time = time.time()
        
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        
        # Get database size before vacuum
        size_before = os.path.getsize(DB_PATH) / (1024 * 1024)  # Size in MB
        
        # Vacuum the database
        conn.execute("VACUUM;")
        
        # Close connection
        conn.close()
        
        # Get database size after vacuum
        size_after = os.path.getsize(DB_PATH) / (1024 * 1024)  # Size in MB
        
        # Calculate time taken and space saved
        time_taken = time.time() - start_time
        space_saved = size_before - size_after
        
        print(f"✅ Database vacuumed successfully in {time_taken:.2f} seconds")
        print(f"   Size before: {size_before:.2f} MB")
        print(f"   Size after: {size_after:.2f} MB")
        print(f"   Space saved: {space_saved:.2f} MB")
        
        return True
    except Exception as e:
        print(f"❌ Error vacuuming database: {e}")
        return False

def analyze_database():
    """Analyze the database to update statistics"""
    try:
        print("Analyzing database...")
        
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Analyze the database
        cursor.execute("ANALYZE;")
        
        # Close connection
        conn.close()
        
        print("✅ Database analyzed successfully")
        return True
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")
        return False

def check_integrity():
    """Check database integrity"""
    try:
        print("Checking database integrity...")
        
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check integrity
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]
        
        # Close connection
        conn.close()
        
        if result == "ok":
            print("✅ Database integrity check passed")
            return True
        else:
            print(f"❌ Database integrity check failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Error checking database integrity: {e}")
        return False

def display_database_info():
    """Display information about the database"""
    try:
        # Check if database file exists
        if not os.path.exists(DB_PATH):
            print(f"❌ Database file not found: {DB_PATH}")
            return
            
        # Get database file size
        size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)  # Size in MB
        
        # Get database modification time
        mod_time = datetime.fromtimestamp(os.path.getmtime(DB_PATH))
        
        print(f"Database file: {DB_PATH}")
        print(f"Size: {size_mb:.2f} MB")
        print(f"Last modified: {mod_time}")
        
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get SQLite version
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()[0]
        print(f"SQLite version: {version}")
        
        # Get journal mode
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0]
        print(f"Journal mode: {journal_mode}")
        
        # Get synchronous mode
        cursor.execute("PRAGMA synchronous;")
        synchronous = cursor.fetchone()[0]
        print(f"Synchronous mode: {synchronous}")
        
        # Get page size
        cursor.execute("PRAGMA page_size;")
        page_size = cursor.fetchone()[0]
        print(f"Page size: {page_size} bytes")
        
        # Get page count
        cursor.execute("PRAGMA page_count;")
        page_count = cursor.fetchone()[0]
        print(f"Page count: {page_count}")
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nTables in database: {len(tables)}")
        
        # Get row counts for each table
        for table in tables:
            table_name = table[0]
            if table_name.startswith("sqlite_"):
                continue  # Skip SQLite internal tables
                
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"  - {table_name}: {row_count} rows")
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"❌ Error displaying database information: {e}")

def main():
    """Main function to run the maintenance script"""
    print("=== Intelligent FIR System - SQLite Database Maintenance ===\n")
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found: {DB_PATH}")
        print("Please run setup_sqlite_db.py first to create the database.")
        sys.exit(1)
    
    # Display menu
    while True:
        print("\nMaintenance Options:")
        print("1. Create database backup")
        print("2. Vacuum database (reclaim space)")
        print("3. Analyze database (update statistics)")
        print("4. Check database integrity")
        print("5. Display database information")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            create_backup()
        elif choice == "2":
            # Create backup before vacuum
            print("Creating backup before vacuum...")
            if create_backup():
                vacuum_database()
        elif choice == "3":
            analyze_database()
        elif choice == "4":
            check_integrity()
        elif choice == "5":
            display_database_info()
        elif choice == "6":
            print("Exiting maintenance script.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
