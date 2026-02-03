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
    
def test_get_tag_views_from_database():
    conn = database_util.open_connection_to_test_database()
    try:
        tag_views = database_util.get_tag_views_from_database(conn, tag_id=4)
        assert len(tag_views) == 2, f"Expected 2 tag views, found {len(tag_views)}"
    finally:
        database_util.close_connection_to_database(conn)
    
    tag_view_one = tag_views[0]
    assert tag_view_one["plant_id"] == 1, f"Expected plant_id 1, found {tag_view_one['plant_id']}"
    assert tag_view_one["tag_id"] == 4, f"Expected tag_id 4, found {tag_view_one['tag_id']}"
    assert tag_view_one["view_type"] == "height", f"Expected view_type 'height', found {tag_view_one['view_type']}"
    assert tag_view_one["image_bound_upper"] == .5, f"Expected image_bound_upper 1.0, found {tag_view_one['image_bound_upper']}"
    assert tag_view_one["image_bound_lower"] == 0, f"Expected image_bound_lower 0.0, found {tag_view_one['image_bound_lower']}"
    assert "color_bound_lower" in tag_view_one, "color_bound_lower not found in tag view"
    assert "color_bound_upper" in tag_view_one, "color_bound_upper not found in tag view"
    
    tag_view_two = tag_views[1]
    assert tag_view_two["plant_id"] == 2, f"Expected plant_id 2, found {tag_view_two['plant_id']}"
    assert tag_view_two["tag_id"] == 4, f"Expected tag_id 4, found {tag_view_two['tag_id']}"
    assert tag_view_two["view_type"] == "height", f"Expected view_type 'height', found {tag_view_two['view_type']}"
    assert tag_view_two["image_bound_upper"] == 1.0, f"Expected image_bound_upper 1.0, found {tag_view_two['image_bound_upper']}"
    assert tag_view_two["image_bound_lower"] == 0.5, f"Expected image_bound_lower 0.0, found {tag_view_two['image_bound_lower']}"
    assert "color_bound_lower" in tag_view_two, "color_bound_lower not found in tag view"
    assert "color_bound_upper" in tag_view_two, "color_bound_upper not found in tag view"
    
def test_get_tag_scale_from_database():
    conn = database_util.open_connection_to_test_database()
    try:
        scale = database_util.get_tag_scale_from_database(conn, tag_id=4)
        assert scale == 0.07, f"Expected scale 0.07, found {scale}"
    finally:
        database_util.close_connection_to_database(conn)
    
