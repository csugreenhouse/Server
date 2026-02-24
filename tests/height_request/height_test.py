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


def test_height_request_lettuce():
    src = IMG_DIR / "lettuce"
    grph = GRPH_DIR / "lettuce"

    image_names = ["lettuce_1", "lettuce_2", "lettuce_3", "lettuce_4", "lettuce_5", "lettuce_6", "lettuce_7", "lettuce_8", "lettuce_9"]

    estimated_heights_plant_5 = [0.0038, 0.031, 0.041, 0.053, 0.092, 0.089, 0.149, 0.165, 0.179]
    estimated_heights_plant_6 = [0.012, 0.024, 0.027, 0.039, 0.069, 0.081,  0.120, 0.125, 0.132]

    # set the color bounds for the lettuce
    database_util.set_color_bounds_for_species_in_database(test_connection, 2, ((28, 50, 50), (95, 255, 180))) #lettuce

    for image_name in image_names:
        image = cv2.imread(str(src / f"{image_name}.jpg"))
        reference_tags = scanner_util.scan_reference_tags(image, test_camera_parameters, test_connection)
        height_response = height_request.height_request(image, reference_tags, test_camera_parameters)
        graph_util.plot_height_request_response(image,str(grph / f"{image_name}_out.png"),height_response)
        assert height_response[0]["estimated_height"] == pytest.approx(estimated_heights_plant_5[image_names.index(image_name)], abs=0.5)
        assert height_response[1]["estimated_height"] == pytest.approx(estimated_heights_plant_6[image_names.index(image_name)], abs=0.5)
