import html, os, re

TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{name}</title>
<style>body{{font-family:system-ui,sans-serif;margin:0;color:#222}}
header{{background:#1f4e79;color:#fff;padding:48px 24px;text-align:center}}
main{{max-width:640px;margin:auto;padding:24px}}
.b{{background:#fff3cd;padding:8px;text-align:center;font-size:14px}}
a.btn{{display:inline-block;background:#25a244;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none}}</style></head>
<body><div class="b">Demo preview, not yet live</div>
<header><h1>{name}</h1><p>{category}{sep}{city}</p></header>
<main><h2>Contact us</h2>{contact}</main></body></html>"""

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "site"

def build_site(lead):
    e = lambda k: html.escape(lead[k] or "")
    phone = re.sub(r"\D", "", lead["phone"] or "")
    contact = f"<p>Email: {e('email')}</p>"
    if phone:
        contact += f'<p>Phone: {e("phone")}</p><a class="btn" href="https://wa.me/{phone}">Chat on WhatsApp</a>'
    sep = " &middot; " if lead["category"] and lead["city"] else ""
    return TEMPLATE.format(name=e("name"), category=e("category"), city=e("city"), sep=sep, contact=contact)

def build_all(conn, cfg):
    os.makedirs(cfg.demo_dir, exist_ok=True)
    rows = conn.execute("SELECT * FROM leads WHERE status='new'").fetchall()
    for r in rows:
        fn = f"{slug(r['name'])}-{r['id']}.html"
        with open(os.path.join(cfg.demo_dir, fn), "w", encoding="utf-8") as f:
            f.write(build_site(r))
        conn.execute("UPDATE leads SET status='demo_built', demo_file=? WHERE id=?", (fn, r["id"]))
    conn.commit()
    return len(rows)
