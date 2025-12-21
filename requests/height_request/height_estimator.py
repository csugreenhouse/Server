import apriltag
import argparse
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import psycopg2
from debug.debug import plot_image
from data_request.data_request import scan_apriltags, scan_qrtags


def plant_mask(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = (35, 120, 60)
    upper_green = (85, 255, 255)

    mask = cv2.inRange(hsv, lower_green, upper_green)
    return mask

def get_heighest_green_pixel(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = (35, 120, 60)
    upper_green = (85, 255, 255)

    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    green_pixels = cv2.findNonZero(mask)
    
    if green_pixels is None:
        raise ValueError("No green pixels found in the image")
    
    highest_pixel = min(green_pixels, key=lambda p: p[0][1])
    # prints the HSV color for debugging purposes
    # make it so that the pixel is relativley close to other green pixels. If it is an outlier, ignore it in the height calculation

    return tuple(highest_pixel[0])

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
def estimated_height(image, reference=None, method="apriltag", scale_units_m=.075,bias_correction_b=0.0):
    heighest_green_pixel = get_heighest_green_pixel(image)
    # if user wants to estimate height based on the april tag
    if reference is None:
        if method == "apriltag":
            scale_info = scan_apriltags(image)[0]
        if method == "qrtag":
            scale_info = scan_qrtags(image)[0]
    else:
        scale_info = reference
    
    # here I calculate the equation of the line passing through the top points of the april tag
    equation_top = get_equation_of_line(
        scale_info["corners"]["top_left"],
        scale_info["corners"]["top_right"]
    )
    # here I calculate the equation of the line passing through the bottom points of the april tag
    equation_bottom = get_equation_of_line(
        scale_info["corners"]["bottom_left"],
        scale_info["corners"]["bottom_right"]
    )
    # to estimate the height, I find the fraction of the distance between the top and bottom lines
    # where the heighest green pixel is located. I then multiply this fraction by the known height of the april tag
    fractional_height = fractional_height_between_lines(
        equation_top,
        equation_bottom,
        heighest_green_pixel
    )
    
    return scale_units_m * fractional_height + bias_correction_b

