import sqlite3
from datetime import datetime

DB_NAME = "fire_detection.db"


# 🔹 Initialize Database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        type TEXT,
        confidence REAL,
        snapshot_path TEXT
    )
    """)

    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()


# 🔹 Add Event
def add_event(event_type: str, confidence: float, snapshot_path: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO events (timestamp, type, confidence, snapshot_path)
    VALUES (?, ?, ?, ?)
    """, (timestamp, event_type, confidence, snapshot_path))

    conn.commit()
    conn.close()


# 🔹 Get Recent Events
def get_recent_events(limit: int = 50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, timestamp, type, confidence, snapshot_path
    FROM events
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "timestamp": row[1],
            "type": row[2],
            "confidence": row[3],
            "snapshot_path": row[4]
        }
        for row in rows
    ]


# 🔹 Get All Events (Pagination)
def get_all_events(limit: int = 50, offset: int = 0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, timestamp, type, confidence, snapshot_path
    FROM events
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "timestamp": row[1],
            "type": row[2],
            "confidence": row[3],
            "snapshot_path": row[4]
        }
        for row in rows
    ]


# 🔹 Daily Stats
def get_daily_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DATE(timestamp) as date, COUNT(*)
    FROM events
    GROUP BY DATE(timestamp)
    ORDER BY date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {"date": row[0], "count": row[1]}
        for row in rows
    ]


# 🔹 Get ALL Settings
def get_all_settings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()

    return {row[0]: row[1] for row in rows}


# 🔹 Get SINGLE Setting ✅ (FIX FOR YOUR ERROR)
def get_setting(key: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None


# 🔹 Set / Update Setting
def set_setting(key: str, value: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO settings (key, value)
    VALUES (?, ?)
    ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, (key, value))

    conn.commit()
    conn.close()