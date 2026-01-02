import cv2
import numpy as np
import apriltag
import warnings

"""
utils for scanning AprilTags, QRTags, and green blobs in images.
scan_apriltags(image) -> list of apriltag dicts
scan_qrtags(image) -> list of qrtag dicts
scan_green_blobs(image, color_bounds, open_kernel_size, close_kernel_size, minimum_area_pixels, maximum_area_pixels) -> list of green blob dicts
"""
def parse_qr_data(qr_data_str):
    """
    Parses a QR code data string into a dictionary.
    The QR code data string is expected to be in the format:
    "should be {'c': 'value', 's': 'value', 'b': 'value'}"
    in refence to color (c), scale (s), and bias (b).
    Returns a dictionary with the parsed key-value pairs.
    """
    try:
        # Evaluate the string to convert it into a dictionary
        qr_data_dict = eval(qr_data_str)
        if not isinstance(qr_data_dict, dict):
            raise ValueError("QR data is not a dictionary")
        return qr_data_dict['c'], qr_data_dict.get['s'], qr_data_dict.get['b'],
    except Exception as e:
        raise ValueError(f"Failed to parse QR data: {e}")
    
def scan_apriltags(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    options = apriltag.DetectorOptions(families="tag25h9")
    detector = apriltag.Detector(options)
    results = detector.detect(gray)
    
    DECISION_MARGIN = 40.0

    valid_tags = []

    for tag in results:
        #print(f"TAG ID {tag.tag_id} with decision margin {tag.decision_margin}")
        if (tag.decision_margin>DECISION_MARGIN):
            # color_bounds, scale_units_m, bias_units_m = parse_qr_data(str(tag.tag_id))
            tag = {
                    "data": tag.tag_id,
                    "tag_type": "apriltag",
                    "center": tuple(tag.center),
                    "corners": {
                        "top_left": tuple(tag.corners[0]),
                        "top_right": tuple(tag.corners[1]),
                        "bottom_right": tuple(tag.corners[2]),
                        "bottom_left": tuple(tag.corners[3]),
                    },
                }
            
            valid_tags.append(tag)

    if (len(valid_tags)==0):
        if (len(results)!=0):
            raise ValueError(f"No Valid april tag has been detected, but a non valid one has been found")
        else:
            raise ValueError(f"No april tags at all have been found")
  
    if (len(valid_tags)>1):
        warnings.warn(f"Multiple valid AprilTags detected ({len(valid_tags)})", RuntimeWarning)
    return valid_tags

def get_first_april_tag_info(april_tag_list):
    return april_tag_list[0]

def scan_qrtags(image):  
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
        # data should be in form of a dictionary encoded as a string
        
        tag = {
            "data": data,
            "tag_type": "qrtag",
            "center": center,
            "corners": {
                "top_left":     tuple(points[0]),
                "top_right":    tuple(points[1]),
                "bottom_right": tuple(points[2]),
                "bottom_left":  tuple(points[3]),
            },
        }
        valid_tags.append(tag)

    if len(valid_tags) == 0:
        raise ValueError("No valid QR tags have been found")

    if len(valid_tags) > 1:
        warnings.warn(
            f"Multiple valid QR Tags detected ({len(valid_tags)})",
            RuntimeWarning
        )
    return valid_tags

def get_first_qr_tag_info(qr_tag_list):
    return qr_tag_list[0]

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

def scan_reference_tags(image, camera_parameters):
    april_tag_list = scan_apriltags(image)
    reference_tags = make_reference_tags(camera_parameters, april_tag_list)