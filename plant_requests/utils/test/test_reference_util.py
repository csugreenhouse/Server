import importlib
from pathlib import Path
import os
import pytest
from pytest import approx
import apriltag
import array
import cv2
# Make sure Python can import modules from the repo root no matter the CWD
ROOT = Path(__file__).resolve().parents[3]  # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_april_codes"

reference_util = importlib.import_module("plant_requests.utils.reference_tag_util")
#graph_util = importlib.import_module("plant_requests.utils.graph_util")


test_camera_parameters = {
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.168.0.11"
    }

def test_methods_existence():
    assert hasattr(reference_util, "scan_apriltags"), "scan_apriltags() not found"
    #assert hasattr(graph_util, "plot_image_tag_detection"), "plot_image_tag_detection() not found"

def test_apritag_test01():
    src = IMG_DIR / "TEST01.jpg"
    dst = IMG_DIR / "TEST01_out.png"
    image = cv2.imread(str(src))
    tag_info = reference_util.scan_apriltags(image)[0]

    tag_info["data"] == 1
    assert "corners" in tag_info, "scan_apriltags() returned no 'corners'"
    corners = tag_info["corners"]
    assert(type(corners)==dict)
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"] 
    assert tl == approx((267.1820373534919, 244.1751403808336),rel=1e-3,abs=0.5)
    assert tr == approx((393.2828063964598, 250.85649108888924),rel=1e-3,abs=0.5)
    assert br == approx((387.81927490236626, 374.93643188478995),rel=1e-3,abs=0.5)
    assert bl == approx((262.30166625978956, 369.2857971191188),rel=1e-3,abs=0.5)
    
def test_apritag_test02():
    src = IMG_DIR / "TEST02.jpg"
    dst = IMG_DIR / "TEST02_out.png"
    
    image = cv2.imread(str(src))
    tag_info = reference_util.scan_apriltags(image)[0]

    assert "corners" in tag_info, "scan_apriltags() returned no 'corners'"
    corners = tag_info["corners"]
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"] 
    
    assert tl == approx((558.5017700195309, 260.1452331542965),rel=1e-3,abs=0.5)   
    assert tr == approx((636.921752929687, 263.3018188476566),rel=1e-3,abs=0.5)
    assert br == approx((632.7066650390628, 341.7890319824224),rel=1e-3,abs=0.5)
    assert bl == approx((554.6207275390632, 338.9519042968744),rel=1e-3,abs=0.5)

def test_apritag_test03():
    src = IMG_DIR / "TEST03.jpg"
    dst = IMG_DIR / "TEST03_out.png"
    
    image = cv2.imread(str(src))
    tag_info = reference_util.scan_apriltags(image)[0]

    assert "corners" in tag_info, "scan_apriltags() returned no 'corners'"
    corners = tag_info["corners"]
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"] 
    
    assert tl == approx((442.08078002929653, 258.8964538574215),rel=1e-3,abs=0.5)
    assert tr == approx((497.32519531249955, 260.3209533691411),rel=1e-3,abs=0.5)
    assert br == approx((495.6865844726565, 315.3803405761721),rel=1e-3,abs=0.5)
    assert bl == approx((440.6880798339846, 313.9172973632811), rel=1e-3,abs=0.5)

def test_apritag_testNONE():
    src = IMG_DIR / "TESTNONE.jpg"
    image = cv2.imread(str(src))
    
    with pytest.raises(ValueError) as excinfo:
        tag_info = reference_util.scan_apriltags(image)
    
    assert "No april tags at all have been found" in str(excinfo.value)