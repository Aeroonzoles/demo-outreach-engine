import smtplib
from email.message import EmailMessage
from .composer import compose, lint
from .db import is_suppressed, now

def draft_all(conn, cfg):
    rows = conn.execute("SELECT * FROM leads WHERE status='demo_built'").fetchall()
    for r in rows:
        s, b = compose(r, cfg)
        conn.execute("INSERT INTO emails(lead_id,subject,body) VALUES(?,?,?)", (r["id"], s, b))
        conn.execute("UPDATE leads SET status='drafted' WHERE id=?", (r["id"],))
    conn.commit()
    return len(rows), auto_approve(conn, cfg)

def approve(conn, ids=None):
    q = "UPDATE emails SET status='approved', approved_by='human' WHERE status='draft'"
    if ids:
        q += f" AND id IN ({','.join('?' * len(ids))})"
    n = conn.execute(q, ids or []).rowcount
    conn.commit()
    return n

def auto_approve(conn, cfg):
    """Auto-approval only starts after you have hand-approved review_first_n emails."""
    human = conn.execute("SELECT COUNT(*) FROM emails WHERE approved_by='human'").fetchone()[0]
    if human < cfg.review_first_n:
        return 0
    n = 0
    for e in conn.execute("SELECT * FROM emails WHERE status='draft'").fetchall():
        if not lint(e["body"], cfg):
            conn.execute("UPDATE emails SET status='approved', approved_by='auto' WHERE id=?", (e["id"],))
            n += 1
    conn.commit()
    return n

def sent_today(conn):
    return conn.execute("SELECT COUNT(*) FROM emails WHERE status='sent' AND date(sent_at)=date('now','localtime')").fetchone()[0]

def send_batch(conn, cfg, smtp_factory=None):
    room = cfg.daily_cap - sent_today(conn)
    if room <= 0:
        return 0
    rows = conn.execute("SELECT e.*, l.email AS to_addr FROM emails e JOIN leads l ON l.id=e.lead_id "
                        "WHERE e.status='approved' ORDER BY e.id").fetchall()
    rows = [r for r in rows if not is_suppressed(conn, r["to_addr"])]
    ok = []
    for r in rows:
        problems = lint(r["body"], cfg)
        if problems:
            print(f"[BLOCKED] #{r['id']} {problems}")
        else:
            ok.append(r)
    rows = ok[:room]
    smtp = None
    if not cfg.dry_run:
        smtp = smtp_factory() if smtp_factory else smtplib.SMTP(cfg.smtp_host, cfg.smtp_port)
        if not smtp_factory:
            smtp.starttls(); smtp.login(cfg.smtp_user, cfg.smtp_pass)
    for r in rows:
        if cfg.dry_run:
            print(f"[DRY RUN] to={r['to_addr']} subject={r['subject']}")
            continue
        m = EmailMessage()
        m["From"], m["To"], m["Subject"] = cfg.sender_email, r["to_addr"], r["subject"]
        m["List-Unsubscribe"] = f"<mailto:{cfg.sender_email}?subject=STOP>"
        m.set_content(r["body"])
        smtp.send_message(m)
        conn.execute("UPDATE emails SET status='sent', sent_at=? WHERE id=?", (now(), r["id"]))
        conn.execute("UPDATE leads SET status='sent' WHERE id=?", (r["lead_id"],))
    conn.commit()
    if smtp:
        smtp.quit()
    return 0 if cfg.dry_run else len(rows)
