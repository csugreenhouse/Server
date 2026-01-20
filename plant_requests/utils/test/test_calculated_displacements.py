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

reference_util = importlib.import_module("plant_requests.utils.reference_tag_util")
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
    assert hasattr(reference_util, "calculate_displacement"), "calculate_displacement() not found"
    assert hasattr(reference_util, "scan_apriltags"), "scan_apriltags() not found"
    #assert hasattr(graph_util, "plot_calculated_displacements_graph_info"), "plot_calculated_displacements_graph_info() not found"
    
def test_calculate_displacement_01():
    src = IMG_DIR / "test_01.jpg"
    dst = IMG_DIR / "test_01_out.png"

    image = cv2.imread(str(src))
    
    assert image is not None, "Failed to read test image"
    
    april_tag_list = reference_util.scan_apriltags(image)
    april_tag = april_tag_list[0]
    april_tag["scale_units_m"]=.065
    reference_tag = reference_util.add_calculated_displacement_info_to_tag(
        camera_parameters=camera_parameters,
        reference_tag=april_tag
    )
    
    displacement_d = reference_tag["displacements"]["d"]
    displacement_z = reference_tag["displacements"]["z"]
    displacement_y = reference_tag["displacements"]["y"]
    displacement_x = reference_tag["displacements"]["x"]
    
    assert displacement_d == pytest.approx(.539, rel=.01)
    assert displacement_z == pytest.approx(.529, rel=.01)
    assert displacement_x == pytest.approx(-.095, rel=.01)
    assert displacement_y == pytest.approx(-.0385, rel=.01)
    
    graph_util.plot_calculated_displacements_graph_info(image, dst, april_tag)
    
def test_calculate_displacement_02():
    src = IMG_DIR / "test_02.jpg"
    dst = IMG_DIR / "test_02_out.png"

    image = cv2.imread(str(src))
    
    assert image is not None, "Failed to read test image"
    
    april_tag_list = reference_util.scan_apriltags(image)
    april_tag = april_tag_list[0]
    april_tag["scale_units_m"]=.065
    reference_tag = reference_util.add_calculated_displacement_info_to_tag(
        camera_parameters=camera_parameters,
        reference_tag=april_tag
    )
    
    displacement_d = reference_tag["displacements"]["d"]
    displacement_z = reference_tag["displacements"]["z"]
    displacement_y = reference_tag["displacements"]["y"]
    displacement_x = reference_tag["displacements"]["x"]
    
    assert displacement_d == pytest.approx(.857, rel=.01)
    assert displacement_z == pytest.approx(.852, rel=.01)
    assert displacement_x == pytest.approx(.0695, rel=.01)
    assert displacement_y == pytest.approx(-.0683, rel=.01)
    
    graph_util.plot_calculated_displacements_graph_info(image, dst, april_tag)
    
def test_calculated_displacement_03():
    src = IMG_DIR / "test_03.jpg"
    dst = IMG_DIR / "test_03_out.png"

    image = cv2.imread(str(src))
    
    assert image is not None, "Failed to read test image"
    
    april_tag_list = reference_util.scan_apriltags(image)
    april_tag = april_tag_list[0]
    april_tag["scale_units_m"]=.065
    reference_tag = reference_util.add_calculated_displacement_info_to_tag(
        camera_parameters=camera_parameters,
        reference_tag=april_tag
    )
    
    displacement_d = reference_tag["displacements"]["d"]
    displacement_z = reference_tag["displacements"]["z"]
    displacement_y = reference_tag["displacements"]["y"]
    displacement_x = reference_tag["displacements"]["x"]
    
    assert displacement_d == pytest.approx(1.216, rel=.01)
    assert displacement_z == pytest.approx(1.210, rel=.01)
    assert displacement_x == pytest.approx(-0.0507, rel=.01)
    assert displacement_y == pytest.approx(-0.1142, rel=.01)
    
    graph_util.plot_calculated_displacements_graph_info(image, dst, april_tag)
    
