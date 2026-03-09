import importlib
from pathlib import Path
import os
import pytest
import cv2
import warnings

width_request = importlib.import_module("plant_requests.width_request.width_request")
scanner_util = importlib.import_module("plant_requests.utils.reference_tag_util")
graph_util = importlib.import_module("plant_requests.utils.graph_util")
database_util = importlib.import_module("database.database_util")

IMG_DIR = Path(__file__).parent / "images"
GRPH_DIR = Path(__file__).parent / "graphs"

test_connection = database_util.open_connection_to_test_database()
test_camera_parameters = database_util.get_available_camera_parameters_from_database(test_connection)[0]

def test_width_lettuce_1():
    src = IMG_DIR / "lettuce"
    grph = GRPH_DIR / "lettuce"

    image_name = "lettuce_1"
    image = cv2.imread(str(src / f"{image_name}.jpg"))
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    width_response = width_request.width_request(image, reference_tags, test_camera_parameters)
    graph_util.plot_widths_request_response(image,str(grph / f"{image_name}_out.png"),width_response)
    
    assert width_response[0]["estimated_width"] == pytest.approx(0.036, abs=0.01)
    #assert width_response[1]["estimated_width"] == pytest.approx(0.020, abs=0.01)
    
def test_width_lettuce_2():
    src = IMG_DIR / "lettuce"
    grph = Path(__file__).parent / "graphs" / "lettuce"

    image_name = "lettuce_2"
    image = cv2.imread(str(src / f"{image_name}.jpg"))
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    width_response = width_request.width_request(image, reference_tags, test_camera_parameters)
    graph_util.plot_widths_request_response(image,str(grph / f"{image_name}_out.png"),width_response)
    
    assert width_response[0]["estimated_width"] == pytest.approx(0.108, abs=0.01)
    assert width_response[1]["estimated_width"] == pytest.approx(0.0374, abs=0.01)
    
def test_width_lettuce_3():
    src = IMG_DIR / "lettuce"
    grph = Path(__file__).parent / "graphs" / "lettuce"

    image_name = "lettuce_3"
    image = cv2.imread(str(src / f"{image_name}.jpg"))
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    width_response = width_request.width_request(image, reference_tags, test_camera_parameters)
    graph_util.plot_widths_request_response(image,str(grph / f"{image_name}_out.png"),width_response)
    
    assert width_response[0]["estimated_width"] == pytest.approx(0.108, abs=0.01)
    assert width_response[1]["estimated_width"] == pytest.approx(0.0374, abs=0.01)
    
def test_width_lettuce_4():
    src = IMG_DIR / "lettuce"
    grph = Path(__file__).parent / "graphs" / "lettuce"

    image_name = "lettuce_4"
    image = cv2.imread(str(src / f"{image_name}.jpg"))
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    width_response = width_request.width_request(image, reference_tags, test_camera_parameters)
    graph_util.plot_widths_request_response(image,str(grph / f"{image_name}_out.png"),width_response)
    
    assert width_response[0]["estimated_width"] == pytest.approx(0.089, abs=0.01)
    assert width_response[1]["estimated_width"] == pytest.approx(0.0441, abs=0.01)
    
def test_width_lettuce_5():
    src = IMG_DIR / "lettuce"
    grph = Path(__file__).parent / "graphs" / "lettuce"

    image_name = "lettuce_5"
    image = cv2.imread(str(src / f"{image_name}.jpg"))
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    width_response = width_request.width_request(image, reference_tags, test_camera_parameters)
    graph_util.plot_widths_request_response(image,str(grph / f"{image_name}_out.png"),width_response)
    
    assert width_response[0]["estimated_width"] == pytest.approx(0.141, abs=0.01)
    #assert width_response[1]["estimated_width"] == pytest.approx(0.0513, abs=0.01)
    
def test_width_lettuce_6():
    src = IMG_DIR / "lettuce"
    grph = Path(__file__).parent / "graphs" / "lettuce"

    image_name = "lettuce_6"
    image = cv2.imread(str(src / f"{image_name}.jpg"))
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    width_response = width_request.width_request(image, reference_tags, test_camera_parameters)
    graph_util.plot_widths_request_response(image,str(grph / f"{image_name}_out.png"),width_response)
    
    assert width_response[0]["estimated_width"] == pytest.approx(0.146, abs=0.01)
    #assert width_response[1]["estimated_width"] == pytest.approx(0.0438, abs=0.01)
