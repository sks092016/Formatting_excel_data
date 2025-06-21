import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import logging
import os

mapping_df = pd.read_excel('map_excel_data.xlsx', sheet_name='Sheet1')
logging.info("Loaded mapping instructions from map_excel_data.xlsx")

# Loading the source data
source_df = pd.read_excel('ofc-survey_updated.xlsx', sheet_name='Sheet1')
logging.info("Loaded source data from ofc-survey_updated.xlsx")


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two lat-long points using the Haversine formula."""
    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    r = 6371e3  # Earth's radius in meters
    return c * r

for _, row in source_df.iterrows():
    dist_bw_st_n_ls, dist_bw_ls_xing, crossing_length, dist_bw_xing_end, dist_bw_ls_end, total_stretch_length = 0,0,0,0,0
    try:
        srvy_start_long, srvy_start_lat = row['the_geom'][10:].strip('()').split(',')[0].split(" ")
        srvy_end_long, srvy_end_lat = row['the_geom'][10:].strip('()').split(',')[-1].split(" ")
        dist_bw_st_n_ls = haversine_distance(row['Start_Location_Point'], row['Start_Location_Point.1'], srvy_start_lat,srvy_start_long)

        if row['Crossing'].lower == 'yes':
            dist_bw_ls_xing = haversine_distance(row['Crossing_Start_Point'], row['Crossing_Start_Point.1'], srvy_end_lat,srvy_end_long)
            crossing_length = haversine_distance(row['Crossing_Start_Point'], row['Crossing_Start_Point.1'], row['Crossing_End_Point'], row['Crossing_End_Point.1'])
            dist_bw_xing_end = haversine_distance(row['Crossing_End_Point'], row['Crossing_End_Point.1'], row['End_Location_Point'], row['End_Location_Point.1'])

        dist_bw_ls_end = haversine_distance(srvy_end_lat, srvy_end_long, row['End_Location_Point'], row['End_Location_Point.1'])

        total_stretch_length = dist_bw_st_n_ls + dist_bw_ls_xing + crossing_length + dist_bw_xing_end + dist_bw_ls_end + row['distance']
    except:
        print("nan not a number")
