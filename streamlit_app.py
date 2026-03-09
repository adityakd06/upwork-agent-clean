import sys
import os

# Make sure the project root is on the path so all `app.*` imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui import *  # noqa: F401, F403 — triggers the Streamlit UI
