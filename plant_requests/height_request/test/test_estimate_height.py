import importlib
from pathlib import Path
import os
import pytest
import cv2

# Make sure Python can import modules from the repo root no matter the CWD
ROOT = Path(__file__).resolve().parents[3] # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_estimate_height"

mod = importlib.import_module("plant_requests.height_request.height_estimator")
graph = importlib.import_module("plant_requests.utils.graph_util")
scanner = importlib.import_module("plant_requests.data_request.data_request")

plastic_color_bounds = ((25, 60, 30),(70, 255, 200))
lettuce_color_bounds = ((30, 35, 30),(75, 255, 255))

def test_methods_existence():
    assert hasattr(mod, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"
    assert hasattr(mod, "scan_apriltags"), "scan_apriltags() not found"
    assert hasattr(mod, "get_equation_of_line"), "get_equation_of_line() not found"
    assert hasattr(mod, "fractional_height_between_lines"), "fractional_height_between_lines() not found"
    assert hasattr(mod, "estimate_height"), "estimate_height() not found"
    assert hasattr(mod, "scan_qrtags"), "scan_qrtags() not found"
    assert hasattr(mod, "scan_green_blobs"), "scan_green_blobs() not found"
    assert hasattr(graph, "plot_image_height"), "plot_image_height() not found"

def test_estimate_height_6CM():
    src = IMG_DIR / "TEST_6CM.jpg"
    dst = IMG_DIR / "TEST_6CM_out.png"
    image = cv2.imread(str(src))
    
    camera_parameters = scanner.get_camera_parameters(1)
    
    
    estimated_height, debug_info = mod.estimate_height(
        image,
        camera_parameters=camera_parameters,
        reference_type="apriltag",
        color_bounds=plastic_color_bounds,
        scale_units_m=.070,
        bias_correction_m=0.01
    )

    graph.plot_image_height(
        image,
        str(dst),
        debug_info=debug_info
    )
    
    assert estimated_height == pytest.approx(.06, rel=.20)
    
def test_estimate_height_10CM():
    src = IMG_DIR / "TEST_10CM.jpg"
    dst = IMG_DIR / "TEST_10CM_out.png"
    image = cv2.imread(str(src))
    
    camera_parameters = scanner.get_camera_parameters(1)
    
    estimated_height, debug_info = mod.estimate_height(
        image,
        camera_parameters=camera_parameters,
        reference_type="apriltag",
        color_bounds=plastic_color_bounds,
        scale_units_m=.070,
        bias_correction_m=0.01
    )
    
    graph.plot_image_height(
        image,
        str(dst),
        debug_info=debug_info
    )
    assert estimated_height == pytest.approx(.10, rel=.20)

def test_estimate_height_16CM():
    src = IMG_DIR / "TEST_16CM.jpg"
    dst = IMG_DIR / "TEST_16CM_out.png"
    image = cv2.imread(str(src))
    
    camera_parameters = scanner.get_camera_parameters(1)
    
    estimated_height, debug_info = mod.estimate_height(
        image,
        camera_parameters=camera_parameters,
        reference_type="apriltag",
        color_bounds=plastic_color_bounds,
        scale_units_m=.070,
        bias_correction_m=0.01
    )  
    graph.plot_image_height(
        image,
        str(dst),
        debug_info=debug_info
    )
    assert estimated_height == pytest.approx(.16, rel=.20)




    

    