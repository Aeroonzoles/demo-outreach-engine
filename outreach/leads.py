import csv, re
from .db import is_suppressed

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def import_csv(conn, path):
    """CSV columns: name,email,category,city,phone. Source your list from the official
    Google Places API or manual research -- do not scrape Maps (against its terms)."""
    added = skipped = 0
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            email = (r.get("email") or "").strip().lower()
            if not r.get("name") or not EMAIL_RE.match(email) or is_suppressed(conn, email):
                skipped += 1
                continue
            cur = conn.execute(
                "INSERT OR IGNORE INTO leads(name,email,category,city,phone) VALUES(?,?,?,?,?)",
                (r["name"].strip(), email, r.get("category", ""), r.get("city", ""), r.get("phone", "")))
            added += cur.rowcount
            skipped += 1 - cur.rowcount
    conn.commit()
    return added, skipped
