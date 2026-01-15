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

hr = importlib.import_module("plant_requests.height_request.height_request")
graph_util = importlib.import_module("plant_requests.utils.graph_util")
reference_util = importlib.import_module("plant_requests.utils.reference_tag_util")

plastic_color_bounds = ((30, 10, 30),(70, 255, 200))
lettuce_color_bounds = ((30, 35, 30),(75, 255, 255))

test_camera_parameters = {
    "camera_id": 1,
    "width": 1024,
    "height": 768,
    "focal_length_mm": 3.6,
    "sensor_height_mm": 2.2684,
    "sensor_width_mm": 3.590,
    "ip_address": "192.168.0.11"
    }



def test_methods_existence():
    assert hasattr(hr, "estimate_height"), "estimate_height() not found"
    assert hasattr(reference_util, "scan_apriltags"), "scan_apriltags() not found"
    assert hasattr(reference_util, "get_first_april_tag_info"), "get_first_april_tag_info() not found"
    assert hasattr(graph_util, "plot_estimate_height_graph_info"), "plot_estimate_height_graph_info() not found"

def test_estimate_height_6CM():
    src = IMG_DIR / "test_6cm.jpg"
    dst = IMG_DIR / "test_6cm_out.png"
    image = cv2.imread(str(src))

    april_tag = reference_util.scan_apriltags(image)[0]
    reference_tag = april_tag
    reference_tag["scale_units_m"] = .07
    reference_tag["color_bounds"] = plastic_color_bounds
    reference_tag["bias_units_m"] = .01
    reference_tag["plant_bounds"] = (.35, .6)

    estimated_height, debug_info = hr.estimate_height(image, april_tag)

    graph_util.plot_estimate_height_graph_info(image, dst, debug_info)

    assert estimated_height == pytest.approx(.06, rel=.20)
    
def test_estimate_height_10CM():
    src = IMG_DIR / "test_10cm.jpg"
    dst = IMG_DIR / "test_10cm_out.png"
    image = cv2.imread(str(src))

    april_tag = reference_util.scan_apriltags(image)[0]
    reference_tag = april_tag
    reference_tag["scale_units_m"] = .065
    reference_tag["color_bounds"] = plastic_color_bounds
    reference_tag["bias_units_m"] = .01
    reference_tag["plant_bounds"] = (.30, .65)

    estimated_height, debug_info = hr.estimate_height(image, april_tag)

    graph_util.plot_estimate_height_graph_info(image, dst, debug_info)
    
    assert estimated_height == pytest.approx(.10, rel=.20)

def test_estimate_height_16CM():
    src = IMG_DIR / "test_16cm.jpg"
    dst = IMG_DIR / "test_16cm_out.png"
    image = cv2.imread(str(src))

    april_tag = reference_util.scan_apriltags(image)[0]
    reference_tag = april_tag
    reference_tag["scale_units_m"] = .065
    reference_tag["color_bounds"] = plastic_color_bounds
    reference_tag["bias_units_m"] = .01
    reference_tag["plant_bounds"] = (.3, .65)

    estimated_height, debug_info = hr.estimate_height(image, april_tag)

    graph_util.plot_estimate_height_graph_info(image, dst, debug_info)
    assert estimated_height == pytest.approx(.16, rel=.20)




    

    