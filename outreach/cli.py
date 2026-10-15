import argparse
from .config import load_config
from .db import connect, suppress
from . import leads, sitegen, pipeline, replies

def main(argv=None):
    p = argparse.ArgumentParser(prog="outreach")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build-demos"); sub.add_parser("draft"); sub.add_parser("review")
    sub.add_parser("send"); sub.add_parser("stats")
    sub.add_parser("import-leads").add_argument("csv")
    a = sub.add_parser("approve"); a.add_argument("ids", nargs="*", type=int)
    s = sub.add_parser("suppress"); s.add_argument("email")
    r = sub.add_parser("reply"); r.add_argument("email"); r.add_argument("text")
    args = p.parse_args(argv)
    cfg = load_config(); db = connect(cfg.db_path)
    if args.cmd == "import-leads": print("added/skipped:", leads.import_csv(db, args.csv))
    elif args.cmd == "build-demos": print("demos built:", sitegen.build_all(db, cfg))
    elif args.cmd == "draft": print("drafted/auto-approved:", pipeline.draft_all(db, cfg))
    elif args.cmd == "review":
        for e in db.execute("SELECT * FROM emails WHERE status='draft'"):
            print(f"--- #{e['id']} {e['subject']}\n{e['body']}")
    elif args.cmd == "approve": print("approved:", pipeline.approve(db, args.ids or None))
    elif args.cmd == "send": print("sent:", pipeline.send_batch(db, cfg), "(dry run)" if cfg.dry_run else "")
    elif args.cmd == "suppress": suppress(db, args.email); print("suppressed")
    elif args.cmd == "reply": print("classified as:", replies.ingest(db, args.email, args.text))
    elif args.cmd == "stats":
        for st, n in db.execute("SELECT status, COUNT(*) FROM leads GROUP BY status"):
            print(f"{st}: {n}")

if __name__ == "__main__":
    main()
