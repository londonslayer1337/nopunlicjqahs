import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "osint_history.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query_type TEXT,
            query_value TEXT,
            result_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_search(user_id: int, query_type: str, query_value: str, result: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO searches (user_id, query_type, query_value, result_summary) VALUES (?, ?, ?, ?)",
        (user_id, query_type, query_value, result)
    )
    conn.commit()
    conn.close()
