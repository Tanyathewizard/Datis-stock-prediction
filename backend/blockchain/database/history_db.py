import sqlite3

DB = "history.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        decision TEXT,
        confidence REAL,
        timestamp INTEGER,
        token_id TEXT,
        actual_result TEXT DEFAULT 'PENDING',
        price_at_predict REAL,
        price_at_resolve REAL
    )
    """)

    conn.commit()
    conn.close()


def fetch_all_history(symbol=None, limit=50, offset=0):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if symbol:
        c.execute("SELECT * FROM history WHERE symbol=? LIMIT ? OFFSET ?", (symbol, limit, offset))
    else:
        c.execute("SELECT * FROM history LIMIT ? OFFSET ?", (limit, offset))

    rows = c.fetchall()
    conn.close()

    return [dict(zip(
        ["id","symbol","decision","confidence","timestamp","token_id","actual_result","price_at_predict","price_at_resolve"],
        row
    )) for row in rows]


def fetch_resolved_predictions(symbol=None):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if symbol:
        c.execute("SELECT * FROM history WHERE actual_result!='PENDING' AND symbol=?", (symbol,))
    else:
        c.execute("SELECT * FROM history WHERE actual_result!='PENDING'")

    rows = c.fetchall()
    conn.close()

    return [dict(zip(
        ["id","symbol","decision","confidence","timestamp","token_id","actual_result","price_at_predict","price_at_resolve"],
        row
    )) for row in rows]


def update_outcome(prediction_id, actual_result, price_at_resolve):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    UPDATE history SET actual_result=?, price_at_resolve=?
    WHERE id=?
    """, (actual_result, price_at_resolve, prediction_id))

    conn.commit()
    updated = c.rowcount > 0
    conn.close()
    return updated


def update_outcome_by_token(token_id, actual_result, price_at_resolve):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    UPDATE history SET actual_result=?, price_at_resolve=?
    WHERE token_id=?
    """, (actual_result, price_at_resolve, token_id))

    conn.commit()
    updated = c.rowcount > 0
    conn.close()
    return updated


def count_predictions():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM history")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM history WHERE actual_result='CORRECT'")
    correct = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM history WHERE actual_result='INCORRECT'")
    incorrect = c.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "pending": total - correct - incorrect
    }