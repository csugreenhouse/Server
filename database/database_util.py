import cv2
import numpy as np
import sys 

sys.path.append('/srv/samba/Server')

import psycopg2
import os
import json

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
    """query = (
        "SELECT "
        "  v.plant_id, "
        "  v.view_type, "
        "  v.image_bound_upper, "
        "  v.image_bound_lower, "
        "  v.request_type AS view_request_type, "
        "  s.lower_color_bound_hue, "
        "  s.lower_color_bound_saturation, "
        "  s.lower_color_bound_value, "
        "  s.upper_color_bound_hue, "
        "  s.upper_color_bound_saturation, "
        "  s.upper_color_bound_value, "
        "  hv.bias_units_m AS height_bias_units_m "
        "FROM \"view\" v "
        "JOIN plant p ON p.plant_id = v.plant_id "
        "JOIN species s ON s.species_id = p.species_id "
        "LEFT JOIN height_view hv ON hv.view_id = v.view_id "
        "LEFT JOIN width_view wv ON wv.view_id = v.view_id "
        "WHERE v.tag_id = %s;"
    ) """
    
    query = (
        "SELECT "
        "v.plant_id, "
        "v.tag_id, "
        "v.view_type, "
        "v.image_bound_upper, "
        "v.image_bound_lower, "
        "s.scientific_name, "
        "s.lower_color_bound_hue, "
        "s.lower_color_bound_saturation, "
        "s.lower_color_bound_value, "
        "s.upper_color_bound_hue, "
        "s.upper_color_bound_saturation, "
        "s.upper_color_bound_value, "
        "hv.bias_units_m AS height_bias_units_m "
        "FROM \"view\" v "
        "JOIN plant p ON p.plant_id = v.plant_id "
        "JOIN species s ON s.species_id = p.species_id "
        "LEFT JOIN height_view hv ON hv.view_id = v.view_id "
        "LEFT JOIN width_view wv ON wv.view_id = v.view_id "
        "WHERE v.tag_id = %s;"
    )


    results = execute_query(conn, query, (tag_id,))
    view = []
    for results_row in results:
        temp_veiw = (
            {
            "plant_id": results_row[0],
            "tag_id": results_row[1],
            "scientific_name": results_row[5],
            "view_type": results_row[2],
            "image_bound_upper": float(results_row[3]),
            "image_bound_lower": float(results_row[4]),
            "color_bound_lower": (
                float(results_row[6]),
                float(results_row[7]),
                float(results_row[8])
            ),
            "color_bound_upper": (
                float(results_row[9]),
                float(results_row[10]),
                float(results_row[11])
            ),
        })
        if results_row[2] == "height":
            temp_veiw["bias_units_m"] = float(results_row[12])
        view.append(temp_veiw)

    return view


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
        print(f"Database error: {e}")
    finally:
        pass
    
