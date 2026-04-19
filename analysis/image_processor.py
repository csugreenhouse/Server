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


def process_images_of_plant(plant_id, beginning_date= None, ending_date=None):
    # to make terminal output red for warnings, you can use the following code to print the warning in red text
    print(f"\033[91mWARNING: THIS FUNCTION IS DESTRUCTIVE BECAUSE IT DELETES FILES IN THE PROCESSED FOLDER. MAKE SURE TO BACK UP YOUR FILES BEFORE RUNNING THIS FUNCTION.\n IT WILL ALSO DELETE ALL PLANT_ID ENTRIES CORRESPONDING TO THE HEIGHT IN THE HEIGHT LOG TABLE IN THE DATABASE FOR THE PLANT ID YOU SPECIFY.\n\033[0m")
    input("press enter to continue or ctrl+c to cancel/n")

    print(f"starting to process images for plant {plant_id}")

    # open database connection and get camera parameters
    conn = database_util.open_connection_to_database()
    camera_parameters = database_util.get_available_camera_parameters_from_database(conn)[0]

    database_util.delete_height_log_entries_for_plant_id(conn, plant_id)

    file_path = f"/srv/samba/plants/image/by_plant/plant{plant_id}/"
    processed_folder_path = f"/srv/samba/plants/image/by_plant/plant{plant_id}/processed/"
    Path(processed_folder_path).mkdir(parents=True, exist_ok=True)

    # delete all files in the processed folder
    for file in Path(processed_folder_path).glob("*"):
        file.unlink()

    # get all files in the file path. exclude folders as well   
    files = os.listdir(file_path)
    files = [file for file in files if os.path.isfile(os.path.join(file_path, file))]
    
    #sort files based on date
    files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(file_path, x)))
    print(f"file count = {len(files)} \n")
    # return a list with the files that are after the begining date, if the begining date is not None

    # EXAMPLE beggining date = "20260318 12:00:00"
    if beginning_date is not None:
        beginning_timestamp = time.mktime(time.strptime(beginning_date, "%Y%m%d %H:%M:%S"))
        files = [file for file in files if os.path.getmtime(os.path.join(file_path, file)) >= beginning_timestamp]
        print(f"file count after filtering by date = {len(files)} \n")
    if ending_date is not None:
         ending_timestamp = time.mktime(time.strptime(ending_date, "%Y%m%d %H:%M:%S"))
         files = [file for file in files if os.path.getmtime(os.path.join(file_path, file)) <= ending_timestamp]
         print(f"file count after filtering by end date = {len(files)} \n")
    if len(files) == 0:
        print("no files to process")
        return
    
    for i, image_name in enumerate(files):
        if i%50==0:
            print(f"on file: {i}")

        # get the timestame from the file name, which is in the format "20260318_120000.jpg"
        time_stamp = time.mktime(time.strptime(image_name.split(".")[0], "%Y%m%d_%H%M%S"))

        
        processed_file_path = processed_folder_path + image_name
        image = cv2.imread(file_path+image_name)

        # try to scan reference tags
        try:
            reference_tags = reference_tag_util.scan_reference_tags(image, camera_parameters, conn)
        except Exception as e:
            print(f"failed to scan reference tags for plant {plant_id} for file /srv/samba/plants/image/by_plant/plant{plant_id}/{image_name}")
            print(f"error: {e}")
            continue

        # filter the views in the reference tag so you dont do uneccessary work
        filtered_views = [view for view in reference_tags[0]["views"] if view["plant_id"]==plant_id]
        reference_tags[0]["views"] = filtered_views

        if (not filtered_views):
            print("OLD IMAGE OR NO RESPONSE TO BE PLOTTED")
            continue

        # if there is one reference tag, try to process the height request and graph the results
        if (len(reference_tags)==1):
            try:
                height_request_response = hr.height_request(image, reference_tags)
                #filtered_list = [response for response in height_request_response if response["plant_id"] == plant_id]
                database_util.insert_height_response_into_database(conn=conn, view_response=height_request_response[0], raw_file_path=file_path+image_name, processed_file_path=processed_file_path, time_stamp=time_stamp)

                gu.plot_height_request_response(image, processed_file_path, height_request_response)
            except Exception as e:
                print(f"failed to process image for plant {plant_id} for file /srv/samba/plants/image/by_plant/plant{plant_id}/{image_name}")
                print(f"error: {e}")
                # display failure
                continue
        else:
            print(f"more than one or no reference tag found for plant {plant_id} for file /srv/samba/plants/image/by_plant/plant{plant_id}/{image_name}")
            # display failure
            continue
    database_util.close_connection_to_database(conn)

#process_images_of_plant(1, beginning_date="20260218 12:00:00", ending_date="20260304 12:00:00")
#process_images_of_plant(5)
#process_images_of_plant(3, ending_date="20260212 12:00:00")
#process_images_of_plant(9, beginning_date="20260411 12:00:00")
#process_images_of_plant(10, beginning_date="20260406 12:00:00")
#process_images_of_plant(11, beginning_date="20260308 12:00:00")
#process_images_of_plant(12, beginning_date="20260308 12:00:00", ending_date="20260326 12:00:00")
#process_images_of_plant(13, beginning_date="20260326 12:00:00")
#process_images_of_plant(16, ending_date="20260326 12:00:00")
#process_images_of_plant(17, beginning_date="20260304 12:00:00")
#process_images_of_plant(18, beginning_date="20260311 12:00:00")
#process_images_of_plant(21, beginning_date="20260408 12:00:00")
#process_images_of_plant(22, beginning_date="20260404 12:00:00")
