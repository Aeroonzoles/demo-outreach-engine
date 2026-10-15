import re
from .db import suppress

STOP = re.compile(r"\b(stop|unsubscribe|remove me|do not contact|don't contact)\b", re.I)
BUY = re.compile(r"\b(interested|price|cost|how much|yes|go ahead|call me)\b", re.I)

def classify(text):
    if STOP.search(text):
        return "stop"
    if BUY.search(text):
        return "interested"
    return "other"

def ingest(conn, from_email, text):
    """Suppress on STOP, flag interested leads for YOU to answer. Nothing is auto-replied."""
    kind = classify(text)
    if kind == "stop":
        suppress(conn, from_email)
    elif kind == "interested":
        conn.execute("UPDATE leads SET status='interested' WHERE lower(email)=?", (from_email.lower(),))
        conn.commit()
    return kind
