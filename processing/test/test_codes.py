# Server/processing/test/test_estimated_height.py
import importlib
from pathlib import Path
import os
import pytest
import apriltag
import array
# Make sure Python can import "Server.processing.height" no matter the CWD
ROOT = Path(__file__).resolve().parents[2]  # repo root (contains "Server")
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

def test_TEST01_apriltag_detection():
    """
    Test that the apriltag in TEST01.jpeg is detected correctly.
    """
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "scan_apriltag"), "scan_apriltag() not found"

    img_path = Path(__file__).parent / "images" / "TEST01.jpeg"
    assert img_path.exists(), f"Missing test image: {img_path}"

    try:
        tag = mod.scan_apriltag(str(img_path))
        assert tag is not None, "No tag returned"
        tag_id = tag["tag_id"]
        assert tag["tag_id"] == 1, f"Unexpected tag ID: {tag["tag_id"]}"
        assert tag["decision_margin"] > 40, f"Decision margin too low: {tag["decision_margin"]}"
        assert abs(tag["center"][0] - 1768)<1, "Tag center x is not correct"
        assert abs(tag["center"][0] - 1768)<1, "Tag center y is not correct"

        # tag corners are at [1398.66125489, 1485.99841309],\n       [2130.49340821, 1470.10461425],\n       [2145.83374023, 2211.55932617],\n       [1404.45263671, 2222.5925293 ]
        assert abs(tag["tag_corners"][0][0]-1398.66125489)<1, "Tag corner 0 x is not correct"
        assert abs(tag["tag_corners"][0][1]-1485.99841309)<1, "Tag corner 0 y is not correct"
        assert abs(tag["tag_corners"][1][0]-2130.49340821)<1, "Tag corner 1 x is not correct"
        assert abs(tag["tag_corners"][1][1]-1470.10461425)<1, "Tag corner 1 y is not correct"
        assert abs(tag["tag_corners"][2][0]-2145.83374023)<1, "Tag corner 2 x is not correct"
        assert abs(tag["tag_corners"][2][1]-2211.55932617)<1, "Tag corner 2 y is not correct"
        assert abs(tag["tag_corners"][3][0]-1404.45263671)<1, "Tag corner 3 x is not correct"
        assert abs(tag["tag_corners"][3][1]-2222.5925293)<1, "Tag corner 3 y is not correct"    

    except ValueError as e:
        pytest.fail(f"Apriltag detection failed: {e}")

def test_TEST02_apriltag_detection():
    """
    Test that the apriltag in TEST02.jpeg is detected correctly.
    """
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "scan_apriltag"), "scan_apriltag() not found"

    img_path = Path(__file__).parent / "images" / "TEST02.jpeg"
    assert img_path.exists(), f"Missing test image: {img_path}"

    try:
        tag = mod.scan_apriltag(str(img_path))
        assert tag is not None, "No tag returned"
        assert tag["tag_id"] == 2, f"Unexpected tag ID: {tag["tag_id"]}"
        assert tag["decision_margin"] > 40, f"Decision margin too low: {tag["decision_margin"]}"
        assert abs(tag["center"][0] - 1460)<1, "Tag center x is not correct"
        assert abs(tag["center"][1] - 1751)<1, "Tag center y is not correct"

    except ValueError as e:
        pytest.fail(f"Apriltag detection failed: {e}")

""""
def test_TEST03_apriltag_detection():
    
    Test that the apriltag in TEST03.jpeg is detected correctly.
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "scan_apriltag"), "scan_apriltag() not found"

    img_path = Path(__file__).parent / "images" / "TEST04.jpeg"
    assert img_path.exists(), f"Missing test image: {img_path}"
    
    try:
        tag = mod.scan_apriltag(str(img_path))

    except ValueError as e:
        pytest.fail(f"Apriltag detection failed: {e}")
"""

def test_TEST04_apriltag_detection():
    """
    Test that the apriltag in TEST01.jpeg is detected correctly.
    """
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "scan_apriltag"), "scan_apriltag() not found"

    img_path = Path(__file__).parent / "images" / "TEST04.jpeg"
    assert img_path.exists(), f"Missing test image: {img_path}"

    try:
        tag = mod.scan_apriltag(str(img_path))
        assert tag is not None, "No tag returned"
        assert tag["tag_id"] == 4, f"Unexpected tag ID: {tag["tag_id"]}"
        assert tag["decision_margin"] > 40, f"Decision margin too low: {tag["decision_margin"]}"
        assert abs(tag["center"][0] - 1666)<1, "Tag center x is not correct"
        assert abs(tag["center"][1] - 1741)<1, "Tag center y is not correct"

    except ValueError as e:
        pytest.fail(f"Apriltag detection failed: {e}")