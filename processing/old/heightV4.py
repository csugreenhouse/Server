import apriltag
import argparse
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import psycopg2
import numpy as np

""" 
SCANNERS AND GETTERS
- Things that can easily be found and require no calculations. 
"""

def scan_apriltags(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"could not load image: {image_path}")

    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    options = apriltag.DetectorOptions(families="tag25h9")
    detector = apriltag.Detector(options)
    results = detector.detect(gray)
    
    DECISION_MARGIN = 40.0

    valid_tags = []

    for tag in results:
        #print(f"TAG ID {tag.tag_id} with decision margin {tag.decision_margin}")
        if (tag.decision_margin>DECISION_MARGIN):
            valid_tags.append(
                {
                    "data": tag.tag_id,
                    "center": tuple(tag.center),
                    "corners": {
                        "top_left": tuple(tag.corners[0]),
                        "top_right": tuple(tag.corners[1]),
                        "bottom_right": tuple(tag.corners[2]),
                        "bottom_left": tuple(tag.corners[3]),
                    }
                })
    if (len(valid_tags)==0):
        if (len(results)!=0):
            raise ValueError(f"No Valid april tag has been detected, but a non valid one has been found")
        else:
            raise ValueError(f"No april tags at all have been found")
  
    if (len(valid_tags)>1):
        warnings.warn(f"Multiple valid AprilTags detected ({len(valid_tags)})", RuntimeWarning)
    
    return valid_tags


def scan_qrtags(image_path):
    image = cv2.imread(str(image_path))
    if image is None:   
        raise ValueError(f"could not load image: {image_path}") 
    
    detector = cv2.QRCodeDetector()
    retval, list_of_qr_data, list_of_qr_points, _ = detector.detectAndDecodeMulti(image)
    
    valid_tags = []

    if not retval or list_of_qr_points is None or list_of_qr_data is None:
        raise ValueError("No QR tags have been found")
    
    for data, points in zip(list_of_qr_data, list_of_qr_points):
        # skip undecoded entries
        if not data or points is None:
            continue

        # points has shape (4, 2)
        center = tuple(points.mean(axis=0))

        valid_tags.append({
            "data": data,
            "center": center,
            "corners": {
                "top_left":     tuple(points[0]),
                "top_right":    tuple(points[1]),
                "bottom_right": tuple(points[2]),
                "bottom_left":  tuple(points[3]),
            }
        })

    if len(valid_tags) == 0:
        raise ValueError("No valid QR tags have been found")

    if len(valid_tags) > 1:
        warnings.warn(
            f"Multiple valid QR Tags detected ({len(valid_tags)})",
            RuntimeWarning
        )

    return valid_tags


