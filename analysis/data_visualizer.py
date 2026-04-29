import os
import sys
import time
sys.path.append('/srv/samba/Server')

import database.database_util as db_util
import pandas as pd
import cv2
import math

from datetime import timedelta

import numpy as np
import matplotlib.pyplot as plt

def date_str_to_timestamp(date_str_series):
    timestamps = []
    start_time = -np.inf
    for date_str in date_str_series[::-1]: # reverse the series to ensure the first timestamp is the earliest date
        timestamp = time.mktime(time.strptime(date_str[0:19], "%Y-%m-%d %H:%M:%S"))
        if timestamp is not None and len(timestamps) > 0:
            timestamps.append((timestamp - start_time) *
                              1/86400) # convert to days after the first timestamp
        else:
            timestamps.append(0)
            start_time = timestamp

    return timestamps



def cleanDataForGraphing(df):
    if len(df) < 200:
        windowval = len(df)/2
    else:
        windowval = 100

    #remove any rows with 0 height, as these are likely to be errors in the data
    dfnozeros = df[df["height_units_m"] > 0].reset_index(drop=True)
    zero_height_rows = df[df["height_units_m"] <= 0].reset_index(drop=True)

    #discard any range of rows where the rolling standard deviation is large as this is probably bad data.
    rolling_std = dfnozeros["height_units_m"].rolling(window=windowval, center=True).std()
    dfnostd = dfnozeros[rolling_std < 0.05].reset_index(drop=True)
    large_std_rows = dfnozeros[rolling_std >= 0.05].reset_index(drop=True)

    #remove any rows with unrealistic outliers, using a rolling median with a window to identify outliers
    rolling_median = dfnostd["height_units_m"].rolling(window=windowval, center=True).median()
    zscore = (dfnostd["height_units_m"] - rolling_median) / dfnostd["height_units_m"].rolling(window=windowval, center=True).std() # having a high zscore means the value is an outlier
    dfclean = dfnostd[(zscore < 4) & (zscore > -4)].reset_index(drop=True)
    outlier_rows = dfnostd[~((zscore < 4) & (zscore > -4))].reset_index(drop=True)

    dfdiscard = pd.concat([zero_height_rows, large_std_rows, outlier_rows]).reset_index(drop=True)

    if len(dfclean) == 0:
        print("No data left after cleaning, returning original dataframe with no cleaning")
        #clear all of dfdiscard
        dfdiscard = pd.DataFrame(columns=df.columns)
        return {"cleaned": df, "discarded": dfdiscard}

    return {"cleaned": dfclean, "discarded": dfdiscard}

def generate_height_graph_for_plant_id(plant_id, display_graph=False, clean_data=True):
    # date stored as 20260318 12:00:00 in the file name, but stored as 2026-03-18 12:00:00 in the database
    conn = db_util.open_connection_to_database()
    results = db_util.get_all_heights_for_plant_id(conn, plant_id)
    db_util.close_connection_to_database(conn)
    folder = f"/srv/samba/plants/image/by_plant/plant{plant_id}/graphs/"
    if not os.path.exists(folder):
        os.makedirs(folder)
    db_util.query_to_CSV_file(results, folder+f"height_log_plant_id_{plant_id}.csv")

    df = pd.read_csv(folder+f"height_log_plant_id_{plant_id}.csv")

    if clean_data:
        df_dict = cleanDataForGraphing(df)
        df = df_dict["cleaned"]
        dfdiscard = df_dict["discarded"]

    print(df["measured_at"][2])

    plt.scatter(pd.to_datetime(df["measured_at"], utc=True), df["height_units_m"]*100, s=10, color='forestgreen', label= "Acceptable Data")
    plt.scatter(pd.to_datetime(dfdiscard["measured_at"], utc=True), dfdiscard["height_units_m"]*100, s=10, color='goldenrod', label= "Discarded Data")

    rollingaverage = df["height_units_m"].rolling(window=25, center=True).mean()
    plt.plot(pd.to_datetime(df["measured_at"], utc=True), rollingaverage*100, color='darkgreen', label= "Rolling Average")

    datearray = pd.to_datetime(df["measured_at"], utc=True)
    idealgrowth = []
    
    start_time = datearray.iloc[0]
    start_height = list(df["height_units_m"])[0]*100
    

    '''
    Later, we will want alerts if a non-discarded point drops below this floor'''
    for timestamp in datearray:
        duration = timestamp - start_time
        net_hours_passed = duration.total_seconds() / 3600

        hours_to_11cm = 3 * 7 * 24 #weeks in hours
        growth_rate = .01
        height_max = 18-start_height  #this is the physical height of the light array. we start pruning the plants

        #sigmoidal growth estimation
        growth_value = height_max * (1 / (1 + math.exp((-1)*growth_rate*(net_hours_passed-hours_to_11cm)))) + start_height - 1.25

        idealgrowth.append(growth_value)

    plt.plot(datearray, idealgrowth, color='red', label="Plant Alert Floor", linestyle='--', alpha = 0.3)

    plt.xlabel(f"Measured On")
    plt.ylabel("Height (cm)")
    plt.title(f"Plant Height {plant_id} Over Time")
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(plt.MultipleLocator(5))
    plt.grid()
    plt.tight_layout()
    plt.ylim(-1, None)
    plt.legend() #Added a legend and labels
    plt.savefig(f"{folder}height_graph.png")
    if display_graph:
        plt.show()
    else:
        plt.close()

    print(f"Generated height graph for plant {plant_id} at {folder}height_graph.png")

#generate_height_graph_for_plant_id(5, display_graph=True)

generate_height_graph_for_plant_id(1, display_graph=False)
generate_height_graph_for_plant_id(5, display_graph=False)
generate_height_graph_for_plant_id(10, display_graph=False)
generate_height_graph_for_plant_id(12, display_graph=False)
generate_height_graph_for_plant_id(13, display_graph=False)
generate_height_graph_for_plant_id(16, display_graph=False)
generate_height_graph_for_plant_id(17, display_graph=False)
generate_height_graph_for_plant_id(18, display_graph=False)
generate_height_graph_for_plant_id(11, display_graph=False)
generate_height_graph_for_plant_id(21, display_graph=False)

# query statment to insert height log values into a height_log_plant_3.csv file for testing the graphing function
# select height_log.*, view.plant_id from height_log join view using (view_id) join plant using (plant_id) where plant.plant_id = 3 order by measured_at; 
# measured_at, height_units_m, view_id, plant_id;
# then use the generated csv file to test the graphing function, and make sure it is working correctly before running it for all plants in the database.