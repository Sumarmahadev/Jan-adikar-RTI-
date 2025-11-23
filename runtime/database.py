import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path.cwd() / 'runtime' / 'rti_warrior.db'
DB_PATH.parent.mkdir(exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, phone TEXT, state TEXT, data TEXT, created_at TEXT, updated_at TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS pio_cache (key TEXT PRIMARY KEY, department TEXT, city TEXT, pio_address TEXT, source_url TEXT, confidence_score REAL, last_verified TEXT)''')
    conn.commit(); conn.close()


def get_db_conn():
    return sqlite3.connect(DB_PATH)