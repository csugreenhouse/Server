import database.database_util as db_util
import pandas as pd
import cv2

import numpy as np
import matplotlib.pyplot as plt

conn = db_util.open_connection_to_database()

results = db_util.get_all_heights_for_plant_id(conn, 3)

db_util.query_to_CSV_file(results, "height_log_plant_id_3.csv")

db_util.close_connection_to_database(conn)

df = pd.read_csv("height_log_plant_id_3.csv")
plt.plot(df["measured_at"], df["height_units_m"], "b.")
plt.xlabel("Measured At")
plt.ylabel("Height (m)")
plt.title("Plant Height Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
