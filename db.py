import sqlite3

def init_db():
    conn = sqlite3.connect("steelbeam.db")
    cur = conn.cursor()
    
    # User Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # History Table (Updated with employee_id)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            processed_file TEXT,
            ibeam INTEGER,
            tbeam INTEGER,
            total INTEGER,
            status TEXT,
            employee_id TEXT, 
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()