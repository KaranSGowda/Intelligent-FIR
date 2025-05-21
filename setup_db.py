import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Define roles
ROLE_PUBLIC = "public"
ROLE_POLICE = "police"
ROLE_ADMIN = "admin"

# Database file path
DB_PATH = "fir_system.db"

def setup_database():
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating tables...")
    
    # Create users table
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create FIRs table
    cursor.execute('''
    CREATE TABLE firs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fir_number TEXT UNIQUE NOT NULL,
        complainant_id INTEGER NOT NULL,
        processing_officer_id INTEGER,
        status TEXT DEFAULT 'draft',
        urgency_level TEXT DEFAULT 'normal',
        incident_description TEXT,
        incident_location TEXT,
        incident_date TIMESTAMP,
        filed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        transcription TEXT,
        legal_sections TEXT,
        FOREIGN KEY (complainant_id) REFERENCES users (id),
        FOREIGN KEY (processing_officer_id) REFERENCES users (id)
    )
    ''')
    
    # Create evidence table
    cursor.execute('''
    CREATE TABLE evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fir_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        file_path TEXT NOT NULL,
        description TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (fir_id) REFERENCES firs (id)
    )
    ''')
    
    # Create legal_sections table
    cursor.execute('''
    CREATE TABLE legal_sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    print("Tables created successfully!")
    
    # Create demo users
    print("Creating demo users...")
    
    # Current timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Insert demo users
    users = [
        (
            'user', 'user@example.com', generate_password_hash('password'),
            'Demo User', ROLE_PUBLIC, '1234567890', '123 Main St', now
        ),
        (
            'police', 'police@example.com', generate_password_hash('password'),
            'Police Officer', ROLE_POLICE, '9876543210', 'Police Station', now
        ),
        (
            'admin', 'admin@example.com', generate_password_hash('password'),
            'System Admin', ROLE_ADMIN, '5555555555', 'Admin Office', now
        )
    ]
    
    cursor.executemany('''
    INSERT INTO users (username, email, password_hash, full_name, role, phone, address, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)
    
    # Insert some sample legal sections
    legal_sections = [
        ('IPC-302', 'Murder', 'Punishment for murder'),
        ('IPC-307', 'Attempted Murder', 'Attempt to murder'),
        ('IPC-354', 'Assault on Woman', 'Assault or criminal force to woman with intent to outrage her modesty'),
        ('IPC-379', 'Theft', 'Punishment for theft'),
        ('IPC-420', 'Cheating', 'Cheating and dishonestly inducing delivery of property'),
        ('IPC-376', 'Rape', 'Punishment for rape'),
        ('IPC-392', 'Robbery', 'Punishment for robbery'),
        ('IPC-323', 'Voluntarily Causing Hurt', 'Punishment for voluntarily causing hurt'),
        ('IPC-406', 'Criminal Breach of Trust', 'Punishment for criminal breach of trust'),
        ('IPC-499', 'Defamation', 'Defamation')
    ]
    
    cursor.executemany('''
    INSERT INTO legal_sections (code, name, description)
    VALUES (?, ?, ?)
    ''', legal_sections)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database setup completed successfully!")

if __name__ == "__main__":
    setup_database()