def scan_plants(image_path,
                lower_green=(20, 30, 30),
                upper_green=(80, 300, 180),
                open_kernel_size=(5,5),
                close_kernel_size=(5,5),
                minimum_area_pixels=1000,
                maximum_area_pixels=100000
                ):
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"could not load image: {image_path}")
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)

    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, open_kernel_size)
    k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, close_kernel_size)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k_open)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k_close)

    numb_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

    plants = []

    for label in range(1, numb_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        if minimum_area_pixels <= area <= maximum_area_pixels:
            plant_mask = (labels == label).astype("uint8") * 255
            plants.append({
                "label": label,
                "centroid": (float(centroids[label][0]), float(centroids[label][1])),
                "area": int(area),
                "mask": plant_mask
            })

    return plants
            


def get_heighest_green_pixel(image_path, lower_green=(60, 30, 30), upper_green=(80, 300, 180), show_mask=False):
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"could not load image: {image_path}")
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    plant_list = scan_plants(image_path, lower_green=lower_green, upper_green=upper_green)
    mask = cv2.inRange(hsv, lower_green, upper_green)

    heighest_pixel = None
    for plant in plant_list:
        mask = cv2.bitwise_and(mask, plant["mask"])
        ys, xs = np.where(plant["mask"] > 0)
        if len(ys) == 0:
            continue
        if (heighest_pixel is None) or (np.min(ys) < heighest_pixel[1]):
            heighest_index = np.argmin(ys)
            heighest_pixel = (int(xs[heighest_index]), int(ys[heighest_index]))
    return heighest_pixel   
    ys, xs = np.where(mask > 0)
    if len(ys) == 0:
        raise ValueError("No green pixels found in the image within the specified HSV range.")
    else:
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
DEBUGGING / PLOTTING HELPERS
- this is ussed to plot the results for debugging purposes
"""

def plot_image(image_path, out_path, qr_list=None, april_list=None, plant_list=None, heighest_green_pixel=None, estimated_height=None):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"could not load image: {image_path}")    
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    W,H = graph_rgb.shape[1], graph_rgb.shape[0]
    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')           
        
    if qr_list is not None:
        for qr in qr_list:
            corners = qr["corners"]
            tl = corners["top_left"]
            tr = corners["top_right"]
            br = corners["bottom_right"]
            bl = corners["bottom_left"]
            for corner, color in zip([tl, tr, br, bl], ['red', 'green', 'blue', 'yellow']):
                x, y = corner
                ax.add_patch(plt.Circle((x, y), 10, color=color, fill=True))
                #draw a verticle line at point x
                #print(f"Plotted corner at ({x}, {y}) with color {color}")
            
    if april_list is not None:
        for april in april_list:
            corners = april["corners"]
            tl = corners["top_left"]
            tr = corners["top_right"]
            br = corners["bottom_right"]
            bl = corners["bottom_left"]
            for corner, color in zip([tl, tr, br, bl], ['red', 'green', 'blue', 'yellow']):
                x, y = corner
                ax.add_patch(plt.Circle((x, y), 10, color=color, fill=True))
                #print(f"Plotted corner at ({x}, {y}) with color {color}")
    if plant_list is not None:
        for plant in plant_list:
            mask = plant["mask"]
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                contour = contour.squeeze()
                ax.plot(contour[:, 0], contour[:, 1], color='lime', linewidth=2)
        
            #print(f"Plotted plant contour with {len(contour)} points")
    if heighest_green_pixel is not None:    
        x, y = heighest_green_pixel
        ax.add_patch(plt.Circle((x, y), 5, color='blue', fill=True))
        #print(f"Plotted heighest green pixel at ({x}, {y}) with color blue")
    
    if estimated_height is not None:
        ax.set_title(f"Estimated Height: {100*estimated_height:.2f} cm")
            
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)
    


"""
ESTIMATORS
- functions that estimate height using the scanners and getters
"""

def estimated_height(image_path, reference="apriltag", heighest_green_pixel=None, auxilary_images=[], scale_units_m=.070,bias_correction_m=1.00,bias_correction_b=0.0):
    if reference=="apriltag":
        reference_info = scan_apriltags(image_path)[0]
    elif reference == "qrcode":
        reference_info = scan_qrtags(image_path)[0]
    else:
        raise ValueError(f"unknown reference type: {reference}")
    if heighest_green_pixel is None:
        heighest_green_pixel = get_heighest_green_pixel(image_path)

    equation_top = get_equation_of_line(
        reference_info["corners"]["top_left"],
        reference_info["corners"]["top_right"]
    )
    # here I calculate the equation of the line passing through the bottom points of the april tag
    equation_bottom = get_equation_of_line(
        reference_info["corners"]["bottom_left"],
        reference_info["corners"]["bottom_right"]
    )
    # to estimate the height, I find the fraction of the distance between the top and bottom lines
    # where the heighest green pixel is located. I then multiply this fraction by the known height of the april tag
    fractional_height = fractional_height_between_lines(
        equation_top,
        equation_bottom,
        heighest_green_pixel
    )
    
    return (scale_units_m * fractional_height)*bias_correction_m + bias_correction_b

