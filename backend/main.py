import sys
import os

# Ensure `app.*` imports resolve when Vercel runs from backend/
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app  # noqa: F401 — Vercel picks up `app` (ASGI)
