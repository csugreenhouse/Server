# Server/processing/test/test_height.py
import importlib
import os
import pytest

# Ensure Python can find the package
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # points to Server/
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

def test_import_height():
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "generate_query")

def test_image_exists():
    img_path = Path(__file__).resolve().parent / "images" / "Image1.jpg"
    assert img_path.exists(), f"Missing test image: {img_path}"
