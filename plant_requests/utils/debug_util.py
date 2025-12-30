from plant_requests.data_request.data_request import scan_qrtags, scan_apriltags, get_offsets
from plant_requests.height_request.height_estimator import get_heighest_green_pixel, get_equation_of_line, fractional_height_between_lines, estimate_height, scan_green_blobs
import cv2
import numpy as np

def estimate_height_debug(image, reference_tag=None, method="apriltag", color_bounds=((35, 120, 60), (85, 255, 255)), scale_units_m=.075, bias_correction_b=0.0):
    lower_green = color_bounds[0]
    upper_green = color_bounds[1]
    heighest_green_pixel = get_heighest_green_pixel(image, color_bounds)
    # if user wants to estimate height based on the april tag
    if reference_tag is None:
        if method == "apriltag":
            reference_tag = scan_apriltags(image)[0]
        if method == "qrtag":
            reference_tag = scan_qrtags(image)[0]
        elif method not in ["apriltag", "qrtag"]:
            raise ValueError(f"Unknown method: {method}")
        
    estimated_height = estimate_height(image, reference_tag=reference_tag, color_bounds=color_bounds, scale_units_m=scale_units_m, bias_correction_m=bias_correction_b)

    equation_top = get_equation_of_line(
        reference_tag["corners"]["top_left"],
        reference_tag["corners"]["top_right"]
    )
    # here I calculate the equation of the line passing through the bottom points of the april tag
    equation_bottom = get_equation_of_line(
        reference_tag["corners"]["bottom_left"],
        reference_tag["corners"]["bottom_right"]
    )
    # to estimate the height, I find the fraction of the distance between the top and bottom lines
    # where the heighest green pixel is located. I then multiply this fraction by the known height of the april tag
    fractional_height = fractional_height_between_lines(
        equation_top,
        equation_bottom,
        heighest_green_pixel
    )

    debug_info = {
        "estimated_height": estimated_height,
        "heighest_green_pixel": heighest_green_pixel,
        "equation_top": equation_top,
        "equation_bottom": equation_bottom,
        "fractional_height": fractional_height,
        "green_blob_list": scan_green_blobs(image, color_bounds=color_bounds),
        "qr_list": scan_qrtags(image),
        "april_list": scan_apriltags(image),
        "reference_tag": reference_tag
    }
    return debug_info