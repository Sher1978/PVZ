import sys
import os

# Append backend directory to Python sys path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app

# Entrypoint for Vercel Serverless Function
handler = app
