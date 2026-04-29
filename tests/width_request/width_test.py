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

IMG_DIR = Path(__file__).parent.parent / "images"
GRPH_DIR = Path(__file__).parent / "graphs"

test_connection = database_util.open_connection_to_test_database()
test_camera_parameters = database_util.get_available_camera_parameters_from_database(test_connection)[0]

def test_width_lettuce_1():
    template("lettuce", "lettuce_1", 0.036, None)
    
def test_width_lettuce_2():
    template("lettuce", "lettuce_2", 0.10361, 0.0373)
    
def test_width_lettuce_3():
    template("lettuce", "lettuce_3", 0.108, 0.0374
             )
def test_width_lettuce_4():
    template("lettuce", "lettuce_4", 0.0878, 0.0438)
    
def test_width_lettuce_5():
    template("lettuce", "lettuce_5", 0.141, 0.041)
    
def test_width_lettuce_6():
    template("lettuce", "lettuce_6", 0.146, 0.0438)


def template(type, image_name, expected_height_plant_1, expected_height_plant_2):
    src = IMG_DIR / type
    grph = GRPH_DIR / type

    image = cv2.imread(str(src / f"{image_name}.jpg"))
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    width_response = width_request.width_request(image, reference_tags)
    graph_util.plot_widths_request_response(image,str(grph / f"{image_name}_out.png"),width_response)
    
    if expected_height_plant_1 is not None:
        assert width_response[0]["estimated_width"] == pytest.approx(expected_height_plant_1, abs=0.01), f"Estimated width for plant 1 in image {image_name} is {width_response[0]['estimated_width']} , but expected {expected_height_plant_1}"
    if expected_height_plant_2 is not None:
        assert width_response[1]["estimated_width"] == pytest.approx(expected_height_plant_2, abs=0.01), f"Estimated width for plant 2 in image {image_name} is {width_response[1]['estimated_width']} , but expected {expected_height_plant_2}"
