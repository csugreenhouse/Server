import cv2
import numpy as np
import sys 

sys.path.append('/srv/samba/Server')


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

def open_connection_to_database():
    with open("/srv/samba/Server/plant_requests/utils/secrets_util.json") as f:
        secrets = json.load(f)["database_util"]
    try:
        conn = psycopg2.connect(
            host=secrets["PG_HOST"],
            dbname=secrets["PG_DATABASE"],
            user=secrets["PG_USER"],
            password=secrets["PG_PASSWORD"]
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
    
def close_connection_to_database(conn):
    if conn:
        conn.close() 
        
def get_tag_information_from_database(conn,tag_id):
    tag_query_results = execute_query(conn,f"select * from tag where tag_id = {tag_id}")
    return tag_query_results

def execute_query(conn,query):
    try:
        cur = conn.cursor()
        cur.execute(query)
        if cur.description is not None:
            results = cur.fetchall()
        else:
            results = None
        conn.commit()
        cur.close()
        return results
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        print("Query executed")

"""
def can_connect_to_database():
    with open("/srv/samba/Server/plant_requests/utils/secrets_util.json") as f:
        secrets = json.load(f)["database_util"]
    try:
        conn = psycopg2.connect(
            host=secrets["PG_HOST"],
            dbname=secrets["PG_DATABASE"],
            user=secrets["PG_USER"],
            password=secrets["PG_PASSWORD"]
        )
        conn.close()
        return True
    except Exception:
        return False
    


def execute_query(query):
    with open("/srv/samba/Server/plant_requests/utils/secrets_util.json") as f:
        secrets = json.load(f)["database_util"]
    try:
        conn = psycopg2.connect(
            host=secrets["PG_HOST"],
            dbname=secrets["PG_DATABASE"],
            user=secrets["PG_USER"],
            password=secrets["PG_PASSWORD"]
        )
        cur = conn.cursor()
        cur.execute(query)
        if cur.description is not None:
            results = cur.fetchall()
        else:
            results = None
        conn.commit()
        cur.close()
        return results
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()   

def get_tag_information_from_database(tag_id):
    tag_query_results = execute_query(f"select * from tag_to_plant where tag_id = {tag_id}")
    return tag_query_results

def get_reference_tags_from_image_and_database(image, camera_parameters):
    return None

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
# GETTERS INTO DATABASE
def get_tag_scale_from_database(tag_id):
    return execute_query(f"select scale_units_m from tag where tag_id='{tag_id}'")[0][0]

def get_tag_views_from_database(tag_id):
    results = execute_query(generate_tag_view_information(tag_id))
    views = []
    for result in results:
        view = {
            "plant_id":result[0],
            "bias_units_m":result[1],
            "request_type":result[2],
            "image_bound_upper":result[3],
            "image_bound_lower":result[4],
            "lower_color_bound": (result[5],result[6],result[7]),
            "upper_color_bound": (result[8],result[9],result[10])
        } 
        views.append(view)
    return views

def generate_tag_view_information(tag_id):
    query = "SELECT ttp.plant_id, ttp.bias_units_m, ttp.request_type, ttp.image_bound_upper, ttp.image_bound_lower, "
    query += "s.lower_color_bound_hue,s.upper_color_bound_value,s.lower_color_bound_saturation, " 
    query += "s.upper_color_bound_hue,s.upper_color_bound_value,s.lower_color_bound_saturation " 
    query += "FROM tag_to_plant ttp JOIN plant p " 
    query += "ON p.plant_id = ttp.plant_id " 
    query += "JOIN species s " 
    query += "ON s.species_id = p.species_id " 
    query +=f"WHERE ttp.tag_id = {tag_id};" 
    return query





# INSERTS INTO DATABASE 
def insert_species_in_database(scientific_name, color_bounds):
    return execute_query(generate_insert_species_query_in_database(scientific_name,color_bounds))

def generate_insert_species_query_in_database(scientific_name, color_bounds):
    query = "insert into species (scientific_name, " 
    query += "upper_color_bound_hue, upper_color_bound_value, upper_color_bound_saturation, " 
    query += "lower_color_bound_hue, lower_color_bound_value, lower_color_bound_saturation) " 
    query += f"values ('{scientific_name}'," 
    query += f"{color_bounds[0][0]}, {color_bounds[0][1]}, {color_bounds[0][2]}, "
    query += f"{color_bounds[1][0]}, {color_bounds[1][1]}, {color_bounds[1][2]} );"
    return query

def insert_plant_in_database(plant_id,scientific_name):
    return execute_query(generate_insert_plant_query_in_database(plant_id,scientific_name))

def generate_insert_plant_query_in_database(plant_id,scientific_name):
    query = f"insert into plant (plant_id, species_id) select {plant_id}, species_id "
    query += f"FROM species WHERE scientific_name ='{scientific_name}'"
    return query

def insert_tag_to_plant_in_database(tag_id,plant_id,scale_units_m,bias_units_m,request_type):
    return execute_query(generate_insert_tag_to_plant_in_database(tag_id,plant_id,scale_units_m,bias_units_m,request_type))

def generate_insert_tag_to_plant_in_database(tag_id,plant_id,scale_units_m,bias_units_m,request_type):
    query = f"insert into tag_to_plant (tag_id,plant_id,scale_units_m,bias_units_m,request_type)"
    query += f"VALUES ({tag_id},{plant_id},{scale_units_m},{bias_units_m},'{request_type}')"
    return query
    
"""


