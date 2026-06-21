"""
Gunicorn configuration for Render free tier (512MB RAM).

Key choices:
- 1 sync worker only: NLP pipeline (NLTK + pdfplumber + google-genai) uses ~230MB.
  Multiple workers would exceed the 512MB limit and cause 502 OOM crashes.
- timeout=120: Gemini API calls can take up to 30s; analysis pipeline ~60s total.
- preload_app=False: Do NOT preload — this forces lazy singleton init per-worker,
  keeping startup RAM under the limit so the healthcheck passes immediately.
"""
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# 1 sync worker to stay within 512MB Render free tier RAM limit
workers = 1
worker_class = "sync"

# Allow 120s for heavy analysis requests (Gemini + NLP pipeline)
timeout = 120

# Do NOT preload — keeps startup fast and RAM low for healthcheck
preload_app = False

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
