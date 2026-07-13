import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    BASE_DIR = BASE_DIR

    # In production, set a real secret via environment variable:
    #   export SECRET_KEY="something-long-and-random"
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")

    # ---- Database ----
    # Locally: SQLite file (instance/voting.db) — persists permanently on
    # your own machine as long as you don't delete that file.
    #
    # On a host like Render: SQLite's disk is EPHEMERAL (wiped on redeploy/
    # sleep), so set a DATABASE_URL environment variable pointing at a real
    # Postgres database there instead — see README "Persistent Database" section.
    _raw_db_url = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "voting.db")
    )
    # Render (and some other hosts) hand out URLs starting with "postgres://",
    # but SQLAlchemy 2.x requires "postgresql://" — normalize it here.
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default admin account, created automatically the first time the app runs.
    # CHANGE THESE before you deploy anywhere public.
    DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

    # ---- Email (OTP delivery) ----
    # If MAIL_USERNAME / MAIL_PASSWORD are not set, the app falls back to
    # showing the OTP on-screen (demo mode) instead of emailing it.
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")          # e.g. your Gmail address
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")          # Gmail "App Password", not your normal password
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
