from datetime import datetime
import time
# below i will import processing functions
import sys
sys.path.append('/srv/samba/Server')
import cv2
#module not found error, to fix: 
#1. check if the path is correct
#2. check if there is an __init__.py file in the directory (not strictly necessary in Python 3.3 and above, but can help with recognition)
#
sys.path.append('/srv/samba')
import Warning.sensor as sensor


import plant_requests.height_request.height_request as hr
import plant_requests.utils.graph_util as graph_util
import plant_requests.utils.image_util as image_util
import plant_requests.utils.reference_tag_util as reference_util
import database.database_util as database_util
import numpy as np




conn = database_util.open_connection_to_database()

#To select only the 6 and 7th element, you would use the following code: database_util.get_available_camera_parameters_from_database(conn)[5:7]
camera_parameter_list = database_util.get_available_camera_parameters_from_database(conn)

# HUE - what colors, green is around 60, red is around 0 or 180, blue is around 120
# SATURATION - how much color vs white, 0 is white, 255 is fully colored
# VALUE - how much color vs black, 0 is black, 255 is fully bright
database_util.set_color_bounds_for_species_in_database(conn, 2, ((28, 30, 25), (95, 255, 180))) #lettuce
database_util.set_color_bounds_for_species_in_database(conn, 3, ((30, 35, 30), (95, 255, 180))) #basil
database_util.set_color_bounds_for_species_in_database(conn, 1, ((30, 100, 100),(85, 240, 255))) #mint
database_util.close_connection_to_database(conn)

def main():
   while(True):
       turn_lights_back_off = False
       print("starting again")
       if (not sensor.are_lights_on()):
            print("lights are off, turning on")
            turn_lights_back_off = True
            sensor.turn_on_lights()

       for camera_parameters in camera_parameter_list:
           image = None
           frames = []
           print(f"Getting and saving image average from https:{camera_parameters['ip_address']}")
           try:
               for i in range(10): #nominal number of frames to average, tune for light artefacts and processing time
                   roughimage = image_util.get_image_from_camera_parameter(camera_parameters)
                   if roughimage is not None:
                       frames.append(roughimage.astype(np.float64)) #overflow
                   time.sleep(0.025+(i*0.05)) #delay, tune for light artefacts. I needed i to be factored in to ensure the frames were not all taken at the same time, which would compound the light artefacts instead of averaging them out.


               image = np.mean(frames, axis=0).astype(np.uint8)


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

       if (turn_lights_back_off):
           print("lights are on, turning off")
           sensor.turn_off_lights()

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


def graph_info_by_camera(camera_id, image, camera_parameters, conn):
   try:
       if image is not None:
           print("here")
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

