#find all the heights of the plants in a folder and then return a list of their heights, along with a date and time stamp for each height measurement.

import time
import cv2
import sys
sys.path.append('/srv/samba/Server') 
import plant_requests.height_request.height_request as hr
import plant_requests.utils.reference_tag_util as reference_util
import database.database_util as database_util
import plant_requests.utils.graph_util as graph_util

from pathlib import Path

def main():
    ## for plant 1, get the main file path
    plant_id = 2



    main_file_path = f"/srv/samba/plants/image/by_plant/plant{plant_id}/"
    processed_file_path = f"/srv/samba/plants/image/by_plant/plant{plant_id}/processed/"

    # change it to accept less black pixels
    plant_color_bounds = ((30, 60, 30),(90, 255, 255)) # this should be the same as the color bounds for the plant in the database for this plant id# this should be the same as the color bounds for the plant in the database for this plant id

    conn = database_util.open_connection_to_database()
    database_util.set_color_bounds_for_species_in_database(conn, 1, plant_color_bounds)
    camera_parameters = database_util.get_available_camera_parameters_from_database(conn)
  

    # collect all the files inside of the main file path
    files = Path(main_file_path).glob("*.jpg")

    for file_name in files:
        print(f"Processing file: {file_name}")
        try:
            image = cv2.imread(str(file_name))
            reference_tags = reference_util.scan_reference_tags(image, camera_parameters=camera_parameters[0], conn=conn)
            height_response = hr.height_request(image, reference_tags, camera_parameters=camera_parameters[0])
            print(f"{file_name}: {height_response[0]['estimated_height']} cm")
            processed_file_name = processed_file_path + file_name.name.split('.')[0] + "_out.png"
            graph_util.plot_height_request_response(image, processed_file_name, height_response)
            print(f"Saved processed image to {processed_file_name}")
            timestamp = file_name.name.split('.')[0] 
            database_util.insert_height_response_into_database(conn, height_response[0], str(file_name), processed_file_name, timestamp)
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
            continue

    database_util.close_connection_to_database(conn)

main()
