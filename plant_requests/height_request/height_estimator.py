import apriltag
import argparse
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import psycopg2
import sys
sys.path.append('/srv/samba/Server/plant_requests')
from plant_requests.utils.graph_util import plot_image, plot_image_dimensions
from data_request.data_request import scan_apriltags, scan_qrtags
import numpy as np

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

def get_heighest_green_pixel(image, color_bounds):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    plant_mask_list = scan_green_blobs(image, color_bounds)
    if len(plant_mask_list) == 0:
        raise ValueError("No plant detected in the image")
    heighest_pixel = None
    mask = np.zeros(hsv.shape[:2], dtype="uint8")
    for plant in plant_mask_list:
        mask = cv2.bitwise_and(mask, plant["mask"])
        ys, xs = np.where(plant["mask"] > 0)
        if len(ys) == 0:
            continue
        if (heighest_pixel is None) or (np.min(ys) < heighest_pixel[1]):
            heighest_index = np.argmin(ys)
            heighest_pixel = (int(xs[heighest_index]), int(ys[heighest_index]))
    return heighest_pixel   

"""
LINEAR ALGEBRA HELPERS
- here exists the basic linear algebra functions needed to compute heights
"""
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
ESTIMATORS
- functions that estimate height using the scanners and getters
"""

def estimate_height(image, reference_tag=None, tag_type="apriltag", color_bounds=((35, 120, 60), (85, 255, 255)), scale_units_m=0.070, bias_correction_m=0.0):
    if reference_tag is None:
        if tag_type == "apriltag":
            reference_tag = scan_apriltags(image)[0]
        elif tag_type == "qrtag":
            reference_tag = scan_qrtags(image)[0]
        elif tag_type not in ["apriltag", "qrtag"]:
            raise ValueError(f"Unknown tag_type: {tag_type}")
    else:  
        tag_info = reference_tag
    heighest_green_pixel = get_heighest_green_pixel(image, color_bounds)

    # here I calculate the equation of the line passing through the top points of the april tag
    equation_top = get_equation_of_line(
        tag_info["corners"]["top_left"],
        tag_info["corners"]["top_right"]
    )
    # here I calculate the equation of the line passing through the bottom points of the april tag
    equation_bottom = get_equation_of_line(
        tag_info["corners"]["bottom_left"],
        tag_info["corners"]["bottom_right"]
    )
    # to estimate the height, I find the fraction of the distance between the top and bottom lines
    # where the heighest green pixel is located. I then multiply this fraction by the known height of the april tag
    fractional_height = fractional_height_between_lines(
        equation_top,
        equation_bottom,
        heighest_green_pixel
    )

    return scale_units_m * fractional_height + bias_correction_m
