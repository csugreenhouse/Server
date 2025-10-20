# Server/processing/test/conftest.py
import sys
from pathlib import Path

# Insert the directory that CONTAINS "Server" into sys.path
root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
