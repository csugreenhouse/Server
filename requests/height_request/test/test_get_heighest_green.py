# Server/processing/test/test_estimated_height.py
import importlib
from pathlib import Path
import os
import pytest
import cv2

# Make sure Python can import "Server.processing.height" no matter the CWD
ROOT = Path(__file__).resolve().parents[2]  # repo root (contains "Server")
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_get_heighest_green"

mod = importlib.import_module("height_request.height_estimator")

def test_heighest_green_01():
    src = IMG_DIR / "TEST01.jpg"
    dst = IMG_DIR / "TEST01_out.png"
    image = cv2.imread(str(src))
    
    assert hasattr(mod, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"

    heighest_green_pixel = mod.get_heighest_green_pixel(image)
    mod.plot_image(str(src), str(dst), heighest_green_pixel=heighest_green_pixel)
    
    assert 150 <= heighest_green_pixel[0] <= 170
    assert 120 <= heighest_green_pixel[1] <= 140
    

    


