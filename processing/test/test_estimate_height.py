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
IMG_DIR = BASE_DIR / "images" / "test_estimate_height"

def test_linear_algebra_helpers():
    src = IMG_DIR / "TEST_6CM.jpg"
    dst = IMG_DIR / "TEST_6CM_out.png"

    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "get_equation_of_line"), "get_equation_of_line() not found"
    assert hasattr(mod, "fractional_height_between_lines"), "fractional_height_between_lines() not found"   
    assert hasattr(mod, "scan_apriltags"), "scan_apriltags() not found"
    assert hasattr(mod, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"

    april_list = mod.scan_apriltags(str(src))
    heighest_green_pixel = mod.get_heighest_green_pixel(str(src))
    top_right = april_list[0]["corners"]["top_right"]
    top_left = april_list[0]["corners"]["top_left"]
    bottom_right = april_list[0]["corners"]["bottom_right"]
    bottom_left = april_list[0]["corners"]["bottom_left"]   
    equation_top = mod.get_equation_of_line(top_left, top_right)
    equation_bottom = mod.get_equation_of_line(bottom_left, bottom_right)
    fractional_height = mod.fractional_height_between_lines(equation_top, equation_bottom, heighest_green_pixel)

    assert fractional_height == pytest.approx(0.6, rel=.1)



def test_estimate_height_6CM():
    src = IMG_DIR / "TEST_6CM.jpg"
    dst = IMG_DIR / "TEST_6CM_out.png"
    
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "estimated_height"), "estimated_height() not found"
    assert hasattr(mod, "plot_image"), "plot_image() not found"
    assert hasattr(mod, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"
    assert hasattr(mod, "scan_apriltags"), "scan_apriltags() not found"
    assert hasattr
    
    
    estimated_height = mod.estimated_height(str(src),scale_units_m=.070, bias_correction_m=0.01)
    april_list = mod.scan_apriltags(str(src))
    heighest_green_pixel = mod.get_heighest_green_pixel(str(src))
    
    mod.plot_image(str(src), str(dst), april_list = april_list, heighest_green_pixel=heighest_green_pixel, estimated_height=estimated_height)
    
    print(f"Estimated height: {estimated_height} m")
    
    assert estimated_height == pytest.approx(.05, rel=.20)

def test_estimate_height_16CM():
    src = IMG_DIR / "TEST_16CM.jpg"
    dst = IMG_DIR / "TEST_16CM_out.png"
    
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "estimated_height"), "estimated_height() not found"
    assert hasattr(mod, "plot_image"), "plot_image() not found"
    assert hasattr(mod, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"
    assert hasattr(mod, "scan_apriltags"), "scan_apriltags() not found"
    
    estimated_height = mod.estimated_height(str(src),scale_units_m=.070, bias_correction_m=0.01)
    april_list = mod.scan_apriltags(str(src))
    heighest_green_pixel = mod.get_heighest_green_pixel(str(src))
    
    mod.plot_image(str(src), str(dst), april_list = april_list, heighest_green_pixel=heighest_green_pixel, estimated_height=estimated_height)
    
    print(f"Estimated height: {estimated_height} m")
    
    assert estimated_height == pytest.approx(.16, rel=.20)

def test_estimate_height_10CM():
    src = IMG_DIR / "TEST_10CM.jpg"
    dst = IMG_DIR / "TEST_10CM_out.png"
    
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "estimated_height"), "estimated_height() not found"
    assert hasattr(mod, "plot_image"), "plot_image() not found"
    assert hasattr(mod, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"
    assert hasattr(mod, "scan_apriltags"), "scan_apriltags() not found"
    
    estimated_height = mod.estimated_height(str(src),scale_units_m=.070, bias_correction_m=0.01)
    april_list = mod.scan_apriltags(str(src))
    heighest_green_pixel = mod.get_heighest_green_pixel(str(src))
    
    mod.plot_image(str(src), str(dst), april_list = april_list, heighest_green_pixel=heighest_green_pixel, estimated_height=estimated_height)
    
    print(f"Estimated height: {estimated_height} m")
    
    assert estimated_height == pytest.approx(.10, rel=.20)



    

    