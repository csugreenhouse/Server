import cv2
import apriltag
import warnings
import numpy as np

camera_parameters = {
    "focal_length_mm": 3.6,
    "sensor_height_mm": 2.2684,
    "sensor_width_mm": 3.590
}

card_dimensions_m = {
    "width_m": 0.068,
    "height_m": 0.068
}

def get_offsets(image, reference_tag):
    fx = (camera_parameters["focal_length_mm"] / camera_parameters["sensor_width_mm"]) * image.shape[1]
    fy = (camera_parameters["focal_length_mm"] / camera_parameters["sensor_height_mm"]) * image.shape[0]
    width_card_m = card_dimensions_m["width_m"]
    height_card_m = card_dimensions_m["height_m"]
    width_card_pixel_top =  np.linalg.norm(np.array(reference_tag['corners']['top_right']) - np.array(reference_tag['corners']['top_left']))
    width_card_pixel_bottom =  np.linalg.norm(np.array(reference_tag['corners']['bottom_right']) - np.array(reference_tag['corners']['bottom_left']))
    width_card_pixel = (width_card_pixel_top + width_card_pixel_bottom) / 2
    height_card_pixel_left = np.linalg.norm(np.array(reference_tag['corners']['top_left']) - np.array(reference_tag['corners']['bottom_left']))
    height_card_pixel_right = np.linalg.norm(np.array(reference_tag['corners']['top_right']) - np.array(reference_tag['corners']['bottom_right']))
    height_card_pixel = (height_card_pixel_left + height_card_pixel_right) / 2
    center_x_image = image.shape[1] / 2
    center_y_image = image.shape[0] / 2
    center_x_tag = reference_tag['center'][0]
    center_y_tag = reference_tag['center'][1]
    displacement_z = (fx * width_card_m) / width_card_pixel
    displacement_x = (center_x_tag - center_x_image) * (fx * width_card_m) / (width_card_pixel * fx)
    displacement_y = (center_y_tag - center_y_image) * (fy * height_card_m) / (height_card_pixel * fy)
    displacement_d = np.sqrt(displacement_z**2 + displacement_x**2 + displacement_y**2)
    return displacement_d, displacement_z,displacement_x, displacement_y

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
            tag = {
                    "data": tag.tag_id,
                    "center": tuple(tag.center),
                    "corners": {
                        "top_left": tuple(tag.corners[0]),
                        "top_right": tuple(tag.corners[1]),
                        "bottom_right": tuple(tag.corners[2]),
                        "bottom_left": tuple(tag.corners[3]),
                    }
                }
            tag["displacements"] = {}
            tag["displacements"]["d"], tag["displacements"]["z"], tag["displacements"]["x"], tag["displacements"]["y"] = get_offsets(image, tag)
            valid_tags.append(tag)

    if (len(valid_tags)==0):
        if (len(results)!=0):
            raise ValueError(f"No Valid april tag has been detected, but a non valid one has been found")
        else:
            raise ValueError(f"No april tags at all have been found")
  
    if (len(valid_tags)>1):
        warnings.warn(f"Multiple valid AprilTags detected ({len(valid_tags)})", RuntimeWarning)
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
        tag = {
            "data": data,
            "center": center,
            "corners": {
                "top_left":     tuple(points[0]),
                "top_right":    tuple(points[1]),
                "bottom_right": tuple(points[2]),
                "bottom_left":  tuple(points[3]),
            }
        }
        tag["displacements"] = {}
        tag["displacements"]["d"], tag["displacements"]["z"], tag["displacements"]["x"], tag["displacements"]["y"] = get_offsets(image, tag)
        valid_tags.append(tag)

    if len(valid_tags) == 0:
        raise ValueError("No valid QR tags have been found")

    if len(valid_tags) > 1:
        warnings.warn(
            f"Multiple valid QR Tags detected ({len(valid_tags)})",
            RuntimeWarning
        )
    return valid_tags