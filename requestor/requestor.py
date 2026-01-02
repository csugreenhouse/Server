
from datetime import datetime
import time
import tempfile
import requests
# below i will import processing functions
import sys
sys.path.append('/srv/samba/Server')
import cv2
import numpy as np

import plant_requests.height_request.height_request as hr
import plant_requests.utils.graph_util as graph
import plant_requests.utils.info_getter_util as info_getter_util


def get_image(url):
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        image = response.content
        return cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
    except requests.exceptions.RequestException as e:
        print(f"failed to get image: {e}")
        return None
    
def request_organizer(reference_tags, camera_parameters, image):
    height_request_reference_tags = []
    area_request_reference_tags = []
    for reference_tag in reference_tags:
        if reference_tag.get("request_type").constains("height_estimation"):
            height_request_reference_tags.append(reference_tag)
        elif reference_tag.get("request_type").constains("area_estimation"):
            area_request_reference_tags.append(reference_tag)
    height_estimations, height_estimations_info = hr.height_request(
        image=image,
        reference_tags=height_request_reference_tags,
        camera_parameters=camera_parameters
    )
    # area_estimations, area_estimations_info = ar.area_request(
    #     image=image,
    #     reference_tags=area_request_reference_tags,
    #     camera_parameters=camera_parameters
    # )
    return (height_estimations, height_estimations_info),(None, None)

# SET WHICH CAMERAS TO USE. THIS WILL EVENTUALLY COME FROM THE DATABASE  
camera_ids = [1]
camera_IPs = [data.get_camera_ip(camera_id) for camera_id in camera_ids]

#get the image from the first camera

image = get_image(f"http://{camera_IPs[0]}/capture")
camera_parameters = hr.info_getter_util.qeury_camera_parameters(camera_ids[0])
reference_tags = hr.info_getter_util.get_reference_tags(image, camera_parameters)



