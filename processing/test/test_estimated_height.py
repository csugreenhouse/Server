# Server/processing/test/test_estimated_height.py
import importlib
from pathlib import Path
import os
import pytest

# Make sure Python can import "Server.processing.height" no matter the CWD
ROOT = Path(__file__).resolve().parents[2]  # repo root (contains "Server")
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

def test_image1_height_between_1_and_2():
    """
    For the sample image, the computed height_est should be in [1.0, 2.0].
    This uses get_height_metrics() directly (no barcode dependency).
    """
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "get_height_metrics"), "get_height_metrics() not found"

    img_path = Path(__file__).parent / "images" / "Image1.jpg"
    assert img_path.exists(), f"Missing test image: {img_path}"

    res = mod.get_height_metrics(str(img_path))
    assert "height_est" in res, "get_height_metrics() returned no 'height_est'"
    h = float(res["height_est"])

    # Allow a tiny tolerance for float math
    assert 1.0 <= h <= 2.0, f"Estimated height {h} not in expected range [1.0, 2.0]"


