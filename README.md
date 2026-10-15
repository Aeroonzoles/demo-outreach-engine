# Demo Outreach Engine

An AI-assisted pipeline that builds a free demo website for local businesses without one, drafts a
personalised email linking to it, and sends a small, capped number per day. Built with **zero
third-party dependencies** (Python standard library only).

**Pipeline:** `import-leads` → `build-demos` → `draft` → `review/approve` → `send` → `reply`

## Guardrails (the point of the project)
- `DRY_RUN=true` by default: nothing is sent until you turn it off.
- **Daily cap** on sends (default 20).
- **Human review gate:** you hand-approve the first N emails before auto-approval starts.
- **Content lint:** blocks "guarantee", "page one", placeholder text (e.g. "Your Name", "yourdomain.com"); requires an opt-out and sender identity. Checked again at send time.
- **Suppression list:** anyone who replies STOP is never contacted again.
- One email per lead, no follow-up spam. Replies are classified, never auto-answered.

## Run
```bash
cp .env.example .env            # fill in, never commit
python -m unittest discover -s tests -v
python -m outreach.cli import-leads leads.csv   # name,email,category,city,phone
python -m outreach.cli build-demos && python -m outreach.cli draft
python -m outreach.cli review && python -m outreach.cli approve
python -m outreach.cli send     # dry run until DRY_RUN=false
```

## Before real sending
Host the `demos/` folder, set SPF/DKIM on your sending domain, source leads from the official
Google Places API or manual research (not scraping), and check Indian rules (TRAI covers SMS/calls;
DPDP Act covers personal data) with a CA or lawyer.

## Roadmap
LLM-written site copy and emails, IMAP reply fetching, Places API lead finder, web dashboard.
