import cv2
import numpy as np

plastic_color_bounds = ((30, 60, 30),(70, 255, 200))
lettuce_color_bounds = ((30, 35, 30),(75, 255, 255))

april_tag_database = {
    1: {"scale_units_m": 0.065, "bias_units_m": 0.0,"color_bounds": plastic_color_bounds, "plant_id": 1, "plant_bounds": (0,1),"request_type": "height"},
    2: {"scale_units_m": 0.065, "bias_units_m": 0.0, "color_bounds": lettuce_color_bounds, "plant_id": 2, "plant_bounds": (0,1), "request_type": "height"},
    3: {"scale_units_m": 0.065, "bias_units_m": 0.0, "color_bounds": lettuce_color_bounds, "plant_id": 3, "plant_bounds": (0,1), "request_type": "height"},
}

camera_database = {
    1: {
        "camera_id": 1,
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.168.0.11"
    },
    2: {
        "camera_id": 2,
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.168.0.12"
    }
}

def qeury_camera_parameters(camera_number):
    if camera_number in camera_database:
        return camera_database[camera_number]
    else:
        raise ValueError(f"Camera number {camera_number} not found in database")
    
def query_height_estimation_parameters(april_tag, camera_parameters):
    queried_info = get_april_tag_info(april_tag["data"])
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

