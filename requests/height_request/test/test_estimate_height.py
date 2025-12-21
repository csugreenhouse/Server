import importlib
from pathlib import Path
import os
import pytest
from height_request import height_estimator
import cv2

# Make sure Python can import "Server.processing.height" no matter the CWD
ROOT = Path(__file__).resolve().parents[2]  # repo root (contains "Server")
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_estimate_height"

mod = importlib.import_module("height_request.height_estimator")

def test_methods_existence():
    assert hasattr(mod, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"
    assert hasattr(mod, "scan_apriltags"), "scan_apriltags() not found"
    assert hasattr(mod, "get_equation_of_line"), "get_equation_of_line() not found"
    assert hasattr(mod, "fractional_height_between_lines"), "fractional_height_between_lines() not found"
    assert hasattr(mod, "estimated_height"), "estimated_height() not found"
    assert hasattr(mod, "plot_image"), "plot_image() not found"

def test_estimate_height_6CM():
    src = IMG_DIR / "TEST_6CM.jpg"
    dst = IMG_DIR / "TEST_6CM_out.png"
    image = cv2.imread(str(src))
    april_list = mod.scan_apriltags(image)
    qr_list = mod.scan_qrtags(image)
    heighest_green_pixel = mod.get_heighest_green_pixel(image)
    estimated_height = mod.estimated_height(image,reference=april_list[0], scale_units_m=.070, bias_correction_b=0.01)
    mod.plot_image(str(src), str(dst), qr_list=qr_list, april_list = april_list, heighest_green_pixel=heighest_green_pixel, estimated_height=estimated_height)
    assert estimated_height == pytest.approx(.05, rel=.20)
    
def test_estimate_height_10CM():
    src = IMG_DIR / "TEST_10CM.jpg"
    dst = IMG_DIR / "TEST_10CM_out.png"
    image = cv2.imread(str(src))
    april_list = mod.scan_apriltags(image)
    qr_list = mod.scan_qrtags(image)
    estimated_height = mod.estimated_height(image,reference=april_list[0], scale_units_m=.070, bias_correction_b=0.01)
    heighest_green_pixel = mod.get_heighest_green_pixel(image)
    mod.plot_image(str(src), str(dst), qr_list=qr_list, april_list = april_list, heighest_green_pixel=heighest_green_pixel, estimated_height=estimated_height)
    assert estimated_height == pytest.approx(.10, rel=.20)

def test_estimate_height_16CM():
    src = IMG_DIR / "TEST_16CM.jpg"
    dst = IMG_DIR / "TEST_16CM_out.png"
    image = cv2.imread(str(src))
    april_list = mod.scan_apriltags(image)
    qr_list = mod.scan_qrtags(image)
    estimated_height = mod.estimated_height(image,reference=april_list[0], scale_units_m=.070, bias_correction_b=0.01)
    heighest_green_pixel = mod.get_heighest_green_pixel(image)
    mod.plot_image(str(src), str(dst), qr_list=qr_list, april_list = april_list, heighest_green_pixel=heighest_green_pixel, estimated_height=estimated_height)
    print(f"Estimated height: {estimated_height} m")
    
    assert estimated_height == pytest.approx(.16, rel=.20)




    

    