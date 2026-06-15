# Vercel serverless entrypoint.
# Vercel's Python runtime detects the ASGI `app` exported here and serves it.
# All routes are forwarded to this function via the rewrite in vercel.json.
from app.main import app  # noqa: F401
