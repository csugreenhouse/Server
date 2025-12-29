
from datetime import datetime
import time
import tempfile
import requests
# below i will import processing functions
import sys
sys.path.append('/srv/samba/Server')
import cv2
import numpy as np

import plant_requests.debug.debug as dg

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

Camera_IPs = [
    "192.168.0.11"
]

plastic_bounds = {
    "lower_green": (25, 60, 30),
    "upper_green": (70, 255, 200),
}

image = get_image(f"http://{Camera_IPs[0]}/capture")
qr_list = data.scan_qrtags(image)
qr_tag = qr_list[0]

debug_info = hr.estimate_height_debug(image, qr_tag, method="qr", lower_green=plastic_bounds["lower_green"], upper_green=plastic_bounds["upper_green"])

dg.plot_image(image, out_path="/srv/samba/Server/image_getter/test_debug.png", qr_list=qr_list, 
                heighest_green_pixel=debug_info['heighest_green_pixel'], 
                green_blob_list=debug_info['green_blob_list'],
                estimated_height=debug_info['estimated_height']/100)

dg.plot_image_dimensions(image, out_path="/srv/samba/Server/image_getter/test.png", reference=qr_tag)
