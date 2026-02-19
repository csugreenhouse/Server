This is the main repository to explain code in the server repository. Each new method should have a breif explanation of what the method hopes to acheive, and various parameters. 

# SERVER
This repository holds the imaging software for the server. ANything that is on the server is also apart of this repository. This repository should not talk about camera information nor ESP32 information. The Program will be broken down in corresponding to file directories. The first of these directories is _Database_ This holds files to interact with the database. plant_request is in charge of requests, usually with input of an image, and does some processing of this image, to insert into the database. This is where most of the program resides. Lastly, run is used for essentially running the program. All of these will be broken down more further in the description.

# DATABASE
## DATABASE_UTIL.PY
Database util is the util responsible for getting and setting various parameters inside of the database. We will go through methods and each individual role they posses. Below are methods utalized.
### open_connection_to_database(): conn
This method is responsible for opening the connection to the database inside of the mini server in the greenhouse. Used for the actuall deployment of the server. It connects to the 'greenhouse' database. 
### open_connection_to_test_database(): conn
This method is responsible for opening the connection to the test database inside individuals computers for testing purposes. This greenhouse is called 'test-greenhouse'
### close_connection_to_database(conn): 
This method is responsible for closing the connection to the database. **it is very important to remember to close this after each connection is open** Otherwise, multiple connections could be open, eventually resulting in a crash. 
### get_available_camera_parameters_from_database(conn): camera_parameter_dictionary_list
This method finds all cameras in the database, and returns a list of camera_parameter dictionaries, which includes camera_id, width, height, focal_lenght_mm, sensor_height_mm, sensor_width_mm, and ip_address. 
### get_tag_views_from_database(conn, tag_id): view_dictionary_list
returns a list of view dictionaries that contain  plant_id, tag_id, scientific_name, view_type, image_bounds, color_bounds. This method is mainly used in the scan reference tags, and is the way for views to be fetched from teh database
### get_tag_scale_from_database(conn, tag_id): scale
queries the database and returns the scale of the april tag. will usually be .07. This is also in the creation of the scan_reference_tags and other methods found in the reference_tag_util
### execute_query(conn,query,params=None): results
responsible for cleaning the inputs of the queries to protect from malicious attacks. you should not call cur.execute(query) without cleaning the inputs of the query. 

# plant requests 
## REQUESTOR.PY
This is the main runner of the program. Currently, the main purpose of this program is to capture the image, and then is responsible for storing the image and the appropriate data in the database. Right now, it retreives all cameras from the database, and for each camera ip, captures the image from the ip adress. There are several methods that need to be implemented as well in this file.
# process image (image, reference_tags): success _not yet implemented_
will break up the reference tag views into their appropriate type. This means it will create height reference tags and width reference tags. It will then collect all the responsens, and then store the various images in the processed bin. 
For each response, it will store the informaiton in the database along with the relative image. 
# save_image_by_plant_id(plant_id, image): void
stores the raw image from the database into a plant folder.
# save_image_by_camera_id(plant_id,image): void 
stores teh raw image from the database into a camera id folder. 
# graph_info_by_camera: camera_id, image, camera_parameters,conn)
is a debug method, that shows the graph of the relative request of the responses. You can see these in the same directory as the requestor method.


plant requests consists of a major portion of the code in the program the plant rrequests files are sorted into area_request, height_request, width_request, and requestor
# area_request _not yet implemented_






  
