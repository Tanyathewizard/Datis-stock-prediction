import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

def _now() -> str:
    return datetime.utcnow().isoformat()

DB_PATH = "datis_portfolio.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cash        REAL    NOT NULL DEFAULT 10000.0,
            total_value REAL    NOT NULL DEFAULT 10000.0,
            pnl         REAL    NOT NULL DEFAULT 0.0,
            updated_at  TEXT    NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol     TEXT    NOT NULL UNIQUE,
            shares     REAL    NOT NULL DEFAULT 0,
            avg_price  REAL    NOT NULL DEFAULT 0,
            updated_at TEXT    NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trade_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol     TEXT NOT NULL,
            action     TEXT NOT NULL,
            shares     REAL NOT NULL,
            price      REAL NOT NULL,
            total      REAL NOT NULL,
            pnl        REAL NOT NULL DEFAULT 0,
            timestamp  TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prediction_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol      TEXT NOT NULL,
            predicted   TEXT NOT NULL,
            actual      TEXT,
            confidence  REAL,
            features    TEXT,
            timestamp   TEXT NOT NULL
        )
    """)
    cur.execute("SELECT COUNT(*) FROM portfolio")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO portfolio (cash, total_value, pnl, updated_at) VALUES (?, ?, ?, ?)",
            (10000.0, 10000.0, 0.0, _now()),
        )
    conn.commit()
    conn.close()

init_db()
