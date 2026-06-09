"""Make the simulator modules importable as top-level (`models`, `config`)
regardless of where pytest is launched from."""

import sys
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
if str(SIM_DIR) not in sys.path:
    sys.path.insert(0, str(SIM_DIR))
