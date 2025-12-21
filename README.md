# Server
This repository holds the imaging software for the server.

# SUMMARY OF CODE
  ## Image Getter 
		Responsable for scanning threw the ESP32 Cameras to access images
  ## Requests
		Responsible for all request types from the images
### height_request
		Responsible for estimating the height of an image given the image and a reference
### area_request
		Not yet implemented, responsibel for estimating the surface area of a plant
### data_request
		get data points such as
		- distance the base of the plant is away from the camera
		- qr code information
		- april tag information
### debug
		Responsible for draw picture, which is used for a nice debug screen to see information like april 
		tag location or mask of the plant
## database_interface
		Will be how the user interacts with the database. Only used for simple queries for now
		

  
