import argparse
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import psycopg2
import sys
sys.path.append('/srv/samba/Server/plant_requests')
import numpy as np
import plant_requests.utils.reference_tag_util as reference_tag_util
import database.database_util as database_util
import plant_requests.utils.line_util as line_util
import plant_requests.utils.image_util as image_util
import plant_requests.utils.reference_tag_util as reference_util

# THESE ARE HELPERS FOR HEIGHT REQUEST

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

def get_heighest_green_pixel(image, color_bounds, plant_bounds=(0,1)):
    W,H = image.shape[1], image.shape[0]
    # ignore x outside of plant_bounds
    if plant_bounds is not None:
        mask = np.zeros((H,W), dtype="uint8")
        x_min = int(max(0, plant_bounds[0]*W))
        x_max = int(min(W-1, plant_bounds[1]*W))
        mask[:, x_min:x_max] = 255
        image = cv2.bitwise_and(image, image, mask=mask)
    
    plant_blob_list = scan_green_blobs(image, color_bounds)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    if len(plant_blob_list) == 0:
        # dont stop the program, but still warn the user that no plant was detected, and return None for the heighest pixel and an empty list for the blob list. This way the height request can still be performed, but it will just return a height of 0.
        warnings.warn("No plant detected in the image with the given color bounds and plant bounds")
    heighest_pixel = None
    mask = np.zeros(hsv.shape[:2], dtype="uint8")
    for plant in plant_blob_list:
        mask = cv2.bitwise_and(mask, plant["mask"])
        ys, xs = np.where(plant["mask"] > 0)
        if len(ys) == 0:
            continue
        if (heighest_pixel is None) or (np.min(ys) < heighest_pixel[1]):
            heighest_index = np.argmin(ys)
            heighest_pixel = (int(xs[heighest_index]), int(ys[heighest_index]))
            
    graph_info = {
        "heighest_green_pixel": heighest_pixel,
        "green_blob_list": plant_blob_list,
        "plant_bounds": plant_bounds
    }
    
    return graph_info

# INTERACTION POINT BETWEEN REQUESTOR AND HEIGHT_REQUEST

def height_request(image, reference_tags, camera_parameters=None):
    if image is None:
        raise ValueError("Input image is None")
    if camera_parameters is None:
        raise ValueError("camera_parameters must be provided")
    if len(reference_tags) == 0:
        raise ValueError("No reference tags were provided")
    
    response = estimate_heights_reference_tags(image, reference_tags)
    
    return response
"""
 #PERFORM THE HEIGHT ESTIMATION AND RETURN THE APPROPRIATE DEBUG. RESPONSE IS IN FORMAT
        response [{
            "reference_tag": reference_tag,
            "plant_id": plant_id,
            "species_id": species_id,
            "estimated_height": estimated_height,
            "fractional_height": fractional_height,
            "equation_top": equation_top,
            "equation_bottom": equation_bottom,
            "heighest_green_pixel": heighest_green_pixel,
            "green_blob_list": green_blob_list,
            "plant_bounds" :plant_bounds,
            "color_bounds" :color_bounds,
            "bias_units_m" : bias_units_m
        }] WITH A LIST OF OTHER RESPONSES
"""

def estimate_heights_reference_tags(image, reference_tags):
    response = []
    for reference_tag in reference_tags:
        reference_tag_response = estimate_heights_reference_tag(image, reference_tag)
        response+=reference_tag_response
    return response

def estimate_heights_reference_tag(image, reference_tag):
    response = []
    views = reference_tag["views"]
    
    corners = reference_tag["corners"]
    tag_top_left_corner = corners["top_left"]
    tag_top_right_corner = corners["top_right"]
    tag_bottom_right_corner = corners["bottom_right"]
    tag_bottom_left_corner = corners["bottom_left"]
    tag_scale_units_m = reference_tag["scale_units_m"]
    
    for view in views:
        plant_id = view["plant_id"]
        bias_units_m = view["bias_units_m"]
        plant_bounds = (view["image_bound_lower"],view["image_bound_upper"])
        color_bounds = (view["color_bound_lower"],view["color_bound_upper"])
        
        heighest_green_pixel_info = get_heighest_green_pixel(image, color_bounds, plant_bounds)
        heighest_green_pixel = heighest_green_pixel_info["heighest_green_pixel"]
        green_blob_list = heighest_green_pixel_info["green_blob_list"]
        plant_bounds =heighest_green_pixel_info["plant_bounds"]
        
        equation_top = line_util.get_equation_of_line(tag_top_left_corner, tag_top_right_corner)
        equation_bottom = line_util.get_equation_of_line(tag_bottom_left_corner, tag_bottom_right_corner)
        

        if (heighest_green_pixel is None):
            fractional_height = 0
            estimated_height = 0
        else:  
            fractional_height = line_util.fractional_height_between_lines(equation_top, equation_bottom, heighest_green_pixel)
            estimated_height = tag_scale_units_m * fractional_height + bias_units_m 
        
        view_response = {
            "reference_tag": reference_tag,
            "plant_id": plant_id,
            "estimated_height": estimated_height,
            "fractional_height": fractional_height,
            "equation_top": equation_top,
            "equation_bottom": equation_bottom,
            "heighest_green_pixel": heighest_green_pixel,
            "green_blob_list": green_blob_list,
            "plant_bounds" :plant_bounds,
            "color_bounds" :color_bounds,
            "bias_units_m" : bias_units_m
        }
        
        response.append(view_response)
    
    return response
