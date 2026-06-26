import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")


def get():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    conn = get()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            registered_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            notified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(date, time)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def add_user(user_id, username=None, full_name=None):
    conn = get()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
        (user_id, username, full_name),
    )
    conn.commit()
    conn.close()


def add_appointment(user_id, name, phone, service, date, time):
    conn = get()
    try:
        cur = conn.execute(
            "INSERT INTO appointments (user_id, name, phone, service, date, time) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, name, phone, service, date, time),
        )
        conn.commit()
        last_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return None
    conn.close()
    return last_id


def get_booked_slots(date):
    conn = get()
    rows = conn.execute(
        "SELECT time FROM appointments WHERE date = ? AND status = 'active'",
        (date,),
    ).fetchall()
    conn.close()
    return {r["time"] for r in rows}


def get_user_appointments(user_id):
    conn = get()
    rows = conn.execute(
        "SELECT * FROM appointments WHERE user_id = ? AND status = 'active' ORDER BY date, time",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cancel_appointment(appointment_id, user_id):
    conn = get()
    conn.execute(
        "UPDATE appointments SET status = 'cancelled' WHERE id = ? AND user_id = ?",
        (appointment_id, user_id),
    )
    conn.commit()
    conn.close()


def get_upcoming_appointments(hours=1):
    conn = get()
    rows = conn.execute(
        "SELECT * FROM appointments WHERE status = 'active' AND notified = 0 AND date = date('now', '+1 day')",
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_notified(appointment_id):
    conn = get()
    conn.execute("UPDATE appointments SET notified = 1 WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()


def add_review(user_id, rating, comment=""):
    conn = get()
    conn.execute(
        "INSERT INTO reviews (user_id, rating, comment) VALUES (?, ?, ?)",
        (user_id, rating, comment),
    )
    conn.commit()
    conn.close()


def get_today_appointments():
    conn = get()
    rows = conn.execute(
        "SELECT * FROM appointments WHERE status = 'active' AND date = date('now') ORDER BY time",
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = get()
    users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    today = conn.execute("SELECT COUNT(*) FROM appointments WHERE date = date('now')").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM appointments WHERE status = 'active'").fetchone()[0]
    conn.close()
    return {"users": users, "today": today, "active": active}
