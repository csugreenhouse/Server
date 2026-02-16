import importlib
from pathlib import Path
import os
import pytest
import cv2
import warnings

ROOT = Path(__file__).resolve().parents[3] # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_height_request"

hr = importlib.import_module("plant_requests.height_request.height_request")
scanner_util = importlib.import_module("plant_requests.utils.reference_tag_util")
graph_util = importlib.import_module("plant_requests.utils.graph_util")
db = importlib.import_module("database.database_util")

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

def test_height_request_exists():
    assert hasattr(hr, "height_request"), "height_request() not found"  

def test_height_request_01():
    src = IMG_DIR / "test_height_request_00.jpg"
    dst = IMG_DIR / "test_height_request_00_out.png"
    image = cv2.imread(str(src))
    
    # Estimated heights should be around .34m for plant 1 and .26m for plant 2.

    color_bounds = plastic_color_bounds
    plant_bounds_1 = (.2, .5)
    plant_bounds_2 = (.5, .8)
    plant_id_1 = 1
    plant_id_2 = 2
    bias_1 = .01
    bias_2 = .01
    views_1 = [
        scanner_util.make_height_view(plant_id_1,plant_bounds_1,color_bounds,bias_1)
    ]
    views_2 = [
        scanner_util.make_height_view(plant_id_2,plant_bounds_2,color_bounds,bias_2)
    ]
    raw_tags = scanner_util.scan_raw_tags(image)
    raw_tag_1 = raw_tags[0]
    raw_tag_2 = raw_tags[1]
    reference_tag_1 = scanner_util.make_reference_tag(raw_tag_1,test_camera_parameters,scale=.07,views=views_1)
    reference_tag_2 = scanner_util.make_reference_tag(raw_tag_2,test_camera_parameters,scale=.07,views=views_2)
    
    reference_tags = [reference_tag_1, reference_tag_2]

    response = hr.height_request(image, reference_tags, test_camera_parameters)
    
    for view_response in response:
        if view_response["plant_id"] == plant_id_1:
            assert view_response["estimated_height"] == pytest.approx(.34, rel=.1)
        elif view_response["plant_id"] == plant_id_2:
            assert view_response["estimated_height"] == pytest.approx(.26, rel=.1)
            
    conn = db.open_connection_to_test_database()
    for view_response in response:
        db.insert_height_response_into_database(conn, view_response)
   
    
    assert  db.get_most_recent_height_for_plant_id(conn, 1)["height_units_m"] == pytest.approx(.34, rel=.1)
    assert  db.get_most_recent_height_for_plant_id(conn, 2)["height_units_m"] == pytest.approx(.26, rel=.1)
    db.close_connection_to_database(conn)
    
    

    assert response[0]["estimated_height"] == pytest.approx(.34, rel=.1)
    assert response[1]["estimated_height"] == pytest.approx(.26, rel=.1)

def test_height_request_02():
    src = IMG_DIR / "TEST02.jpg"
    dst = IMG_DIR / "TEST02_out.png"
    image = cv2.imread(str(src))
    
    # Estimated height should be around .007m for plant 5.
    # Plant 6 has a reading, but should be ingored.
    
    conn = db.open_connection_to_test_database()
    
    reference_tags = scanner_util.scan_reference_tags(image,test_camera_parameters, conn)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", Warning)
        response = hr.height_request(image, reference_tags, test_camera_parameters)

    graph_util.plot_height_request_response(image, dst, response)
    
    for view_response in response:
        db.insert_height_response_into_database(conn, view_response)
    assert  db.get_most_recent_height_for_plant_id(conn, 5)["height_units_m"] == pytest.approx(.007, rel=.1)
    
    db.close_connection_to_database(conn)
    
def test_height_request_03():
    src = IMG_DIR / "TEST03.jpg"
    dst = IMG_DIR / "TEST03_out.png"
    image = cv2.imread(str(src))
    
    # No plants in the image, but picking up some random colors.
    
    conn = db.open_connection_to_test_database()
    reference_tags = scanner_util.scan_reference_tags(image,test_camera_parameters, conn)
    db.close_connection_to_database(conn)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", Warning)
        response = hr.height_request(image, reference_tags, test_camera_parameters)

    graph_util.plot_height_request_response(image, dst, response)
    
def test_height_request_04():
    src = IMG_DIR / "TEST04.jpg"
    dst = IMG_DIR / "TEST04_out.png"
    image = cv2.imread(str(src))
    conn = db.open_connection_to_test_database()
    
    # no plants at all, Should be 0 cm for both.
    
    reference_tags = scanner_util.scan_reference_tags(image,test_camera_parameters, conn)
    
    response = None
    with pytest.raises(Warning, match="No plant detected in the image"):
        response = hr.height_request(image, reference_tags, test_camera_parameters)
        graph_util.plot_height_request_response(image, dst, response)
        for view_response in response:
            db.insert_height_response_into_database(conn, view_response)
        assert  db.get_most_recent_height_for_plant_id(conn, 5)["height_units_m"] == pytest.approx(0, rel=.1)
        assert  db.get_most_recent_height_for_plant_id(conn, 6)["height_units_m"] == pytest.approx(0, rel=.1)
    db.close_connection_to_database(conn)
            
        

def test_height_request_04_LARGE():
    src = IMG_DIR / "TEST04_LARGE.jpg"
    dst = IMG_DIR / "TEST04_LARGE_out.png"
    image = cv2.imread(str(src))
    
    # should be 8.75 cm for the plant 6, and 7.75 for plant 5.
    
    conn = db.open_connection_to_test_database()
    reference_tags = scanner_util.scan_reference_tags(image,test_camera_parameters, conn)
    db.close_connection_to_database(conn)

    response = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", Warning)
        response = hr.height_request(image, reference_tags, test_camera_parameters)

    graph_util.plot_height_request_response(image, dst, response)
import psycopg2