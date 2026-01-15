import cv2
import numpy as np
import sys 

sys.path.append('/srv/samba/Server')

import plant_requests.utils.reference_tag_util as scanner

plastic_color_bounds = ((30, 60, 30),(70, 255, 200))
lettuce_color_bounds = ((30, 35, 30),(75, 255, 255))

april_tag_database = [
    {"id": 1, "scale_units_m": 0.065, "bias_units_m": 0.0,"color_bounds": plastic_color_bounds, "plant_id": 1, "plant_bounds": (0,1),"request_type": "height"},
    {"id": 2,"scale_units_m": 0.065, "bias_units_m": 0.0, "color_bounds": lettuce_color_bounds, "plant_id": 2, "plant_bounds": (0,1), "request_type": "height"},
    {"id": 3, "scale_units_m": 0.065, "bias_units_m": 0.0, "color_bounds": lettuce_color_bounds, "plant_id": 3, "plant_bounds": (0,1), "request_type": "height"},
]

camera_database = [
    {
        "camera_id": 1,
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.168.0.11"
    },
    {
        "camera_id": 2,
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.168.0.12"
    },
    {
        "camera_id": 3,
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.168.0.13"
    },
    {
        "camera_id": 4,
        "width": 1024,
        "height": 768,
        "focal_length_mm": 3.6,
        "sensor_height_mm": 2.2684,
        "sensor_width_mm": 3.590,
        "ip_address": "192.168.0.14"
    }
]

import psycopg2
import os
import json

def execute_query(query):
    with open("/srv/samba/Server/plant_requests/utils/secrets_util.json") as f:
        secrets = json.load(f)["database_util"]

    conn = psycopg2.connect(
        host=secrets["PG_HOST"],
        dbname=secrets["PG_DATABASE"],
        user=secrets["PG_USER"],
        password=secrets["PG_PASSWORD"]
    )
    try:
        cur = conn.cursor()
        cur.execute(query)

        results = cur.fetchall()
        conn.commit()
        cur.close()
        return results
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()    


def get_available_camera_parameters_from_database():
    camera_query_results = execute_query("select * from camera")
    available_camera_parameters = []
    for camera_result in camera_query_results:
        camera_parameters = {
            "camera_id": camera_result[0],
            "width": camera_result[1],
            "height": camera_result[2],
            "focal_length_mm": camera_result[3],
            "sensor_height_mm": camera_result[4],
            "sensor_width_mm": camera_result[5],
            "ip_address": camera_result[6]
        }
        available_camera_parameters.append(camera_parameters)
    return available_camera_parameters



