# Demo Outreach Engine

[![CI](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)

An AI-assisted pipeline for small web-design businesses: it builds a free demo website for local
businesses that don't have one, drafts a personalised email linking to the demo, and sends a small,
capped number per day. **Python standard library only, no dependencies.**

The focus of the project is **safe automation**: every step that could annoy a real person has a
guardrail, and each guardrail has a test.

## How it works

```
leads.csv -> import-leads -> build-demos -> draft -> review/approve -> send -> reply handling
```

| Stage | What it does |
|---|---|
| `import-leads` | Reads a CSV, rejects invalid or suppressed emails, skips duplicates |
| `build-demos` | Generates one static demo site per business (HTML-escaped) |
| `draft` | Writes one personalised email per lead |
| `review` / `approve` | You read and approve drafts by hand |
| `send` | Sends via SMTP, capped per day, only approved and clean emails |
| `reply` | Classifies replies; STOP adds the sender to a permanent suppression list |

## Guardrails
- **Dry run by default** (`DRY_RUN=true`): nothing is sent until you turn it off.
- **Daily cap** on sends (default 20).
- **Human review gate:** the first N emails (default 20) need manual approval before auto-approval starts.
- **Content lint**, checked at draft time and again at send time: blocks claims like "guarantee" or "page one", placeholder text such as "Your Name", and requires an opt-out line and sender identity.
- **Suppression list:** anyone who replies STOP is never contacted again.
- **One email per lead**, no follow-up spam. Replies are classified, never auto-answered.

## Quick start

Windows (PowerShell):
```powershell
copy .env.example .env          # then edit .env
copy leads.sample.csv leads.csv
python -m unittest discover -s tests -v
python -m outreach.cli import-leads leads.csv
python -m outreach.cli build-demos
python -m outreach.cli draft
python -m outreach.cli review
python -m outreach.cli approve
python -m outreach.cli send      # dry run until DRY_RUN=false
```
macOS / Linux: the same commands, with `cp` instead of `copy` and `python3` instead of `python`.

`.env`, `leads.csv` and `*.db` are git-ignored. Never commit them.

## Before sending real email
Host the `demos/` folder, send from your own domain with SPF/DKIM set up, source leads from the
official Google Places API or manual research (not scraping), and check the rules that apply to you
(in India: TRAI covers SMS and calls, the DPDP Act covers personal data). Confirm each business
really has no website before adding it to the list.

## Tests
`python -m unittest discover -s tests -v` covers the daily cap, suppression list, review gate,
dry run, placeholder blocking, reply classification and HTML escaping.

## Roadmap
LLM-written site copy and emails, IMAP reply fetching, Places API lead finder, web dashboard.
