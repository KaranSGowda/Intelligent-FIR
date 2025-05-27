"""
Script to check the database for IPC sections.
"""

import os
import sys
import logging
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

def check_database():
    """Check the database for IPC sections."""
    try:
        # Connect to the database
        conn = sqlite3.connect('fir_system.db')
        cursor = conn.cursor()
        
        # Check if the legal_sections table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='legal_sections'")
        if not cursor.fetchone():
            logger.error("The legal_sections table does not exist in the database")
            return
        
        # Count the total number of sections
        cursor.execute("SELECT COUNT(*) FROM legal_sections")
        total_sections = cursor.fetchone()[0]
        logger.info(f"Total IPC sections in the database: {total_sections}")
        
        # Get a sample of sections
        cursor.execute("SELECT code, name FROM legal_sections ORDER BY code LIMIT 10")
        sample_sections = cursor.fetchall()
        logger.info("Sample IPC sections:")
        for code, name in sample_sections:
            logger.info(f"- Section {code}: {name}")
        
        # Close the connection
        conn.close()
    
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")

if __name__ == "__main__":
    check_database()
