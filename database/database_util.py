import cv2
import numpy as np
import sys 

sys.path.append('/srv/samba/Server')

import psycopg2
import os
import json

def get_available_camera_parameters_from_database(conn):
    query = (
        "SELECT "
        "  camera_id, "
        "  width, "
        "  height, "
        "  focal_length_mm, "
        "  sensor_height_mm, "
        "  sensor_width_mm, "
        "  ip_address "
        "FROM camera;"
    )
    
    results = execute_query(conn, query)
    camera_parameter_list = []
    for row in results:
        camera_parameter = {
            "camera_id": row[0],
            "width": row[1],
            "height": row[2],
            "focal_length_mm": float(row[3]),
            "sensor_height_mm": float(row[4]),
            "sensor_width_mm": float(row[5]),
            "ip_address": row[6]
        }
        camera_parameter_list.append(camera_parameter)

    return camera_parameter_list

def open_connection_to_test_database():
    try:
        conn = psycopg2.connect(
            dbname="test_greenhouse",
            user="greenhouse_test_user",
            password="greenhouse_test_pass",
            host="localhost",
            port=5432,
        )
        return conn
    except Exception as e:
        print(f"Test database connection error: {e}")
        return None

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

def get_tag_views_from_database(conn, tag_id):
    
    query = (
        "SELECT "
        "v.plant_id, "
        "v.tag_id, "
        "v.view_type, "
        "v.image_bound_x_high, "
        "v.image_bound_x_low, "
        "v.minimum_area_pixels AS minimum_area_pixels, "
        "s.species_id, "
        "s.scientific_name, "
        "s.lower_hsv[1], "
        "s.lower_hsv[2], "
        "s.lower_hsv[3], "
        "s.upper_hsv[1], "
        "s.upper_hsv[2],  "
        "s.upper_hsv[3], "
        "hv.bias_units_m AS height_bias_units_m "
        "FROM \"view\" v "
        "JOIN plant p ON p.plant_id = v.plant_id "
        "JOIN species s ON s.species_id = p.species_id "
        "LEFT JOIN height_view hv ON hv.view_id = v.view_id "
        "LEFT JOIN width_view wv ON wv.view_id = v.view_id "
        "WHERE v.tag_id = %s "
        "AND v.current = TRUE;"
    )


    results = execute_query(conn, query, (tag_id,))
    view = []
    for results_row in results:
        temp_veiw = (
            {
            "species_id": results_row[6],
            "plant_id": results_row[0],
            "tag_id": results_row[1],
            "scientific_name": results_row[7],
            "view_type": results_row[2],
            "minimum_area_pixels": int(results_row[5]),
            "image_bounds_x_high": float(results_row[3]),
            "image_bounds_x_low": float(results_row[4]),
            "color_bound_lower": (
                float(results_row[8]),
                float(results_row[9]),
                float(results_row[10])
            ),
            "color_bound_upper": (
                float(results_row[11]),
                float(results_row[12]),
                float(results_row[13])
            ),
        })
        if results_row[2] == "height":
            temp_veiw["bias_units_m"] = float(results_row[14])
        view.append(temp_veiw)

    return view

def set_color_bounds_for_species_in_database(conn, species_id, color_bounds):
    query = (
        "UPDATE species "
        "SET lower_hsv = ARRAY[%s, %s, %s], "
        "    upper_hsv = ARRAY[%s, %s, %s] "
        "WHERE species_id = %s;"
    )
    
    params = (
        color_bounds[0][0],
        color_bounds[0][1],
        color_bounds[0][2],
        color_bounds[1][0],
        color_bounds[1][1],
        color_bounds[1][2],
        species_id
    )
    try:        
        execute_query(conn, query, params)
        #rint(f"Color bounds for species_id {species_id} updated successfully.")
    except Exception as e:        
        print(f"Error updating color bounds for species_id {species_id}: {e}")


