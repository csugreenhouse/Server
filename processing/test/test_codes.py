# Server/processing/test/test_estimated_height.py
import importlib
from pathlib import Path
import os
import pytest
from pytest import approx
import apriltag
import array
# Make sure Python can import "Server.processing.height" no matter the CWD
ROOT = Path(__file__).resolve().parents[2]  # repo root (contains "Server")
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_codes"

def test_apritag_test01(tmp_path=" "):
    src = IMG_DIR / "TEST01.jpg"
    dst = IMG_DIR / "TEST01_out.png"
    
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "scan_apriltag"), "scan_apriltag() not found"
    
    #mod.plot_image(str(src), str(dst))
    tag_info = mod.scan_apriltag(str(src))
    
    tag_info["tag_id"] == 1
    assert "corners" in tag_info, "scan_apriltag() returned no 'corners'"
    corners = tag_info["corners"]
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"] 
    assert tl == approx((267.1820373534919, 244.1751403808336),rel=1e-3,abs=0.5)
    assert tr == approx((393.2828063964598, 250.85649108888924),rel=1e-3,abs=0.5)
    assert br == approx((387.81927490236626, 374.93643188478995),rel=1e-3,abs=0.5)
    assert bl == approx((262.30166625978956, 369.2857971191188),rel=1e-3,abs=0.5)
    
def test_apritag_test02(tmp_path=" "):
    src = IMG_DIR / "TEST02.jpg"
    dst = IMG_DIR / "TEST02_out.png"
    
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "scan_apriltag"), "scan_apriltag() not found"
    assert hasattr(mod, "plot_image"), "plot_image() not found"
    
    #mod.plot_image(src, dst)
    tag_info = mod.scan_apriltag(str(src))
    
    assert "corners" in tag_info, "scan_apriltag() returned no 'corners'"
    corners = tag_info["corners"]
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"] 
    
    assert tl == approx((558.5017700195309, 260.1452331542965),rel=1e-3,abs=0.5)   
    assert tr == approx((636.921752929687, 263.3018188476566),rel=1e-3,abs=0.5)
    assert br == approx((632.7066650390628, 341.7890319824224),rel=1e-3,abs=0.5)
    assert bl == approx((554.6207275390632, 338.9519042968744),rel=1e-3,abs=0.5)

def test_apritag_test03(tmp_path=" "):
    src = IMG_DIR / "TEST03.jpg"
    dst = IMG_DIR / "TEST03_out.png"
    
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "scan_apriltag"), "scan_apriltag() not found"
    assert hasattr(mod, "plot_image"), "plot_image() not found"
    
    #mod.plot_image(src, dst)
    tag_info = mod.scan_apriltag(str(src))
    
    assert "corners" in tag_info, "scan_apriltag() returned no 'corners'"
    corners = tag_info["corners"]
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"] 
    
    assert tl == approx((442.08078002929653, 258.8964538574215),rel=1e-3,abs=0.5)
    assert tr == approx((497.32519531249955, 260.3209533691411),rel=1e-3,abs=0.5)
    assert br == approx((495.6865844726565, 315.3803405761721),rel=1e-3,abs=0.5)
    assert bl == approx((440.6880798339846, 313.9172973632811), rel=1e-3,abs=0.5)
    
def test_apritag_testNONE(tmp_path=" "):
    src = IMG_DIR / "TESTNONE.jpg"
    
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "scan_apriltag"), "scan_apriltag() not found"
    
    with pytest.raises(ValueError) as excinfo:
        tag_info = mod.scan_apriltag(str(src))
    
    assert "No april tags at all have been found" in str(excinfo.value)