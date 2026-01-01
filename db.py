import sqlite3

DB = "steelbeam.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            ibeam INTEGER,
            tbeam INTEGER,
            total INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_history(filename, ibeam, tbeam, total):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO history (filename, ibeam, tbeam, total) VALUES (?, ?, ?, ?)",
        (filename, ibeam, tbeam, total)
    )
    conn.commit()
    conn.close()

def fetch_history():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows