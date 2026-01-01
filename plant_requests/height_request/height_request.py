import apriltag
import argparse
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import psycopg2
import sys
sys.path.append('/srv/samba/Server/plant_requests')
import numpy as np
import data_request.data_request as dr

"""
    VARIOUS HELPERS. CAN FOR THE MOST PART BE IGNORED
"""

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

def get_heighest_green_pixel(image, plant_blob_list):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    if len(plant_blob_list) == 0:
        raise ValueError("No plant detected in the image")
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
    return heighest_pixel   
    

def get_equation_of_line(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    if x2 - x1 == 0:
        raise ValueError("Vertical line - slope is undefined")
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    return slope, intercept
            
def fractional_height_between_lines(equation_top, equation_bottom, coordinate):
    slope_top, intercept_top = equation_top
    slope_bottom, intercept_bottom = equation_bottom
    x, y = coordinate
    
    y_top = slope_top * x + intercept_top
    y_bottom = slope_bottom * x + intercept_bottom
    
    if y_bottom - y_top == 0:
        raise ValueError("Top and bottom lines are the same - cannot compute fractional height")
    
    fractional_height = 1 - (y - y_top) / (y_bottom - y_top)
    return fractional_height  

"""
HEIGHT REQUEST. TAKES CAMERA_ID AND REFERENCE_TYPE AS INPUT, THEN RETURNS AN ESTIMATED HEIGHT, 
AND GRAPH INFO FOR PLOTTING
"""


def height_request(camera_id, reference_type="apriltag"):
    '''Clean inputs to make sure they are valid'''
    camera_parameters = dr.get_camera_parameters()
    image = dr.get_image_from_camera_parameters(camera_parameters)
    if reference_type not in ["apriltag", "qrtag"]:
        raise ValueError(f"Unknown reference_type: {reference_type}")
    if image is None:
        raise ValueError("Input image is None")
    if camera_id is None:
        raise ValueError("camera_id must be provided")
    
    camera_parameters = dr.get_camera_parameters(camera_id)
    
    apriltag_information_list = dr.scan_apriltags(image, camera_parameters)
    qrtag_information_list = dr.scan_qrtags(image, camera_parameters)

    if reference_type == "apriltag":
        reference_tag = dr.get_first_april_tag_info(apriltag_information_list)
        reference_tag = dr.append_database_info_to_april_tag(reference_tag)
    elif reference_type == "qrtag":
        reference_tag = dr.get_first_qr_tag_info(qrtag_information_list)

    estimated_height, estimate_height_graph_info = estimate_height(image, reference_tag)

    graph_info = estimate_height_graph_info 

    graph_info["qr_list"] = qrtag_information_list
    graph_info["april_list"] = apriltag_information_list
    graph_info["camera_parameters"] = camera_parameters

    return estimated_height, graph_info

"""
    ESTIMATE HEIGHT METHOD. FINDS TEH HEIGEST GREEN PIXEL GIVEN COLOR BOUNDS PROVIDED BY REFERENCE TAG
    THEN RETURNS ESTIMATED HEIGHT, ALONG WITH APPROPRIATE GRAPH INFO
"""

def estimate_height(image, reference_tag):

    color_bounds = reference_tag["color_bounds"]
    corners = reference_tag["corners"]
    tag_top_left_corner = corners["top_left"]
    tag_top_right_corner = corners["top_right"]
    tag_bottom_right_corner = corners["bottom_right"]
    tag_bottom_left_corner = corners["bottom_left"]
    tag_scale_units_m = reference_tag["scale_units_m"]
    tag_bias_units_m = reference_tag["bias_units_m"]


    plant_blob_list = scan_green_blobs(image, color_bounds)
    heighest_green_pixel = get_heighest_green_pixel(image, plant_blob_list=plant_blob_list)

    equation_top = get_equation_of_line(tag_top_left_corner, tag_top_right_corner)
    equation_bottom = get_equation_of_line(tag_bottom_left_corner, tag_bottom_right_corner)

    fractional_height = fractional_height_between_lines(equation_top, equation_bottom, heighest_green_pixel)

    estimated_height = tag_scale_units_m * fractional_height + tag_bias_units_m 

    graph_info = {
        "estimated_height" : estimated_height,
        "heighest_green_pixel" : heighest_green_pixel,
        "equation_top": equation_top,
        "equation_bottom": equation_bottom,
        "fractional_height": fractional_height,
        "reference_tag": reference_tag,
        "green_blob_list": plant_blob_list
    }

    return estimated_height, graph_info