import importlib
from pathlib import Path
import os
import pytest
import height_request.height_estimator as mod
from debug.debug import plot_image
import cv2

# Make sure Python can import "Server.processing.height" no matter the CWD
ROOT = Path(__file__).resolve().parents[2]  # repo root (contains "Server")
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_estimate_height"

mod = importlib.import_module("height_request.height_estimator")

# darker green then lettuce
plastic_bounds = {
    # not detecting light greens
    "lower_green": (25, 60, 30),
    "upper_green": (70, 255, 200),
}

lettuce_bounds = {
    "lower_green": (30, 35, 30),
    "upper_green": (75, 255, 255)
}

def test_methods_existence():
    assert hasattr(mod, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"
    assert hasattr(mod, "scan_apriltags"), "scan_apriltags() not found"
    assert hasattr(mod, "get_equation_of_line"), "get_equation_of_line() not found"
    assert hasattr(mod, "fractional_height_between_lines"), "fractional_height_between_lines() not found"
    assert hasattr(mod, "estimate_height"), "estimate_height() not found"
    assert hasattr(mod, "scan_qrtags"), "scan_qrtags() not found"
    assert hasattr(mod, "scan_green_blobs"), "scan_green_blobs() not found"
    assert hasattr(mod, "plot_image"), "plot_image() not found"

def test_estimate_height_6CM():
    src = IMG_DIR / "TEST_6CM.jpg"
    dst = IMG_DIR / "TEST_6CM_out.png"
    image = cv2.imread(str(src))
    lower_green = plastic_bounds["lower_green"]
    upper_green = plastic_bounds["upper_green"]

    estimated_height_debug = mod.estimate_height_debug(image, method="apriltag", lower_green=lower_green, upper_green=upper_green, scale_units_m=.070, bias_correction_b=0.01)
    estimated_height = estimated_height_debug["estimated_height"]
    april_list = estimated_height_debug["april_list"]
    qr_list = estimated_height_debug["qr_list"]
    heighest_green_pixel = estimated_height_debug["heighest_green_pixel"]
    green_blob_list = estimated_height_debug["green_blob_list"]
    mod.plot_image(image, str(dst), qr_list=qr_list, april_list = april_list, heighest_green_pixel=heighest_green_pixel, estimated_height=estimated_height, green_blob_list=green_blob_list)
    assert estimated_height == pytest.approx(.06, rel=.20)
    
def test_estimate_height_10CM():
    src = IMG_DIR / "TEST_10CM.jpg"
    dst = IMG_DIR / "TEST_10CM_out.png"
    image = cv2.imread(str(src))
    lower_green = lettuce_bounds["lower_green"]
    upper_green = lettuce_bounds["upper_green"]
    estimated_height_debug = mod.estimate_height_debug(image, method="apriltag", lower_green=lower_green, upper_green=upper_green, scale_units_m=.070, bias_correction_b=0.01)
    estimated_height = estimated_height_debug["estimated_height"]
    april_list = estimated_height_debug["april_list"]
    qr_list = estimated_height_debug["qr_list"]
    heighest_green_pixel = estimated_height_debug["heighest_green_pixel"]
    green_blob_list = estimated_height_debug["green_blob_list"]
    mod.plot_image(image, str(dst), qr_list=qr_list, april_list = april_list, heighest_green_pixel=heighest_green_pixel, estimated_height=estimated_height, green_blob_list=green_blob_list)
    assert estimated_height == pytest.approx(.10, rel=.20)

def test_estimate_height_16CM():
    src = IMG_DIR / "TEST_16CM.jpg"
    dst = IMG_DIR / "TEST_16CM_out.png"
    image = cv2.imread(str(src))
    lower_green = plastic_bounds["lower_green"]
    upper_green = plastic_bounds["upper_green"]
    estimated_height_debug = mod.estimate_height_debug(image, method="apriltag", lower_green=lower_green, upper_green=upper_green, scale_units_m=.070, bias_correction_b=0.01)
    estimated_height = estimated_height_debug["estimated_height"]
    april_list = estimated_height_debug["april_list"]
    qr_list = estimated_height_debug["qr_list"]
    heighest_green_pixel = estimated_height_debug["heighest_green_pixel"]
    green_blob_list = estimated_height_debug["green_blob_list"]
    mod.plot_image(image, str(dst), qr_list=qr_list, april_list = april_list, heighest_green_pixel=heighest_green_pixel, estimated_height=estimated_height, green_blob_list=green_blob_list)
    print(f"Estimated height: {estimated_height} m")
    
    assert estimated_height == pytest.approx(.16, rel=.20)




    

    