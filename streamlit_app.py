"""Entry point for Streamlit Community Cloud live demo."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.dashboard import main

main()