def get_tag_scale_from_database(conn, tag_id):
    query = (
        "SELECT "
        "  t.scale_units_m "
        "FROM tag t "
        "WHERE t.tag_id = %s ;"
    )

    tag_query_results = execute_query(conn,query,(tag_id,))
    
    if tag_query_results and len(tag_query_results) > 0:
        return float(tag_query_results[0][0])
    else:
        raise ValueError(f"Tag ID {tag_id} not found in database.")

def execute_query(conn,query,params=None):
    try:
        cur = conn.cursor()
        cur.execute(query,params)
        if cur.description is not None:
            results = cur.fetchall()
        else:
            results = []
        conn.commit()
        cur.close()
        return results
    except Exception as e:
        conn.rollback()
        raise LookupError(f"Database error: {e}")
    finally:
        pass
    
def get_most_recent_height_for_plant_id(conn, plant_id):
    query = (
        "SELECT height_units_m, measured_at "
        "FROM height_log "
        "WHERE plant_id = %s "
        "ORDER BY measured_at DESC "
        "LIMIT 1;"
    )
    results = execute_query(conn, query, (plant_id,))
    if results and len(results) > 0:
        return {
            "height_units_m": float(results[0][0]),
            "measured_at": results[0][1]
        }
    else:
        return None
    
def get_all_heights_for_plant_id(conn, plant_id):
    query = (
        "SELECT height_units_m, measured_at "
        "FROM height_log "
        "WHERE plant_id = %s "
        "ORDER BY measured_at DESC;"
    )
    results = execute_query(conn, query, (plant_id,))
    height_logs = []
    for row in results:
        height_log = {
            "height_units_m": float(row[0]),
            "measured_at": row[1]
        }
        height_logs.append(height_log)
    return height_logs
    
def insert_height_response_into_database(conn, view_response,raw_file_path,processed_file_path, timestamp=None):
    query = (
        "INSERT INTO height_log (plant_id, height_units_m, raw_file_path, processed_file_path, measured_at) "
        "VALUES (%s, %s, %s, %s, %s);"
    )
    params = (
        view_response["plant_id"],
        float(view_response["estimated_height"]),
        raw_file_path,
        processed_file_path,
        timestamp.split('.')[0] if timestamp else 'NOW()'
    )
    try:
        execute_query(conn, query, params)
    except Exception as e:
        #still throw the error so that the calling function can handle it, but also print it here for debugging purposes
        print(f"Error inserting height log for plant_id {view_response['plant_id']}: {e}")
        raise MemoryError(f"Error inserting height log for plant_id {view_response['plant_id']}: {e}")
        

def insert_width_log_into_database(conn, plant_id, width_m, unproccessed_file_path, timestamp=None):
    query = (
        "INSERT INTO width_log (plant_id, width_m, file_path, measured_at) "
        "VALUES (%s, %s, %s, %s);"
    )
    params = (plant_id, width_m, unproccessed_file_path, timestamp or 'NOW()')
    try:
        execute_query(conn, query, params)
        print(f"Width log for plant_id {plant_id} inserted successfully.")
    except Exception as e:
        print(f"Error inserting width log for plant_id {plant_id}: {e}")

def query_to_CSV_file(results, CSVfile_path):
    import csv
    with open(CSVfile_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(results[0].keys())
        for entry in results:
            writer.writerow(entry.values())
        print(CSVfile_path)

def define_plant_x_bounds_in_database(conn, plant_id, xlow, xhigh):
    query = (
        "UPDATE view "
        "SET image_bound_x_high = %s,"
        "   image_bound_x_low = %s "
        "WHERE plant_id = %s;"
    )

    params = (
        xhigh,
        xlow,
        plant_id
    )
    
    try:        
        execute_query(conn, query, params)
        #rint(f"Color bounds for species_id {species_id} updated successfully.")
    except Exception as e:        
        print(f"Error updating x bounds for plant {plant_id}: {e}")