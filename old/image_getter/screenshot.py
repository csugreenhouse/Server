
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
import plant_requests.height_request.height_request as hr
import plant_requests.area_request as ar
import database_interface.database_interface as db
import plant_requests.data_request.data_request as data
import plant_requests.utils.graph_util as graph


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
camera_IPs = [data.get_camera_ip(camera_id) for camera_id in camera_ids]

#get the image from the first camera
image = get_image(f"http://{camera_IPs[0]}/capture")
# estimate the height. The debug info is used to make a debug graph.
height_estimate, debug_info = hr.height_request(camera_id=camera_ids[0], reference_type="apriltag")

# debug graph of the height estimation
graph.plot_image_height(image, out_path="/srv/samba/Server/image_getter/test_debug.png", debug_info=debug_info)
