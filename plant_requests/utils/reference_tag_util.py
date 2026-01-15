import cv2
import numpy as np
import apriltag
import warnings

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

def get_reference_tags_from_image(image, camera_parameters):
    april_tags = scan_apriltags(image)
    reference_tags = make_reference_tags(camera_parameters, april_tags)
    return reference_tags
    
   
def query_height_estimation_parameters(april_tag, camera_parameters):
    queried_info = query_april_tag_info(april_tag["data"])
    return queried_info

def add_height_estimation_info_to_tag(april_tag, camera_parameters):
    queried_info = query_height_estimation_parameters(april_tag, camera_parameters)
    april_tag["scale_units_m"] = queried_info["scale_units_m"]
    april_tag["bias_units_m"] = queried_info["bias_units_m"]
    april_tag["color_bounds"] = queried_info["color_bounds"]
    april_tag["plant_id"] = queried_info["plant_id"]
    april_tag["plant_bounds"] = queried_info["plant_bounds"]
    april_tag["request_type"] = queried_info["request_type"]
    return april_tag
    
def calculate_displacement(camera_parameters, reference_tag):
    width = camera_parameters["width"]
    height = camera_parameters["height"]
    fx = (camera_parameters["focal_length_mm"] / camera_parameters["sensor_width_mm"]) * width
    fy = (camera_parameters["focal_length_mm"] / camera_parameters["sensor_height_mm"]) * height
    width_card_m = reference_tag.get("scale_units_m", 0.065)
    height_card_m = reference_tag.get("scale_units_m", 0.065)
    width_card_pixel_top = np.linalg.norm(np.array(reference_tag['corners']['top_right']) - np.array(reference_tag['corners']['top_left']))
    width_card_pixel_bottom = np.linalg.norm(np.array(reference_tag['corners']['bottom_right']) - np.array(reference_tag['corners']['bottom_left']))
    width_card_pixel = (width_card_pixel_top + width_card_pixel_bottom) / 2
    height_card_pixel_left = np.linalg.norm(np.array(reference_tag['corners']['top_left']) - np.array(reference_tag['corners']['bottom_left']))
    height_card_pixel_right = np.linalg.norm(np.array(reference_tag['corners']['top_right']) - np.array(reference_tag['corners']['bottom_right']))
    height_card_pixel = (height_card_pixel_left + height_card_pixel_right) / 2
    center_x_image = width / 2
    center_y_image = height / 2
    center_x_tag = reference_tag['center'][0]
    center_y_tag = reference_tag['center'][1]
    displacement_z = (fx * width_card_m) / width_card_pixel
    displacement_x = (center_x_tag - center_x_image) * (fx * width_card_m) / (width_card_pixel * fx)
    displacement_y = (center_y_tag - center_y_image) * (fy * height_card_m) / (height_card_pixel * fy)
    displacement_d = np.sqrt(displacement_z**2 + displacement_x**2 + displacement_y**2)
    return displacement_d, displacement_z, displacement_x, displacement_y

def add_calculated_displacement_info_to_tag(camera_parameters, reference_tag):
    displacement_d, displacement_z, displacement_x, displacement_y = calculate_displacement(camera_parameters, reference_tag)
    reference_tag['displacements'] = {
        'd': displacement_d,
        'z': displacement_z,
        'x': displacement_x,
        'y': displacement_y
    }
    return reference_tag

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

def scan_reference_tags(image, camera_parameters):
    april_tag_list = scan_apriltags(image)
    reference_tags = make_reference_tags(camera_parameters, april_tag_list)