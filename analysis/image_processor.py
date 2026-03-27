import os
import cv2
import numpy as np
from pathlib import Path

import sys
sys.path.append('/srv/samba/Server')

import plant_requests.height_request.height_request as hr
import plant_requests.utils.reference_tag_util as reference_tag_util
import plant_requests.utils.graph_util as gu
import database.database_util as database_util

def process_images_of_plant(plant_id):
    conn = database_util.open_connection_to_database()
    camera_parameters = database_util.get_available_camera_parameters_from_database(conn)[0]
    file_path = f"/srv/samba/plants/image/by_plant/plant{plant_id}/"
    processed_folder_path = f"/srv/samba/plants/image/by_plant/plant{plant_id}/processed/"
    Path(processed_folder_path).mkdir(parents=True, exist_ok=True)
    #touch the folder to make sure it exists: 
    for image_name in os.listdir(file_path):
        if (image_name=="processed"):
            continue
        processed_file_path = processed_folder_path + image_name
        image = cv2.imread(file_path+image_name)
        reference_tags = reference_tag_util.scan_reference_tags(image, camera_parameters, conn)
        heigh_request_response = hr.height_request(image, reference_tags)
        gu.plot_height_request_response(image, processed_file_path, heigh_request_response)
    
    database_util.close_connection_to_database(conn)
'''
#this is how to change x bounds for one plant.
connupdate = database_util.open_connection_to_database()
database_util.define_plant_x_bounds_in_database(conn=connupdate, plant_id = 18, xlow=.75, xhigh=.95)
database_util.close_connection_to_database(connupdate)
'''
process_images_of_plant(18)