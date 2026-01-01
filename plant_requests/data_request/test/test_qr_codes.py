import importlib
from pathlib import Path
import os
import pytest
from pytest import approx
import cv2
import array

# Make sure Python can import "Server.processing.height" no matter the CWD
ROOT = Path(__file__).resolve().parents[2]  # repo root (contains "Server")
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_qr_codes"

mod = importlib.import_module("plant_requests.data_request.data_request")
graph = importlib.import_module("plant_requests.utils.graph_util")

def test_methods_existence():
    assert hasattr(mod, "scan_qrtags"), "scan_qrtags() not found"
    assert hasattr(graph, "plot_image_tag_detection"), "plot_image_tag_detection() not found"


def test_qrtag_test01(tmp_path=" "):
    src = IMG_DIR / "TEST01.jpg"
    dst = IMG_DIR / "TEST01_out.png"
    
    image = cv2.imread(str(src))
    qr_list = mod.scan_qrtags(image)
    qr = qr_list[0]

    qr["data"] == 'Test01-C1v'
    assert "corners" in qr, "scan_qrtags() returned no 'corners'"
    corners = qr["corners"]
    assert(type(corners)==dict)
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"] 
    assert tl == approx((271.00156, 71.95007),rel=1e-3,abs=0.5)
    assert tr == approx((399.1945, 78.359726),rel=1e-3,abs=0.5)
    assert br == approx((394.64542, 206.09476),rel=1e-3,abs=0.5)
    assert bl == approx((266.99057, 200.30188),rel=1e-3,abs=0.5)
    
def test_qrtag_test02(tmp_path=" "):
    src = IMG_DIR / "TEST02.jpg"
    dst = IMG_DIR / "TEST02_out.png"
    
    image = cv2.imread(str(src))
    qr_list = mod.scan_qrtags(image)
    qr = qr_list[0]
    
    assert "corners" in qr, "scan_qrtags() returned no 'corners'"
    corners = qr["corners"]
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"] 
    
    assert tl == approx((561.30676, 151.89005),rel=1e-3,abs=0.5)   
    assert tr == approx((640.5522, 157.03586),rel=1e-3,abs=0.5)
    assert br == approx((637.168, 235.34978),rel=1e-3,abs=0.5)
    assert bl == approx((559.5875, 230.97421),rel=  1e-3,abs=0.5)
    
def test_qrtag_toFarAway_TEST03(tmp_path=" "):
    src = IMG_DIR / "TEST03.jpg"
    dst = IMG_DIR / "TEST03_out.png"
    
    image = cv2.imread(str(src))
    
    # assert that scan_qrtags raises a ValueError
    with pytest.raises(ValueError):
        qr_list = mod.scan_qrtags(image)
        
def test_qrtag_testNone(tmp_path=" "):
    src = IMG_DIR / "TESTNONE.jpg"
    dst = IMG_DIR / "TESTNONE_out.png"
    image = cv2.imread(str(src))
    
    with pytest.raises(ValueError):
        qr_list = mod.scan_qrtags(image)
        
def test_qrtag_CHUCK_TEST(tmp_path=" "):
    src = IMG_DIR / "CHUCK_TEST.jpg"
    dst = IMG_DIR / "CHUCK_TEST_out.png"
    image = cv2.imread(str(src))

    qr_list = mod.scan_qrtags(image)
    qr = qr_list[0]

    assert qr["data"]=='Test01-C1v'

    