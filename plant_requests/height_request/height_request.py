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
import plant_requests.utils.plant_finder_util as plant_finder_util



def get_heighest_green_pixel(image, color_bounds, plant_bounds, minimum_area_pixels):
    W,H = image.shape[1], image.shape[0]
    # ignore x outside of plant_bounds
    if plant_bounds is not None:
        mask = np.zeros((H,W), dtype="uint8")
        x_min = int(max(0, plant_bounds[0]*W))
        x_max = int(min(W-1, plant_bounds[1]*W))
        y_min = int(max(0, plant_bounds[2]*H))
        y_max = int(min(H-1, plant_bounds[3]*H))
        mask[y_min:y_max, x_min:x_max] = 255
        image = cv2.bitwise_and(image, image, mask=mask)
    
    green_blobs = plant_finder_util.find_green_blobs(image, color_bounds, minimum_area_pixels=minimum_area_pixels)
    mask_result = plant_finder_util.grow_plant_mask(image, green_blobs, color_tolerance=22, anchor_area_fraction=0.75, anchor_max_proximity_px=25)
    
    mask = mask_result["filtered_mask"]
    heighest_pixel = None
    
    for pixel in np.argwhere(mask > 0):
        py, px = pixel
        if (heighest_pixel is None) or (py < heighest_pixel[1]):
            heighest_pixel = (int(px), int(py))
            
    graph_info = {
        "heighest_green_pixel": heighest_pixel,
        "green_blob_list": mask_result["kept_blobs"],
        "plant_bounds": plant_bounds
    }
    
    return graph_info

def height_request(image, reference_tags):

    reference_tags = reference_util.filter_reference_tags_by_view_type(reference_tags, "height")
    if image is None:
        raise ValueError("Input image is None")
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
        plant_bounds = (view["image_bound_x_low"],view["image_bound_x_high"], view["image_bound_y_low"], view["image_bound_y_high"])
        color_bounds = (view["color_bound_lower"],view["color_bound_upper"])
        minimum_area_pixels = view["minimum_area_pixels"]
        
        heighest_green_pixel_info = get_heighest_green_pixel(image, color_bounds, plant_bounds, minimum_area_pixels)
        heighest_green_pixel = heighest_green_pixel_info["heighest_green_pixel"]
        green_blob_list = heighest_green_pixel_info["green_blob_list"]
        plant_bounds = heighest_green_pixel_info["plant_bounds"]
        
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
