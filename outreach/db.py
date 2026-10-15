import sqlite3, datetime as dt

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads(
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
  category TEXT, city TEXT, phone TEXT, status TEXT DEFAULT 'new', demo_file TEXT);
CREATE TABLE IF NOT EXISTS emails(
  id INTEGER PRIMARY KEY, lead_id INTEGER NOT NULL, subject TEXT, body TEXT,
  status TEXT DEFAULT 'draft', approved_by TEXT, sent_at TEXT);
CREATE TABLE IF NOT EXISTS suppression(email TEXT PRIMARY KEY, reason TEXT, added TEXT);
"""

def connect(path=":memory:"):
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c

def now():
    return dt.datetime.now().isoformat(timespec="seconds")

def suppress(conn, email, reason="stop"):
    conn.execute("INSERT OR REPLACE INTO suppression VALUES(?,?,?)", (email.lower(), reason, now()))
    conn.execute("UPDATE leads SET status='suppressed' WHERE lower(email)=?", (email.lower(),))
    conn.commit()

def is_suppressed(conn, email):
    return conn.execute("SELECT 1 FROM suppression WHERE email=?", (email.lower(),)).fetchone() is not None
