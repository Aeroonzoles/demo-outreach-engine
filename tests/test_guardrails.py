import unittest
from unittest.mock import MagicMock
from outreach.config import load_config
from outreach.db import connect, suppress
from outreach import pipeline, replies, sitegen
from outreach.composer import lint

def setup(n=5, **kw):
    cfg = load_config(dry_run=False, review_first_n=0, demo_dir="/tmp/_demos", sender_name="Test Dev",
                      sender_email="dev@realsite.in", demo_base_url="https://demos.realsite.in", **kw)
    db = connect()
    for i in range(n):
        db.execute("INSERT INTO leads(name,email,category,city) VALUES(?,?,?,?)",
                   (f"Shop {i}", f"s{i}@x.com", "salon", "Bengaluru"))
    db.commit()
    sitegen.build_all(db, cfg)
    pipeline.draft_all(db, cfg)
    return cfg, db

class Guardrails(unittest.TestCase):
    def test_daily_cap(self):
        cfg, db = setup(5, daily_cap=3)
        self.addCleanup(db.close)
        smtp = MagicMock()
        self.assertEqual(pipeline.send_batch(db, cfg, lambda: smtp), 3)
        self.assertEqual(pipeline.send_batch(db, cfg, lambda: smtp), 0)

    def test_suppressed_never_sent(self):
        cfg, db = setup(2, daily_cap=10)
        self.addCleanup(db.close)
        suppress(db, "s0@x.com")
        self.assertEqual(pipeline.send_batch(db, cfg, lambda: MagicMock()), 1)

    def test_review_gate_blocks_auto_approval(self):
        cfg, db = setup(3, daily_cap=10)
        self.addCleanup(db.close)
        cfg.review_first_n = 10
        db.execute("UPDATE emails SET status='draft', approved_by=NULL"); db.commit()
        self.assertEqual(pipeline.auto_approve(db, cfg), 0)

    def test_placeholder_text_blocks_send(self):
        cfg, db = setup(2, daily_cap=10)
        self.addCleanup(db.close)
        cfg.sender_name = "Your Name"
        db.execute("UPDATE emails SET body=body || ' Your Name'"); db.commit()
        self.assertEqual(pipeline.send_batch(db, cfg, lambda: MagicMock()), 0)

    def test_dry_run_sends_nothing(self):
        cfg, db = setup(2, daily_cap=10)
        self.addCleanup(db.close)
        cfg.dry_run = True
        self.assertEqual(pipeline.send_batch(db, cfg), 0)

    def test_lint_and_replies_and_escaping(self):
        cfg = load_config()
        self.assertTrue(lint("We guarantee page one", cfg))
        self.assertEqual(replies.classify("Please STOP emailing"), "stop")
        lead = {"name": "<script>x</script>", "email": "a@b.com", "category": "", "city": "", "phone": ""}
        self.assertNotIn("<script>", sitegen.build_site(lead))

if __name__ == "__main__":
    unittest.main()
