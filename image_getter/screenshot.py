
from datetime import datetime
import time
import tempfile
import requests
# below i will import processing functions
import sys
sys.path.append('/srv/samba/Server')
import cv2
import numpy as np

import plant_requests.utils.debug_util as debug
import plant_requests.utils.graph_util as dg
import plant_requests.height_request.height_estimator as hr
import plant_requests.area_request as ar
import database_interface.database_interface as db
import plant_requests.data_request.data_request as data


def get_image(url):
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        image = response.content
        return cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
    except requests.exceptions.RequestException as e:
        print(f"failed to get image: {e}")
        return None
  
# SET WHICH CAMERAS TO USE. THIS WILL EVENTUALLY COME FROM THE DATABASE  
camera_ids = [1]
Camera_IPs = [data.get_camera_ip(camera_id) for camera_id in camera_ids]


image = get_image(f"http://{Camera_IPs[0]}/capture")

debug_info = debug.estimate_height_debug(image, camera_number=camera_ids[0], reference_type="apriltag")

qr_list = debug_info['qr_list']
qr_tag = debug_info['reference_tag']
april_list = debug_info['april_list']

graph.plot_image_height(image, out_path="/srv/samba/Server/image_getter/test_debug.png", debug_info=debug_info)
