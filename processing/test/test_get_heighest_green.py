# Server/processing/test/test_estimated_height.py
import importlib
from pathlib import Path
import os
import pytest
from processing import height

# Make sure Python can import "Server.processing.height" no matter the CWD
ROOT = Path(__file__).resolve().parents[2]  # repo root (contains "Server")
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_get_heighest_green"

def test_heighest_green_01():
    src = IMG_DIR / "TEST01.jpg"
    dst = IMG_DIR / "TEST01_out.png"
    
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"
    
    heighest_green_pixel = mod.get_heighest_green_pixel(str(src))
    mod.plot_image(str(src), str(dst), heighest_green_pixel=heighest_green_pixel)
    
    assert heighest_green_pixel == (158, 129)  # Expected coordinates of the highest green pixel
    

    


