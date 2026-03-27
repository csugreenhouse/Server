import sys
sys.path.append('/srv/samba/Server')

import database.database_util as db_util
import pandas as pd
import cv2

import numpy as np
import matplotlib.pyplot as plt

def generate_height_graph_for_plant_id(plant_id):
    conn = db_util.open_connection_to_database()
    results = db_util.get_all_heights_for_plant_id(conn, plant_id)
    db_util.query_to_CSV_file(results, f"query_csvs/height_log_plant_id_{plant_id}.csv")
    db_util.close_connection_to_database(conn)
    df = pd.read_csv(f"query_csvs/height_log_plant_id_{plant_id}.csv")
    plt.plot(df["measured_at"], df["height_units_m"], "b.")
    plt.xlabel("Measured At")
    plt.ylabel("Height (m)")
    plt.title("Plant Height Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

generate_height_graph_for_plant_id(3)