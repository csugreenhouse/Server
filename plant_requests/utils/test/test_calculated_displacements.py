import cv2
import os
import importlib
from pathlib import Path
import pytest


ROOT = Path(__file__).resolve().parents[3]  # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_calculated_displacements"

calculated_displacements_util = importlib.import_module("plant_requests.utils.info_getter_util")
scanner_util = importlib.import_module("plant_requests.utils.scanner_util")
graph_util = importlib.import_module("plant_requests.utils.graph_util")

camera_parameters = {
        "camera_id": 1,
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.168.0.11"
}

def test_methods_existence():
    assert hasattr(calculated_displacements_util, "calculate_displacement"), "calculate_displacement() not found"
    assert hasattr(scanner_util, "scan_apriltags"), "scan_apriltags() not found"
    #assert hasattr(graph_util, "plot_calculated_displacements_graph_info"), "plot_calculated_displacements_graph_info() not found"
    
def test_calculate_displacement():
    src = IMG_DIR / "test_01.jpg"
    dst = IMG_DIR / "test_01_out.png"

    image = cv2.imread(str(src))
    
    assert image is not None, "Failed to read test image"
    
    april_tag_list = scanner_util.scan_apriltags(image)
    
    displacements = calculated_displacements_util.calculate_displacement(
        camera_parameters=camera_parameters,
        reference_tag=april_tag_list[0]
    )
    
    