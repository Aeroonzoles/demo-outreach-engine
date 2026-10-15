import os
from dataclasses import dataclass

@dataclass
class Config:
    db_path: str = "outreach.db"
    dry_run: bool = True
    daily_cap: int = 20
    review_first_n: int = 20
    sender_name: str = "Your Name"
    sender_email: str = "you@example.com"
    sender_address: str = "Bengaluru, India"
    sender_tagline: str = "web developer"
    sender_city: str = "Bengaluru"
    demo_base_url: str = "https://demos.example.com"
    demo_dir: str = "demos"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""

def _load_dotenv(path=".env"):
    """Tiny .env reader (no dependencies). Real environment variables win."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.split(" #")[0].strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

def load_config(**overrides) -> Config:
    _load_dotenv()
    e = os.environ.get
    cfg = Config(
        db_path=e("DB_PATH", "outreach.db"),
        dry_run=e("DRY_RUN", "true").lower() != "false",
        daily_cap=int(e("DAILY_CAP", "20")),
        review_first_n=int(e("REVIEW_FIRST_N", "20")),
        sender_name=e("SENDER_NAME", "Your Name"),
        sender_email=e("SENDER_EMAIL", "you@example.com"),
        sender_address=e("SENDER_ADDRESS", "Bengaluru, India"),
        sender_tagline=e("SENDER_TAGLINE", "web developer"),
        sender_city=e("SENDER_CITY", "Bengaluru"),
        demo_base_url=e("DEMO_BASE_URL", "https://demos.example.com"),
        smtp_host=e("SMTP_HOST", ""), smtp_port=int(e("SMTP_PORT", "587")),
        smtp_user=e("SMTP_USER", ""), smtp_pass=e("SMTP_PASS", ""),
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg
