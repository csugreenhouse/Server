import importlib
from pathlib import Path
import os
import pytest
import cv2

ROOT = Path(__file__).resolve().parents[3] # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_height_request"

hr = importlib.import_module("plant_requests.height_request.height_request")
scanner_util = importlib.import_module("plant_requests.utils.reference_tag_util")
graph_util = importlib.import_module("plant_requests.utils.graph_util")

plastic_color_bounds = ((30, 60, 30),(90, 255, 200))
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

"""
def make_reference_tag(april_tag, scale_units_m, color_bounds, bias_units_m, plant_bounds):
    reference_tag = april_tag
    reference_tag["scale_units_m"] = scale_units_m
    reference_tag["color_bounds"] = color_bounds    
    reference_tag["bias_units_m"] = bias_units_m
    reference_tag["plant_bounds"] = plant_bounds
    reference_tag = reference_util.add_calculated_displacement_info_to_tag(
        test_camera_parameters,reference_tag)
    return reference_tag

def test_height_request_01():
    src = IMG_DIR / "test_height_request_00.jpg"
    dst = IMG_DIR / "test_height_request_00_out.png"
    image = cv2.imread(str(src))
    
    april_tags = scanner_util.scan_apriltags(image)
    april_1 = april_tags[0]
    april_2 = april_tags[1]
    reference_tag_1 = make_reference_tag(april_1,.07,plastic_color_bounds,.01,(.55,.8))
    reference_tag_2 = make_reference_tag(april_2,.07,plastic_color_bounds,.01,(.2,.5))
    
    reference_tags = [reference_tag_1, reference_tag_2]

    estimated_heights, estimated_heights_info = hr.height_request(image, reference_tags, test_camera_parameters)
    
    graph_util.plot_height_request_graph_info(image, dst, estimated_heights_info)
"""