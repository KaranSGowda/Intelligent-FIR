"""
Script to create a backup of the SQLite database for the Intelligent FIR System.
This script can be scheduled to run regularly using a task scheduler.
"""

import os
import sys
import shutil
import time
from datetime import datetime

# Configuration
DB_PATH = "fir_system.db"
BACKUP_DIR = "backups"
MAX_BACKUPS = 10  # Maximum number of backups to keep

def create_backup():
    """Create a backup of the database"""
    # Create backups directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found: {DB_PATH}")
        return False
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}/fir_system_{timestamp}.db"
    
    try:
        # Copy the database file
        shutil.copy2(DB_PATH, backup_path)
        print(f"Backup created: {backup_path}")
        
        # Get database size
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)  # Size in MB
        print(f"Backup size: {size_mb:.2f} MB")
        
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def cleanup_old_backups():
    """Remove old backups if there are more than MAX_BACKUPS"""
    try:
        # Get list of backup files
        backup_files = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("fir_system_") and filename.endswith(".db"):
                file_path = os.path.join(BACKUP_DIR, filename)
                backup_files.append((file_path, os.path.getmtime(file_path)))
        
        # Sort by modification time (oldest first)
        backup_files.sort(key=lambda x: x[1])
        
        # Remove oldest backups if there are too many
        if len(backup_files) > MAX_BACKUPS:
            files_to_remove = backup_files[:(len(backup_files) - MAX_BACKUPS)]
            for file_path, _ in files_to_remove:
                os.remove(file_path)
                print(f"Removed old backup: {file_path}")
            
            print(f"Kept {MAX_BACKUPS} most recent backups")
        
        return True
    except Exception as e:
        print(f"Error cleaning up old backups: {e}")
        return False

if __name__ == "__main__":
    print(f"=== SQLite Database Backup [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ===")
    
    # Create backup
    if create_backup():
        # Clean up old backups
        cleanup_old_backups()
        print("Backup completed successfully")
    else:
        print("Backup failed")
        sys.exit(1)
