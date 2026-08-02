import sys
import os

# Append current directory and backend directory to Python sys path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app

# Entrypoint for Vercel Serverless Function
handler = app

