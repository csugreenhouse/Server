import apriltag
import argparse
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import psycopg2

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


def get_heighest_green_pixel(image_path):
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"could not load image: {image_path}")
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_green = (35, 120, 60)
    upper_green = (85, 255, 255)

    mask = cv2.inRange(hsv, lower_green, upper_green)

    #display the mask for debugging purposes
    #cv2.imshow("Green Mask", mask)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
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
DEBUGGING / PLOTTING HELPERS
- this is ussed to plot the results for debugging purposes
"""

def plot_image(image_path, out_path, qr_list=None, april_list=None, heighest_green_pixel=None, estimated_height=None):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"could not load image: {image_path}")    
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

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

def estimated_height(image_path, auxilary_images=[], scale_units_m=.075,bias_correction_m=0.0):
    heighest_green_pixel = get_heighest_green_pixel(image_path)
    apriltag_info = scan_apriltags(image_path)[0]
    
    equation_top = get_equation_of_line(
        apriltag_info["corners"]["top_left"],
        apriltag_info["corners"]["top_right"]
    )
    # here I calculate the equation of the line passing through the bottom points of the april tag
    equation_bottom = get_equation_of_line(
        apriltag_info["corners"]["bottom_left"],
        apriltag_info["corners"]["bottom_right"]
    )
    # to estimate the height, I find the fraction of the distance between the top and bottom lines
    # where the heighest green pixel is located. I then multiply this fraction by the known height of the april tag
    fractional_height = fractional_height_between_lines(
        equation_top,
        equation_bottom,
        heighest_green_pixel
    )
    
    return scale_units_m * fractional_height + bias_correction_m

