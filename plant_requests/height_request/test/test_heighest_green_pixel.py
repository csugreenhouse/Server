import cv2
import numpy as np
import pytest
import os
from pathlib import Path
import importlib



ROOT = Path(__file__).resolve().parents[3] # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_heighest_green_pixel"

height_request = importlib.import_module("plant_requests.height_request.height_request")
reference_util = importlib.import_module("plant_requests.utils.reference_tag_util")
graph_util = importlib.import_module("plant_requests.utils.graph_util")

plastic_color_bounds = ((30, 60, 30),(70, 255, 200))
lettuce_color_bounds = ((30, 35, 30),(75, 255, 255))

def test_methods_existence():
    assert hasattr(height_request, "get_heighest_green_pixel"), "get_heighest_green_pixel() not found"
    assert hasattr(graph_util, "plot_heighest_green_pixel_graph_info"), "plot_heighest_green_pixel_graph_info() not found"
    
def test_heighest_green_pixel_lettuce():
    src = IMG_DIR / "test_plastic_6.jpg"
    dst = IMG_DIR / "test_plastic_6_out.png"

    image = cv2.imread(str(src))
    
    assert image is not None, "Failed to read test image"
    
    response = height_request.get_heighest_green_pixel(
        image,
        lettuce_color_bounds,
        plant_bounds=(.3, .7)
    )
    
    graph_util.plot_heighest_green_pixel_response(image, dst, response)

    heighest_pixel = response["heighest_green_pixel"]
    
    assert heighest_pixel[1] == pytest.approx(500, rel=.1)


def test_heighest_green_pixel_plastic():
    src = IMG_DIR / "test_plastic_16.jpg"
    dst = IMG_DIR / "test_plastic_16_out.png"

    image = cv2.imread(str(src))
    
    assert image is not None, "Failed to read test image"
    
    response = height_request.get_heighest_green_pixel(
        image,
        plastic_color_bounds,
        plant_bounds=(.3, .7)
    )
    
    graph_util.plot_heighest_green_pixel_response(image, dst, response)
    
    heighest_pixel = response["heighest_green_pixel"]
    
    assert heighest_pixel[1] == pytest.approx(258, rel=.1)
    
def test_heighest_green_pixel_no_plant():
    src = IMG_DIR / "test_no_plant.jpg"

    image = cv2.imread(str(src))
    
    assert image is not None, "Failed to read test image"
    
    # replace with warning
    
    with pytest.warns(UserWarning, match="No plant detected in the image"):
        graph_info = height_request.get_heighest_green_pixel(
            image,
            plastic_color_bounds,
            plant_bounds=(.3, .7)
        )