from datetime import datetime
import time
# below i will import processing functions
import sys
sys.path.append('/srv/samba/Server')
import cv2

import plant_requests.height_request.height_request as hr
import plant_requests.utils.graph_util as graph_util
import plant_requests.utils.image_util as image_util
import plant_requests.utils.reference_tag_util as reference_util
import database.database_util as database_util

conn = database_util.open_connection_to_database()

camera_parameter_list = database_util.get_available_camera_parameters_from_database(conn)
database_util.set_color_bounds_for_species_in_database(conn, 2, ((28, 30, 25), (95, 255, 180))) #lettuce
database_util.set_color_bounds_for_species_in_database(conn, 3, ((30, 60, 30),(85, 240, 255))) #basil
database_util.close_connection_to_database(conn)

def main():
    while(True):
        print("starting again")
        for camera_parameters in camera_parameter_list:
            image = None
            print(f"Getting and saving image from https:{camera_parameters['ip_address']}")
            try:
                image = image_util.get_image_from_camera_parameter(camera_parameters)

                #save by camera id
                camera_id = camera_parameters["camera_id"]
                save_image_by_camera_id(camera_id, image)

                conn = database_util.open_connection_to_database()
                #save for each plant id in the image
                if image is not None:
                    reference_tags = reference_util.scan_reference_tags(image,camera_parameters,conn)
                    for reference_tag in reference_tags:
                        views = reference_tag["views"]
                        for view in views:
                            save_image_by_plant_id(view["plant_id"], image)
                print(f"image successfully saved by plant id and camera number")

                graph_info_by_camera(camera_id, image, camera_parameters,conn)

                database_util.close_connection_to_database(conn)

            except Exception as e:
                print(e)
                print(f"\033[91mfailed to get image from camera {camera_parameters['camera_id']}\033[0m")
            
        print("taking a break")
        # wait 30 for the next round of images and height requests
        time.sleep(1800)

def save_image_by_plant_id(plant_id, image):
    try:
        save_path = image_util.save_image_to_server_directory_by_plant(plant_id,image)
        cv2.imwrite(str(f"plant_requests/requestor/by_plant/{plant_id}.jpg"), image)
        print(f"\033[92mimage successfully saved by plant to : {save_path}\033[0m")
    except Exception as e:
        print(e)
        print("\033[91mFailed to save image by plant, for plant no. {plant_id}\033[0m")

def save_image_by_camera_id(camera_id, image):
    try:
        save_path = image_util.save_image_to_server_directory(camera_id,image)
        cv2.imwrite(str(f"plant_requests/requestor/by_camera/{camera_id}.jpg"), image)
        print(f"image successfully saved by camera number to : {save_path}")
    except Exception as e:
        print(e)
        print("\033[91mFailed to save image by camera, for camera no. {camera_id}\033[0m")

def graph_info_by_camera(camera_id, image, camera_parameters,conn):
    try: 
        if image is not None:
            reference_tags = reference_util.scan_reference_tags(image,camera_parameters,conn)
            for reference_tag in reference_tags:
                response = hr.height_request(image, [reference_tag], camera_parameters)
            
            graph_path = f"plant_requests/requestor/{camera_id}_graph.jpg"
            graph_util.plot_height_request_response(image, graph_path,response)
            print(f"\033[92mgraph successfully saved to : {graph_path}\033[0m")
    except Exception as e:
        print(e)
        print(f"\033[91mfailed to process height request for camera {camera_parameters['camera_id']}\033[0m")

main()
























'''
while True:
    print("starting again")
    for camera_parameters in camera_parameter_list:
        image = None
        print(f"Getting and saving image from https:{camera_parameters['ip_address']}")
        try:
            image = image_util.get_image_from_camera_parameter(camera_parameters)
            camera_id = camera_parameters["camera_id"]
            save_path = image_util.save_image_to_server_directory(camera_id,image)
            cv2.imwrite(str(f"plant_requests/requestor/{camera_id}.jpg"), image)
            print(f"image successfully saved to : {save_path}")
        except Exception as e:
            
            print(e)
            print(f"failed to get image from camera {camera_parameters['camera_id']}")
        try: 
            if image is not None:
                reference_tags = reference_util.scan_reference_tags(image,camera_parameters)
                for reference_tag in reference_tags:
                    response = hr.height_request(image, [reference_tag], camera_parameters)
                
                graph_path = f"plant_requests/requestor/{camera_id}_graph.jpg"
                graph_util.plot_height_request_response(image, graph_path,response)
                print(f"graph successfully saved to : {graph_path}")
        except Exception as e:
            print(e)
            print(f"failed to process height request for camera {camera_parameters['camera_id']}")

        time.sleep(5)
    print("taking a break")
    time.sleep(1800)

'''