# starting by using all the same packages as height request
import argparse
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import psycopg2
import sys
sys.path.append('/srv/samba/Server/plant_requests')
import numpy as np

#including the custom attributes from the tag, which will
#specify the plants and their bounds, as well as more info
import plant_requests.utils.reference_tag_util as reference_tag_util
import plant_requests.utils.line_util as line_util
import plant_requests.utils.image_util as image_util
import plant_requests.utils.reference_tag_util as reference_util

#Here begin the helper methods for the width request
# there are the following:
#       1. creates bounds of the plant using openCV, the same as the height request. perhaps we can make a place where this can be called so it only needs to be written once.
#       2. take the green boundaries and determine right and left most pixels

#this method creates the bounds of the plant, primarily leaves. it uses
# opencv to define the borders in a green color
def scan_green_blobs(image,
                color_bounds,
                open_kernel_size=(5,5),
                close_kernel_size=(5,5),
                minimum_area_pixels=500,
                maximum_area_pixels=100000
                ):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_bounds[0], color_bounds[1])
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, open_kernel_size)
    k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, close_kernel_size)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k_open)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k_close)
    numb_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    plant_blob_list = []
    for label in range(1, numb_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        if minimum_area_pixels <= area <= maximum_area_pixels:
            plant_mask = (labels == label).astype("uint8") * 255
            plant_blob_list.append({
                "label": label,
                "centroid": (float(centroids[label][0]), float(centroids[label][1])),
                "area": int(area),
                "mask": plant_mask
            })
    return plant_blob_list

# find max and min pixels in the x axis; this is the main development of this file
def get_maxmin_x_green_pixel(image, color_bounds, plant_bounds=(0,1)):
    W,H = image.shape[1], image.shape[0] # size of the digital canvas.

    # this is an image slicer from the reference tag. It segments it vertically, 
    # so that side by side plants are not accidentally merged. This info is
    # inherited from the database. Since there are not plants vertically stacked
    # in any images, this needs not change
    if plant_bounds is not None:
        mask = np.zeros((H,W), dtype="uint8")
        x_min = int(max(0, plant_bounds[0]*W))
        x_max = int(min(W-1, plant_bounds[1]*W))
        mask[:, x_min:x_max] = 255
        image = cv2.bitwise_and(image, image, mask=mask)
    
    plant_blob_list = scan_green_blobs(image, color_bounds)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    if len(plant_blob_list) == 0:
        raise ValueError("No plant detected in the image")
    
    leftmost_pixel = None
    rightmost_pixel = None

    mask = np.zeros(hsv.shape[:2], dtype="uint8")
    for plant in plant_blob_list: #this is not different plants, but rather disconnected parts of the same plant
        mask = cv2.bitwise_and(mask, plant["mask"])
        ys, xs = np.where(plant["mask"] > 0)
        if len(ys) == 0:
            continue

        # np.min(xs) <- in this context, xs is a list of the x vals of every green outline
        # pixel from the plant detection.
        if (leftmost_pixel is None) or (np.min(xs) < leftmost_pixel[0]):
            leftmost_index = np.argmin(xs)
            leftmost_pixel = (int(xs[leftmost_index]), int(ys[leftmost_index]))

        if (rightmost_pixel is None) or (np.max(xs) > rightmost_pixel[0]):
            rightmost_index = np.argmax(xs)
            rightmost_pixel = (int(xs[rightmost_index]), int(ys[rightmost_index]))
            
    graph_info = {
        "leftmost_green_pixel": leftmost_pixel,
        "rightmost_green_pixel": rightmost_pixel,
        "green_blob_list": plant_blob_list,
        "plant_bounds": plant_bounds
    }
    
    return graph_info #I think this part is to make the images to help visually troubleshoot


# Below is the actual width estimation part

def width_request(image, reference_tags, camera_parameters):
    # Same errors as height request
    if image is None:
        raise ValueError("Input image is None")
    if camera_parameters is None:
        raise ValueError("camera_parameters must be provided")
    if len(reference_tags) == 0:
        raise ValueError("No reference tags were provided")
    
    response = estimate_widths_reference_tags(image, reference_tags)
    return response

def estimate_widths_reference_tags(image, reference_tags):
    response = []
    for reference_tag in reference_tags:
        reference_tag_response = estimate_widths_reference_tag(image, reference_tag)
        response+=reference_tag_response
    return response

def estimate_widths_reference_tag(image, reference_tag):
    response = []
    views = reference_tag["views"]
    
    corners = reference_tag["corners"]

    tag_left_top = corners["top_left"]
    tag_left_bottom = corners["bottom_left"]
    tag_right_top = corners["top_right"]
    tag_right_bottom = corners["bottom_right"]
    
    tag_scale_units_m = reference_tag["scale_units_m"]

    for view in views: #iterate through every plant in the image
        plant_id = view["plant_id"]
        #bias_units_m = view["bias_units_m"] #bias offset for the bottom y bound, not needed here but only for height
        plant_bounds = (view["image_bound_lower"],view["image_bound_upper"]) #left and right boundaries in img
        color_bounds = (view["color_bound_lower"],view["color_bound_upper"])
        
        pixel_info = get_maxmin_x_green_pixel(image, color_bounds, plant_bounds)
        
        left_pixel = pixel_info["leftmost_green_pixel"]
        right_pixel = pixel_info["rightmost_green_pixel"]
        
        equation_left = line_util.get_equation_of_line(tag_left_top, tag_left_bottom)
        equation_right = line_util.get_equation_of_line(tag_right_top, tag_right_bottom)
        
        f_left = line_util.fractional_width_between_lines(equation_left, equation_right, left_pixel)
        f_right = line_util.fractional_width_between_lines(equation_left, equation_right, right_pixel)
        
        fractional_width = abs(f_right - f_left)
                
        estimated_width = tag_scale_units_m * fractional_width
        
        view_response = {
            "reference_tag": reference_tag,
            "plant_id": plant_id,
            "estimated_width": estimated_width,
            "fractional_width": fractional_width,
            #"equation_top": equation_top,
            #"equation_bottom": equation_bottom,
            "leftmost_green_pixel": left_pixel,
            "rightmost_green_pixel": right_pixel,
            "green_blob_list": pixel_info["green_blob_list"],
            "plant_bounds" :plant_bounds,
            "color_bounds" :color_bounds,
            #"bias_units_m" : bias_units_m
        }
        
        response.append(view_response)
    
    return response