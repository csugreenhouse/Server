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
import plant_requests.utils.database_util as database_util
import plant_requests.utils.image_util as image_util

camera_parameter_list = database_util.get_available_camera_parameters_from_database()


for camera_parameters in camera_parameter_list:
    print(f"Getting and saving image from {camera_parameters["ip_address"]}")
    try:
        image = image_util.get_image_from_camera_parameter(camera_parameters)
        camera_id = camera_parameters["camera_id"]
        image_util.save_image_to_server_directory(camera_id,image)
        cv2.imwrite(str(f"plant_requests/requestor/{camera_id}.jpg"), image)
    except Exception as e:
        raise RuntimeWarning("The camera ip adress was unable to be reached \n no file saved.")
    

    
