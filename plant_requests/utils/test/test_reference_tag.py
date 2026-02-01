import importlib
from pathlib import Path
import os
import pytest
from pytest import approx
import array
import cv2
import sys
# Make sure Python can import modules from the repo root no matter the CWD

sys.path.append('/srv/samba/Server')

test_camera_parameters = {
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.169.0.11"
}

ROOT = Path(__file__).resolve().parents[3]  # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_reference_tag"

database_util = importlib.import_module("database.database_util")
reference_util = importlib.import_module("plant_requests.utils.reference_tag_util")
graph_util = importlib.import_module("plant_requests.utils.graph_util")

def test_make_reference_tag_exists():
    assert hasattr(reference_util, "make_reference_tag"), "make_reference_tag() not found"

def test_make_reference_tag_01():
    
    src = IMG_DIR / "TEST01.jpg"
    dst = IMG_DIR / "TEST01_ref_out.png"
    image = cv2.imread(str(src))
    
    raw_tags = reference_util.scan_raw_tags(image)
    raw_tag = raw_tags[0]
    
    conn = database_util.open_connection_to_test_database()

    
    database_util.close_connection_to_database(conn)
    
    #make_reference_tag = reference_util.make_reference_tag(raw_tag, test_camera_parameters)
    
    
    
    
    
