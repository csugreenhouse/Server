import cv2
import apriltag
import warnings
import numpy as np
from plant_requests.utils.camera_util import get_offsets

april_tag_database = {
    1: {"scale_units_m": 0.065, "bias_units_m": 0.0, "color_bounds": ((35, 120, 60), (85, 255, 255)), "request_type": "height"},
    2: {"scale_units_m": 0.065, "bias_units_m": 0.0, "color_bounds": ((35, 120, 60), (85, 255, 255)), "request_type": "height"},
    3: {"scale_units_m": 0.065, "bias_units_m": 0.0, "color_bounds": ((35, 120, 60), (85, 255, 255)), "request_type": "height"},
}

camera_database = {
    1: {
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.168.0.11"
    }
}

qr_tag_default_info = {
    "scale_units_m": 0.065, 
    "bias_units_m": 0.0,
    "color_bounds": ((35, 120, 60), (85, 255, 255)),
    "request_type": "height"
}

def get_camera_ip(camera_number):
    # Example function to retrieve camera IP based on camera number
    # This is temporary, will eventually que the database
    if camera_number in camera_database:
        return camera_database[camera_number]["ip_address"]
    else:
        raise ValueError(f"Camera number {camera_number} not found in database")

def get_camera_parameters(camera_number):
    # Example function to retrieve camera info based on camera number
    # This is temporary, will eventually que the database
    if camera_number in camera_database:
        return camera_database[camera_number]
    else:
        raise ValueError(f"Camera number {camera_number} not found in database")

def get_april_tag_info(april_tag_data):
    # Example function to retrieve AprilTag info based on ID
    # This is temporary, will eventually que the database
    april_tag_id = int(april_tag_data)
    if april_tag_id in april_tag_database:
        return april_tag_database[april_tag_id]
    else:
        raise ValueError(f"AprilTag ID {april_tag_id} not found in database")

def scan_apriltags(image, camera_parameters=get_camera_parameters(1)):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    options = apriltag.DetectorOptions(families="tag25h9")
    detector = apriltag.Detector(options)
    results = detector.detect(gray)
    
    DECISION_MARGIN = 40.0

    valid_tags = []

    for tag in results:
        #print(f"TAG ID {tag.tag_id} with decision margin {tag.decision_margin}")
        if (tag.decision_margin>DECISION_MARGIN):
            tag = {
                    "data": tag.tag_id,
                    "center": tuple(tag.center),
                    "corners": {
                        "top_left": tuple(tag.corners[0]),
                        "top_right": tuple(tag.corners[1]),
                        "bottom_right": tuple(tag.corners[2]),
                        "bottom_left": tuple(tag.corners[3]),
                    },
                    "color_bounds": get_april_tag_info(tag.tag_id)["color_bounds"],
                    "scale_units_m": get_april_tag_info(tag.tag_id)["scale_units_m"],
                    "bias_units_m": get_april_tag_info(tag.tag_id)["bias_units_m"]
                }
            tag["displacements"] = {}
            tag["displacements"]["d"], tag["displacements"]["z"], tag["displacements"]["x"], tag["displacements"]["y"] = get_offsets(image, camera_parameters,tag)
            valid_tags.append(tag)

    if (len(valid_tags)==0):
        if (len(results)!=0):
            raise ValueError(f"No Valid april tag has been detected, but a non valid one has been found")
        else:
            raise ValueError(f"No april tags at all have been found")
  
    if (len(valid_tags)>1):
        warnings.warn(f"Multiple valid AprilTags detected ({len(valid_tags)})", RuntimeWarning)
    return valid_tags

def scan_qrtags(image, camera_parameters=get_camera_parameters(1)):  
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
            "center": center,
            "corners": {
                "top_left":     tuple(points[0]),
                "top_right":    tuple(points[1]),
                "bottom_right": tuple(points[2]),
                "bottom_left":  tuple(points[3]),
            },
            "color_bounds": qr_tag_default_info["color_bounds"],  # default color bounds
            "scale_units_m": qr_tag_default_info["scale_units_m"],  # default scale
            "bias_units_m": qr_tag_default_info["bias_units_m"]   # default bias
        }
        tag["displacements"] = {}
        tag["displacements"]["d"], tag["displacements"]["z"], tag["displacements"]["x"], tag["displacements"]["y"] = get_offsets(image, camera_parameters, tag)
        valid_tags.append(tag)

    if len(valid_tags) == 0:
        raise ValueError("No valid QR tags have been found")

    if len(valid_tags) > 1:
        warnings.warn(
            f"Multiple valid QR Tags detected ({len(valid_tags)})",
            RuntimeWarning
        )
    return valid_tags