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
IMG_DIR = BASE_DIR / "images" / "test_estimate_height" #using same images to prove output

hr = importlib.import_module("plant_requests.width_request.width_request")
graph_util = importlib.import_module("plant_requests.utils.graph_util")
reference_util = importlib.import_module("plant_requests.utils.reference_tag_util")

plastic_color_bounds = ((31, 50, 50), (75, 255, 200)) #I had to change this to get proper blob for test
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
    assert hasattr(hr, "estimate_widths_reference_tags"), "estimate_widths_reference_tags() not found"
    assert hasattr(hr, "estimate_widths_reference_tag"), "estimate_widths_reference_tag() not found"
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

    # make width view
    
    views = [reference_util.make_height_view(plant_id,plant_bounds,color_bounds,bias)]
    raw_april_tag = reference_util.scan_raw_tags(image)[0]
    reference_tag = reference_util.make_reference_tag(raw_april_tag,test_camera_parameters,scale=test_scale,views=views)
    estimated_width_response =  hr.estimate_widths_reference_tags(image, [reference_tag])
    
    graph_util.plot_estimated_widths_response(image,dst,estimated_width_response)
    
    estimated_width = estimated_width_response[0]["estimated_width"]
    assert estimated_width == pytest.approx(.025, rel=.10)


    #######################
    # SECOND TEST
    #######################

def test_calibration_sheet_multi_plant():
    src = IMG_DIR / "calibrationsheet.jpg"
    dst = IMG_DIR / "calibration_output.png"
    image = cv2.imread(str(src))
    
    color_bounds = plastic_color_bounds 
    
    # Manually defining the views for the 3 plants
    manual_views = [
        {
            "plant_id": 1, # 2cm
            "image_bound_lower": 0.30, 
            "image_bound_upper": 0.45,
            "color_bound_lower": color_bounds[0],
            "color_bound_upper": color_bounds[1]
        },
        {
            "plant_id": 2, #  4cm 
            "image_bound_lower": 0.45,
            "image_bound_upper": 0.65,
            "color_bound_lower": color_bounds[0],
            "color_bound_upper": color_bounds[1]
        },
        {
            "plant_id": 3, #  8cm 
            "image_bound_lower": 0.65,
            "image_bound_upper": 1.0,
            "color_bound_lower": color_bounds[0],
            "color_bound_upper": color_bounds[1]
        }
    ]

    raw_april_tags = reference_util.scan_raw_tags(image)[0]

    reference_tag = reference_util.make_reference_tag(
        raw_april_tags, 
        test_camera_parameters, 
        scale=test_scale, 
        views=manual_views
    )
    
    estimated_width_response = hr.estimate_widths_reference_tags(image, [reference_tag])
    
    # Output the visualization
    graph_util.plot_estimated_widths_response(image, dst, estimated_width_response)
    
    # 2cm plant
    assert estimated_width_response[0]["estimated_width"] == pytest.approx(0.02, abs=0.005)
    # 4cm plant
    assert estimated_width_response[1]["estimated_width"] == pytest.approx(0.04, abs=0.005)
    # 8cm plant
    assert estimated_width_response[2]["estimated_width"] == pytest.approx(0.08, abs=0.005)