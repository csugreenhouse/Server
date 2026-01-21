import cv2
import os
import importlib
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[3]  # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

database_util = importlib.import_module("plant_requests.utils.database_util") 
reference_util = importlib.import_module("plant_requests.utils.reference_tag_util")
image_util = importlib.import_module("plant_requests.utils.image_util")

camera_database = [
 {'camera_id': 1, 'width': 1024, 'height': 768, 'focal_length_mm': ('3.6'), 'sensor_height_mm': ('2.2684'), 'sensor_width_mm': ('3.590'), 'ip_address': '192.168.0.11'}, 
 {'camera_id': 2, 'width': 1024, 'height': 768, 'focal_length_mm': ('3.6'), 'sensor_height_mm': ('2.2684'), 'sensor_width_mm': ('3.590'), 'ip_address': '192.168.0.12'}, 
 {'camera_id': 3, 'width': 1024, 'height': 768, 'focal_length_mm': ('3.6'), 'sensor_height_mm': ('2.2684'), 'sensor_width_mm': ('3.590'), 'ip_address': '192.168.0.13'}, 
 {'camera_id': 4, 'width': 1024, 'height': 768, 'focal_length_mm': ('3.6'), 'sensor_height_mm': ('2.2684'), 'sensor_width_mm': ('3.590'), 'ip_address': '192.168.0.14'}]

'''
def test_secrets_util_existance():
    secrets_path = Path("plant_requests/utils/secrets_util.json")
    assert secrets_path.exists(), 'the secrets json fore the datbase connection does not exist'

def test_tag_query():
    tag_query = database_util.get_tag_information_from_database(1)

def test_get_camera_parameters():
    camera_parameters = database_util.get_available_camera_parameters_from_database()

def test_get_tag_scale():
    tag_scale = database_util.get_tag_scale_from_database(4)

def test_get_tag_views():
    print(database_util.get_tag_views_from_database(4))

    
    

def test_camera_existance():
    return None
'''
   
    
