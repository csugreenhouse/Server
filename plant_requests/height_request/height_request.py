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
import plant_requests.utils.scanner_util as scanner_util
import plant_requests.utils.info_getter_util as info_getter_util
import plant_requests.utils.line_util as line_util
import plant_requests.utils.image_getter_util as image_getter_util


def get_heighest_green_pixel(image, color_bounds, plant_bounds=(0,1)):
    W,H = image.shape[1], image.shape[0]
    # ignore x outside of plant_bounds
    if plant_bounds is not None:
        mask = np.zeros((H,W), dtype="uint8")
        x_min = int(max(0, plant_bounds[0]*W))
        x_max = int(min(W-1, plant_bounds[1]*W))
        mask[:, x_min:x_max] = 255
        image = cv2.bitwise_and(image, image, mask=mask)
    
    plant_blob_list = scanner_util.scan_green_blobs(image, color_bounds)
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
            
    graph_info = {
        "heighest_pixel": heighest_pixel,
        "green_blob_list": plant_blob_list
    }
    return heighest_pixel, graph_info

def height_request(camera_id, reference_type="apriltag"):
    camera_parameters = info_getter_util.qeury_camera_parameters(camera_id)
    image = image_getter_util.get_image_from_camera_parameters(camera_parameters)
    
    if reference_type not in ["apriltag", "qrtag"]:
        raise ValueError(f"Unknown reference_type: {reference_type}")
    if image is None:
        raise ValueError("Input image is None")
    if camera_id is None:
        raise ValueError("camera_id must be provided")
    
    camera_parameters = info_getter_util.get_camera_parameters(camera_id)
    
    apriltag_information_list = scanner_util.scan_apriltags(image)
    qrtag_information_list = scanner_util.scan_qrtags(image)
    
    reference_tags = info_getter_util.make_reference_tags(camera_parameters, apriltag_information_list)
    
    estimated_heights, estimated_heights_info = estimate_heights(image, reference_tags)

    for reference_tag in reference_tags:
        estimated_height, estimate_height_graph_info = estimate_height(image, reference_tag)
        estimated_heights.append(estimated_height)
        estimated_heights_info.append(estimate_height_graph_info)

    graph_info = {
        "estimed_heights": [res[0] for res in result],
        "estimated_heights_info": [res[1] for res in result],
        "qr_list": qrtag_information_list,
        "april_list": apriltag_information_list,
        "camera_parameters": camera_parameters,
    }

    return estimated_heights, estimated_heights_info

def estimate_heights(image, reference_tags):
    estimated_heights = []
    estimated_heights_info = []
    for reference_tag in reference_tags:
        estimated_height, estimate_height_graph_info = estimate_height(image, reference_tag)
        estimated_heights.append(estimated_height)
        estimated_heights_info.append(estimate_height_graph_info)
    return estimated_heights, estimated_heights_info

def estimate_height(image, reference_tag):
    color_bounds = reference_tag["color_bounds"]
    plant_bounds = reference_tag["plant_bounds"]
    corners = reference_tag["corners"]
    tag_top_left_corner = corners["top_left"]
    tag_top_right_corner = corners["top_right"]
    tag_bottom_right_corner = corners["bottom_right"]
    tag_bottom_left_corner = corners["bottom_left"]
    tag_scale_units_m = reference_tag["scale_units_m"]
    tag_bias_units_m = reference_tag["bias_units_m"]

    heighest_green_pixel, heighest_green_pixel_graph_info = get_heighest_green_pixel(image, color_bounds, plant_bounds)

    equation_top = line_util.get_equation_of_line(tag_top_left_corner, tag_top_right_corner)
    equation_bottom = line_util.get_equation_of_line(tag_bottom_left_corner, tag_bottom_right_corner)

    fractional_height = line_util.fractional_height_between_lines(equation_top, equation_bottom, heighest_green_pixel)

    estimated_height = tag_scale_units_m * fractional_height + tag_bias_units_m 

    graph_info = {
        "estimated_height" : estimated_height,
        "heighest_green_pixel" : heighest_green_pixel,
        "equation_top": equation_top,
        "equation_bottom": equation_bottom,
        "fractional_height": fractional_height,
        "reference_tag": reference_tag,
        "green_blob_list": heighest_green_pixel_graph_info["green_blob_list"],
    }

    return estimated_height, graph_info