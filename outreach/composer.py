PLACEHOLDERS = ["your name", "yourdomain.com", "example.com", "your postal"]
BANNED = ["guarantee", "page one", "#1", "100%", "free money", "act now"]

def compose(lead, cfg):
    url = f"{cfg.demo_base_url.rstrip('/')}/{lead['demo_file']}"
    subject = f"A free website demo for {lead['name']}"
    body = (f"Hi {lead['name']} team,\n\n"
            f"I'm {cfg.sender_name}, a {cfg.sender_tagline} in {cfg.sender_city}. I couldn't find a website "
            f"for {lead['name']}, so I built a quick demo from the details I found publicly:\n\n{url}\n\n"
            "If you like it, I can customise it and put it online for you. If not, no problem at all.\n\n"
            "Reply STOP and I won't contact you again.\n\n"
            f"{cfg.sender_name}\n{cfg.sender_email}\n{cfg.sender_address}\n")
    return subject, body

def lint(body, cfg):
    """Return a list of problems; empty means OK to auto-approve."""
    low = body.lower()
    problems = [f"banned phrase: {p}" for p in BANNED if p in low]
    problems += [f"placeholder text: {p}" for p in PLACEHOLDERS if p in low]
    if "stop" not in low:
        problems.append("missing opt-out")
    if cfg.sender_email not in body:
        problems.append("missing sender identity")
    return problems
