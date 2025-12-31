import numpy as np
def get_offsets(image, camera_parameters, reference_tag):
    fx = (camera_parameters["focal_length_mm"] / camera_parameters["sensor_width_mm"]) * image.shape[1]
    fy = (camera_parameters["focal_length_mm"] / camera_parameters["sensor_height_mm"]) * image.shape[0]
    width_card_m = reference_tag.get("scale_units_m", 0.065)
    height_card_m = reference_tag.get("scale_units_m", 0.065)
    width_card_pixel_top = np.linalg.norm(np.array(reference_tag['corners']['top_right']) - np.array(reference_tag['corners']['top_left']))
    width_card_pixel_bottom = np.linalg.norm(np.array(reference_tag['corners']['bottom_right']) - np.array(reference_tag['corners']['bottom_left']))
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
    return displacement_d, displacement_z, displacement_x, displacement_y