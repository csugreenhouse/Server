import importlib
from pathlib import Path
import os
import pytest
import cv2
import warnings

height_request = importlib.import_module("plant_requests.height_request.height_request")
scanner_util = importlib.import_module("plant_requests.utils.reference_tag_util")
graph_util = importlib.import_module("plant_requests.utils.graph_util")
database_util = importlib.import_module("database.database_util")

IMG_DIR = Path(__file__).parent / "images"
GRPH_DIR = Path(__file__).parent / "graphs"


test_connection = database_util.open_connection_to_test_database()
test_camera_parameters = database_util.get_available_camera_parameters_from_database(test_connection)[0]

#database_util.set_color_bounds_for_species_in_database(conn, 2, ((28, 30, 25), (95, 255, 180))) #lettuce
#database_util.set_color_bounds_for_species_in_database(conn, 3, ((30, 35, 30), (95, 255, 180))) #basil
#database_util.set_color_bounds_for_species_in_database(conn, 1, ((30, 100, 100),(85, 240, 255))) #mint

# HUE - what colors, green is around 60, red is around 0 or 180, blue is around 120
# SATURATION - how much color vs white, 0 is white, 255 is fully colored
# VALUE - how much color vs black, 0 is black, 255 is fully bright

def  test_lettuce_1():
    template("lettuce", "lettuce_1", 0.0038, -0.042)

def test_lettuce_2():
    template("lettuce", "lettuce_2", 0.031, 0.024)
    
def test_lettuce_3():
    template("lettuce", "lettuce_3", 0.041, 0.027)
    
def test_lettuce_4():
    template("lettuce", "lettuce_4", 0.053, 0.039)
    
def test_lettuce_5():
    template("lettuce", "lettuce_5", 0.092, 0.069)
    
def test_lettuce_6():
    template("lettuce", "lettuce_6", 0.089, 0.081)

def test_lettuce_7():
    template("lettuce", "lettuce_7", 0.14, 0.12)

def test_lettuce_8():
    template("lettuce", "lettuce_8", 0.165, 0.125)
    
def test_lettuce_9():
    template("lettuce", "lettuce_9", 0.18, None)
    
#HUE - what colors, green is around 60, red is around 0 or 180, blue is around 120
#SATURATION - how much color vs white, 0 is white, 255 is fully colored
#VALUE - how much color vs black, 0 is black, 255 is fully bright   
def test_basil_1():
    database_util.set_color_bounds_for_species_in_database(test_connection, 3, ((20, 90, 60), (100, 255, 180))) #basil
    pass
    template("basil", "basil_1", None, None)

def test_basil_2():
    pass
    template("basil", "basil_2", None, None)
    
def test_basil_3():
    pass
    template("basil", "basil_3", None, None)
    
def test_basil_4():
    pass 
    template("basil", "basil_4", None, None)
    
def test_basil_5():
    pass
    template("basil", "basil_5", None, None)
    
def test_basil_6():
    pass
    template("basil", "basil_6", None, None)
    
def test_basil_7():
    pass
    template("basil", "basil_7", None, None)
    
def test_basil_8():
    pass
    template("basil", "basil_8", None, None)
    
def test_basil_9():
    pass
    template("basil", "basil_9", None, None)



def template(type, image_name, expected_height_plant_1, expected_height_plant_2):
    src = IMG_DIR / type
    grph = GRPH_DIR / type

    image = cv2.imread(str(src / f"{image_name}.jpg"))
    reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
    height_response = height_request.height_request(image, reference_tags)
    graph_util.plot_height_request_response(image,str(grph / f"{image_name}_out.png"),height_response)
    
    if expected_height_plant_1 is not None:
        assert height_response[0]["estimated_height"] == pytest.approx(expected_height_plant_1, abs=0.01), f"Estimated height for plant 1 in image {image_name} is {height_response[0]['estimated_height']} , but expected {expected_height_plant_1}"
    if expected_height_plant_2 is not None:
        assert height_response[1]["estimated_height"] == pytest.approx(expected_height_plant_2, abs=0.01), f"Estimated height for plant 2 in image {image_name} is {height_response[1]['estimated_height']} , but expected {expected_height_plant_2}"
    