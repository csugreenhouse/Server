import cv2
import numpy as np
import warnings
import sys
sys.path.append('/srv/samba/Server')
import apriltag
import plant_requests.utils.database_util as database


def scan_raw_tags(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    options = apriltag.DetectorOptions(families="tag25h9")
    detector = apriltag.Detector(options)
    results = detector.detect(gray)
    return results

def scan_apriltags(image):
    """
    Uses pupil_apriltags for detection but returns the SAME dict format you already use.
    """
    results = scan_raw_tags(image)

    DECISION_MARGIN = 40.0
    valid_tags = []

    for tag in results:
        #print(f"TAG ID {tag.tag_id} with decision margin {tag.decision_margin}")
        if (tag.decision_margin>DECISION_MARGIN):
            # color_bounds, scale_units_m, bias_units_m = parse_qr_data(str(tag.tag_id))
            # Expected order is typically TL, TR, BR, BL (matches your current indexing)
            tag = {
                "data": int(tag.tag_id),
                "tag_type": "apriltag",
                "center": tuple(np.asarray(tag.center, dtype=np.float32)),
                "corners": {
                    # RELATIVE TO THE IMAGE, Y INCREASES DOWNWARDS, THUS SWITCH THE ORDER
                    "top_left": tuple(tag.corners[0]),
                    "top_right": tuple(tag.corners[1]),
                    "bottom_right": tuple(tag.corners[2]),
                    "bottom_left": tuple(tag.corners[3]),
                },
            }
            valid_tags.append(tag)

    if len(valid_tags) == 0:
        if len(results) != 0:
            raise ValueError("No valid april tag has been detected, but a non valid one has been found")
        else:
            raise ValueError("No april tags at all have been found")
    return valid_tags

def scan_reference_tags(image, camera_parameters):
    results = scan_raw_tags(image)
    
    DECISION_MARGIN = 40.0

    reference_tags = []

    for raw_tag in results:
        #print(f"TAG ID {tag.tag_id} with decision margin {tag.decision_margin}")
        if (raw_tag.decision_margin>DECISION_MARGIN):
            reference_tag = make_reference_tag(raw_tag,camera_parameters)
            reference_tags.append(reference_tag)    
    
    if (len(reference_tags)==0):
        if (len(results)!=0):
            raise ValueError(f"No Valid april tag has been detected, but a non valid one has been found")
        else:
            raise ValueError(f"No april tags at all have been found")
  
    return reference_tags

def make_reference_tag(raw_april_tag, camera_parameters, scale=None, views=None):
    # pupil_apriltags detection fields:
    #   raw_april_tag.tag_id, raw_april_tag.corners, raw_april_tag.center
    tag_id = int(raw_april_tag.tag_id)

    scale = scale if scale is not None else database.get_tag_scale_from_database(tag_id)
    views = views if views is not None else database.get_tag_views_from_database(tag_id)

    # Ensure numpy arrays -> tuples (JSON safe)
    corners_np = np.asarray(raw_april_tag.corners, dtype=np.float32)
    center_np = np.asarray(raw_april_tag.center, dtype=np.float32)

    corners = {
        "top_left": tuple(corners_np[0]),
        "top_right": tuple(corners_np[1]),
        "bottom_right": tuple(corners_np[2]),
        "bottom_left": tuple(corners_np[3]),
    }
    
    center = tuple(center_np)

    displacement_d, displacement_z, displacement_x, displacement_y = calculate_displacement(
        camera_parameters, scale, center, corners
    )
    if not views:
        raise ValueError("Views is None or empty")

    for view in views:
        if view["image_bound_upper"] < view["image_bound_lower"]:
            raise ValueError("image bounds in a view are switched")

    tag = {
        "data": tag_id,
        "tag_type": "referencetag",
        "center": center,
        "corners": corners,
        "scale_units_m": float(scale),
        "displacements": {
            "d": float(displacement_d),
            "z": float(displacement_z),
            "x": float(displacement_x),
            "y": float(displacement_y),
        },
        "views": views,
    }
    return tag


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

def make_height_view(plant_id, image_bounds, color_bounds, bias_units_m):
    return {"plant_id": plant_id,
            "bias_units_m":bias_units_m,
            "image_bound_upper": image_bounds[1],
            "image_bound_lower": image_bounds[0],
            "color_bound_upper": color_bounds[1],
            "color_bound_lower": color_bounds[0],
            "request_type":'height',
            }