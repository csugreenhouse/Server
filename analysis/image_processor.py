import os
import cv2
import numpy as np
from pathlib import Path
import time

import sys
sys.path.append('/srv/samba/Server')

import plant_requests.height_request.height_request as hr
import plant_requests.utils.reference_tag_util as reference_tag_util
import plant_requests.utils.graph_util as gu
import database.database_util as database_util

def process_images_of_plant(plant_id, begining_date= None):
    conn = database_util.open_connection_to_database()
    camera_parameters = database_util.get_available_camera_parameters_from_database(conn)[0]
    file_path = f"/srv/samba/plants/image/by_plant/plant{plant_id}/"
    processed_folder_path = f"/srv/samba/plants/image/by_plant/plant{plant_id}/processed/"
    Path(processed_folder_path).mkdir(parents=True, exist_ok=True)

    # delete all files in the processed folder
    for file in Path(processed_folder_path).glob("*"):
        file.unlink()

    files = os.listdir(file_path)
    #sort files based on date
    files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(file_path, x)))
    print(f"file count = {len(files)} \n")
    # return a list with the files that are after the begining date, if the begining date is not None
    # EXAMPLE beggining date = "20260318 12:00:00"
    if begining_date is not None:
        begining_timestamp = time.mktime(time.strptime(begining_date, "%Y%m%d %H:%M:%S"))
        files = [file for file in files if os.path.getmtime(os.path.join(file_path, file)) >= begining_timestamp]
        print(f"file count after filtering by date = {len(files)} \n")
    if len(files) == 0:
        print("no files to process")
    #touch the folder to make sure it exists: 
    for i, image_name in enumerate(files):
        if i%50==0:
            print(f"on file: {i}")
        if (image_name=="processed"):
            continue
        processed_file_path = processed_folder_path + image_name
        image = cv2.imread(file_path+image_name)
        reference_tags = reference_tag_util.scan_reference_tags(image, camera_parameters, conn)

        filtered_views = [view for view in reference_tags[0]["views"] if view["plant_id"]==plant_id]
        reference_tags[0]["views"] = filtered_views
        if (len(reference_tags)==1):
            try:
                height_request_response = hr.height_request(image, reference_tags)
                filtered_list = [response for response in height_request_response if response["plant_id"] == plant_id]
                if (not filtered_list):
                    print("OLD IMAGE OR NO RESPONSE TO BE PLOTTED")
                    break
                gu.plot_height_request_response(image, processed_file_path, filtered_list)
            except Exception as e:
                print(f"failed to process image for plant {plant_id} for file {image_name}")
                # display failure
                continue
    database_util.close_connection_to_database(conn)

#this is how to change x bounds for one plant.
connupdate = database_util.open_connection_to_database()
#database_util.define_plant_x_bounds_in_database(conn=connupdate, plant_id = 13, xlow=.75, xhigh=1)
#color_bounds = ((30, 110, 110),(90, 240, 255)) #mint
#good, but picking up to much grey. 
color_bounds = ((30, 150, 110),(90, 240, 255)) #mint
database_util.set_color_bounds_for_species_in_database(conn=connupdate, species_id=1, color_bounds=((30, 110, 110),(90, 240, 255))) #mint
database_util.close_connection_to_database(connupdate)

process_images_of_plant(14, "20260321 12:00:00")