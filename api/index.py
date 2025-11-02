"""
Vercel Serverless Function Adapter for FastAPI
This file adapts the FastAPI app to run as a Vercel serverless function.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.main import app
