import importlib
from pathlib import Path
import os
import pytest
import cv2

# Make sure Python can import modules from the repo root no matter the CWD
ROOT = Path(__file__).resolve().parents[3] # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_estimate_height"

hr = importlib.import_module("plant_requests.height_request.height_request")
graph_util = importlib.import_module("plant_requests.utils.graph_util")
reference_util = importlib.import_module("plant_requests.utils.reference_tag_util")

plastic_color_bounds = ((30, 60, 30),(90, 255, 200))
lettuce_color_bounds = ((30, 35, 30),(75, 255, 255))

test_scale = .07

test_camera_parameters = {
    "camera_id": 1,
    "width": 1024,
    "height": 768,
    "focal_length_mm": 3.6,
    "sensor_height_mm": 2.2684,
    "sensor_width_mm": 3.590,
    "ip_address": "192.168.0.11"
    }

def test_methods_existence():
    assert hasattr(hr, "estimate_heights_reference_tags"), "estimate_heights_reference_tags() not found"
    assert hasattr(hr, "estimate_heights_reference_tag"), "estimate_heights_reference_tag() not found"
    assert hasattr(reference_util, "scan_apriltags"), "scan_apriltags() not found"
    #assert hasattr(graph_util, "plot_estimate_height_graph_info"), "plot_estimate_height_graph_info() not found"

def test_estimate_height_6CM():
    src = IMG_DIR / "test_6cm.jpg"
    dst = IMG_DIR / "test_6cm_out.png"
    image = cv2.imread(str(src))
    color_bounds = plastic_color_bounds
    plant_bounds = (.35, .6)
    plant_id = 1
    bias = .01
    
    
    views = [reference_util.make_height_view(plant_id,plant_bounds,color_bounds,bias)]
    raw_april_tag = reference_util.scan_raw_tags(image)[0]
    reference_tag = reference_util.make_reference_tag(raw_april_tag,test_camera_parameters,scale=test_scale,views=views)
    estimated_height_response =  hr.estimate_heights_reference_tags(image, [reference_tag])
    
    graph_util.plot_estimated_heights_response(image,dst,estimated_height_response)
    
    estimated_height = estimated_height_response[0]["estimated_height"]
    assert estimated_height == pytest.approx(.06, rel=.20)
   

def test_estimate_height_10CM():
    src = IMG_DIR / "test_10cm.jpg"
    dst = IMG_DIR / "test_10cm_out.png"
    
    image = cv2.imread(str(src))
    color_bounds = plastic_color_bounds
    plant_bounds = (.35, .6)
    plant_id = 1
    bias = .01
    
    views = [reference_util.make_height_view(plant_id,plant_bounds,color_bounds,bias)]
    raw_april_tag = reference_util.scan_raw_tags(image)[0]
    reference_tag = reference_util.make_reference_tag(raw_april_tag,test_camera_parameters,scale=test_scale,views=views)
    estimated_height_response =  hr.estimate_heights_reference_tags(image, [reference_tag])
    
    graph_util.plot_estimated_heights_response(image,dst,estimated_height_response)
    
    estimated_height = estimated_height_response[0]["estimated_height"]
    
    assert estimated_height == pytest.approx(.10, rel=.20)

def test_estimate_height_16CM():
    src = IMG_DIR / "test_16cm.jpg"
    dst = IMG_DIR / "test_16cm_out.png"
    image = cv2.imread(str(src))

    color_bounds = plastic_color_bounds
    plant_bounds = (.35, .6)
    plant_id = 1
    bias = .01
    
    views = [reference_util.make_height_view(plant_id,plant_bounds,color_bounds,bias)]
    raw_april_tag = reference_util.scan_raw_tags(image)[0]
    reference_tag = reference_util.make_reference_tag(raw_april_tag,test_camera_parameters,scale=test_scale,views=views)
    estimated_height_response =  hr.estimate_heights_reference_tags(image, [reference_tag])
    
    graph_util.plot_estimated_heights_response(image,dst,estimated_height_response)
    
    estimated_height = estimated_height_response[0]["estimated_height"]
    

    assert estimated_height == pytest.approx(.16, rel=.20)
    

def test_estimate_multiple_heights():
    src = IMG_DIR / "test_multiple.jpg"
    dst = IMG_DIR / "test_multiple_out.png"
    image = cv2.imread(str(src))
    
    view_one = reference_util.make_height_view(
        plant_id=1,
        image_bounds =(.05,.45),
        color_bounds = plastic_color_bounds,
        bias_units_m = 0,
    )
    
    view_two = reference_util.make_height_view(
        plant_id=2,
        image_bounds =(0.50,.95),
        color_bounds = plastic_color_bounds,
        bias_units_m = 0,
    )
    
    views = [view_one, view_two]
    
    raw_april_tag = reference_util.scan_raw_tags(image)[0]
    reference_tag = reference_util.make_reference_tag(raw_april_tag,test_camera_parameters,scale=test_scale,views=views)
    estimated_heights_response =  hr.estimate_heights_reference_tags(image, [reference_tag])
    
    graph_util.plot_estimated_heights_response(image, dst, estimated_heights_response)
    
    
    



    

    