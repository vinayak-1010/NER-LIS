"""
scripts/reset.py — Drops and recreates all tables. Use in development only.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import engine, Base
from app.models import models  # noqa — register all models

def run():
    print("⚠️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("🔨 Recreating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Reset complete.")

if __name__ == "__main__":
    run()
