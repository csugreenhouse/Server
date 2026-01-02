import cv2
import numpy as np
import requests
from pathlib import Path

def get_image_from_camera_parameters(camera_parameters):
    camera_ip = camera_parameters["ip_address"]
    camera_id = camera_parameters["camera_id"]
    camera_url = f"http://{camera_ip}/capture"
    try:
        response = requests.get(camera_url,timeout=10)
        response.raise_for_status()
        image = response.content
        return cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
    except requests.exceptions.RequestException as e:
        ConnectionRefusedError(f"Camera {camera_id}'s ip {camera_url} failed")
        return None