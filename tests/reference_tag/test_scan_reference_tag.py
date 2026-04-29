import importlib
from pathlib import Path
import os
import pytest
import cv2
import warnings
import sys

# ImportError while importing test module '/home/tyler/projects/Server/tests/height_request/height_test.py'.
# Hint: make sure your test modules/packages have valid Python names.
# Traceback:

sys.path.append('/srv/samba/Server')

height_request = importlib.import_module("plant_requests.height_request.height_request")
scanner_util = importlib.import_module("plant_requests.utils.reference_tag_util")
graph_util = importlib.import_module("plant_requests.utils.graph_util")
database_util = importlib.import_module("database.database_util")

IMG_DIR = Path(__file__).parent.parent / "images" / "apriltags"
GRPH_DIR = Path(__file__).parent / "graphs"


test_connection = database_util.open_connection_to_test_database()
test_camera_parameters = database_util.get_available_camera_parameters_from_database(test_connection)[0]


def test_scan_reference_tags_no_tags():
    src = IMG_DIR / "testnull.jpg"
    
    image = cv2.imread(str(src))
    
    with pytest.raises(ValueError) as excinfo:
        tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    
    assert "No reference tags at all have been found" in str(excinfo.value)
    
def test_scan_reference_tags_tag_1():
    src = IMG_DIR / "tag1.png"
    
    image = cv2.imread(str(src))
    
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    
    reference_tag = reference_tags[0]
    
    assert reference_tag["data"] == 1
    assert reference_tag["scale_units_m"] == .07
    assert len(reference_tag["views"]) > 0
    assert "corners" in reference_tag
    
    veiw_1 = reference_tag["views"][0]
    
    assert "image_bound_x_low" in veiw_1
    assert "image_bound_x_high" in veiw_1
    assert "image_bound_y_low" in veiw_1
    assert "image_bound_y_high" in veiw_1
    assert "color_bound_upper" in veiw_1
    assert "color_bound_lower" in veiw_1
    assert "plant_id" in veiw_1

def test_scan_reference_tags_tag_2():
    src = IMG_DIR / "tag2.png"
    
    image = cv2.imread(str(src))
    
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    
    reference_tag = reference_tags[0]
    
    assert reference_tag["data"] == 2
    assert reference_tag["scale_units_m"] == .07
    assert len(reference_tag["views"]) > 0
    assert "corners" in reference_tag
    
    veiw_1 = reference_tag["views"][0]
    
    assert "image_bound_x_low" in veiw_1
    assert "image_bound_x_high" in veiw_1
    assert "image_bound_y_low" in veiw_1
    assert "image_bound_y_high" in veiw_1
    assert "color_bound_upper" in veiw_1
    assert "color_bound_lower" in veiw_1
    assert "plant_id" in veiw_1
    
def test_scan_reference_tags_tag_3():
    src = IMG_DIR / "tag3.png"
    
    image = cv2.imread(str(src))
    
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    
    reference_tag = reference_tags[0]
    
    assert reference_tag["data"] == 3
    assert reference_tag["scale_units_m"] == .07
    assert len(reference_tag["views"]) > 0
    assert "corners" in reference_tag
    
    veiw_1 = reference_tag["views"][0]
    
    assert "image_bound_x_low" in veiw_1
    assert "image_bound_x_high" in veiw_1
    assert "image_bound_y_low" in veiw_1
    assert "image_bound_y_high" in veiw_1
    assert "color_bound_upper" in veiw_1
    assert "color_bound_lower" in veiw_1
    assert "plant_id" in veiw_1

def test_scan_reference_tags_tag_4():
    src = IMG_DIR / "tag4.png"
    
    image = cv2.imread(str(src))
    
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    
    reference_tag = reference_tags[0]
    
    assert reference_tag["data"] == 4
    assert reference_tag["scale_units_m"] == .07
    assert len(reference_tag["views"]) > 0
    assert "corners" in reference_tag
    
    veiw_1 = reference_tag["views"][0]
    
    assert "image_bound_x_low" in veiw_1
    assert "image_bound_x_high" in veiw_1
    assert "image_bound_y_low" in veiw_1
    assert "image_bound_y_high" in veiw_1
    assert "color_bound_upper" in veiw_1
    assert "color_bound_lower" in veiw_1
    assert "plant_id" in veiw_1



    