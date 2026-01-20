import cv2
import numpy as np
import apriltag
import warnings
import sys
sys.path.append('/srv/samba/Server')

import plant_requests.utils.database_util as database


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
  
    return valid_tags

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

    return valid_tags

def scan_reference_tags(image, camera_parameters):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    options = apriltag.DetectorOptions(families="tag25h9")
    detector = apriltag.Detector(options)
    results = detector.detect(gray)
    
    DECISION_MARGIN = 40.0

    valid_tags = []

    for tag in results:
        #print(f"TAG ID {tag.tag_id} with decision margin {tag.decision_margin}")
        if (tag.decision_margin>DECISION_MARGIN):
            tag_id = tag.tag_id
            scale = database.get_tag_scale_from_database(tag_id)
            views = database.get_tag_views_from_database(tag_id)
            corners = {
                        "top_left": tuple(tag.corners[0]),
                        "top_right": tuple(tag.corners[1]),
                        "bottom_right": tuple(tag.corners[2]),
                        "bottom_left": tuple(tag.corners[3]),
                      }
            center = tuple(tag.center)
            displacement_d, displacement_z, displacement_x, displacement_y = calculate_displacement(camera_parameters, scale, center, corners )
            # color_bounds, scale_units_m, bias_units_m = parse_qr_data(str(tag.tag_id))
            tag = {
                    "data": tag.tag_id,
                    "tag_type": "referencetag",
                    "center": center,
                    "corners": corners,
                    "scale_units_m": scale,
                    "views": views
                }
            valid_tags.append(tag)    
            '''"views": [{"plant_id":
                        "bias_units_m":
                        "image_bound_upper":
                        "image_bound_lower":
                        "color_bound_upper":
                        "color_bound_lower":
                        "request_type":}]'''
            
    if (len(valid_tags)==0):
        if (len(results)!=0):
            raise ValueError(f"No Valid april tag has been detected, but a non valid one has been found")
        else:
            raise ValueError(f"No april tags at all have been found")
  
    return valid_tags





def make_reference_tag(camera_parameters, april_tag):

    reference_tag = add_height_estimation_info_to_tag(april_tag, camera_parameters)
    reference_tag = add_calculated_displacement_info_to_tag(camera_parameters, reference_tag)
    return reference_tag

def make_reference_tags(camera_parameters, april_tag_list):
    reference_tags = []
    for april_tag in april_tag_list:
        reference_tag = make_reference_tag(camera_parameters, april_tag)
        reference_tags.append(reference_tag)
    return reference_tags


def get_reference_tags_from_image(image, camera_parameters):
    april_tags = scan_apriltags(image)
    reference_tags = make_reference_tags(camera_parameters, april_tags)
    return reference_tags


def add_height_estimation_info_to_tag(april_tag, camera_parameters):
    queried_info = database.get_tag_information_from_database(april_tag, camera_parameters)
    april_tag["scale_units_m"] = queried_info["scale_units_m"]
    april_tag["bias_units_m"] = queried_info["bias_units_m"]
    april_tag["color_bounds"] = queried_info["color_bounds"]
    april_tag["plant_id"] = queried_info["plant_id"]
    april_tag["plant_bounds"] = queried_info["plant_bounds"]
    april_tag["request_type"] = queried_info["request_type"]
    return april_tag
    
def calculate_displacement(camera_parameters, scale_units_m, center, corners):
    width = camera_parameters["width"]
    height = camera_parameters["height"]
    fx = float((camera_parameters["focal_length_mm"] / camera_parameters["sensor_width_mm"]) * width)
    fy = float((camera_parameters["focal_length_mm"] / camera_parameters["sensor_height_mm"]) * height)
    width_card_m = float(scale_units_m)
    height_card_m = float(scale_units_m)
    width_card_pixel_top = np.linalg.norm(np.array(corners['top_right']) - np.array(corners['top_left']))
    width_card_pixel_bottom = np.linalg.norm(np.array(corners['bottom_right']) - np.array(corners['bottom_left']))
    width_card_pixel = float((width_card_pixel_top + width_card_pixel_bottom) / 2)
    height_card_pixel_left = np.linalg.norm(np.array(corners['top_left']) - np.array(corners['bottom_left']))
    height_card_pixel_right = np.linalg.norm(np.array(corners['top_right']) - np.array(corners['bottom_right']))
    height_card_pixel = float((height_card_pixel_left + height_card_pixel_right) / 2)
    center_x_image = width / 2
    center_y_image = height / 2
    center_x_tag = center[0]
    center_y_tag = center[1]
    displacement_z = (fx * width_card_m) / width_card_pixel
    displacement_x = (center_x_tag - center_x_image) * (fx * width_card_m) / (width_card_pixel * fx)
    displacement_y = (center_y_tag - center_y_image) * (fy * height_card_m) / (height_card_pixel * fy)
    displacement_d = np.sqrt(displacement_z**2 + displacement_x**2 + displacement_y**2)
    return displacement_d, displacement_z, displacement_x, displacement_y

def add_calculated_displacement_info_to_tag(camera_parameters, reference_tag):
    scale = reference_tag["scale_units_m"]
    center = reference_tag["center"]
    corners = reference_tag["corners"]

    displacement_d, displacement_z, displacement_x, displacement_y = calculate_displacement(camera_parameters, scale, center, corners)
    reference_tag['displacements'] = {
        'd': displacement_d,
        'z': displacement_z,
        'x': displacement_x,
        'y': displacement_y
    }
    return reference_tag
