import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import logging
import os

# Setting up logging to capture warnings and info
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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


def calculate_distances(row):
    try:
        # Initialize variables
        dist_bw_st_n_ls, dist_bw_ls_xing, crossing_length, dist_bw_xing_end, dist_bw_ls_end = 0, 0, 0, 0, 0

        # Parse the_geom
        geom = row['the_geom'][10:].strip('()')
        start_coords = geom.split(',')[0].split(" ")
        end_coords = geom.split(',')[-1].split(" ")
        srvy_start_long, srvy_start_lat = float(start_coords[0]), float(start_coords[1])
        srvy_end_long, srvy_end_lat = float(end_coords[0]), float(end_coords[1])

        # Calculate distances
        dist_bw_st_n_ls = haversine_distance(
            row['Start_Location_Point'], row['Start_Location_Point.1'],
            srvy_start_lat, srvy_start_long
        )

        if row['Crossing'].lower() == 'yes':
            dist_bw_ls_xing = haversine_distance(
                row['Crossing_Start_Point'], row['Crossing_Start_Point.1'],
                srvy_end_lat, srvy_end_long
            )
            crossing_length = haversine_distance(
                row['Crossing_Start_Point'], row['Crossing_Start_Point.1'],
                row['Crossing_End_Point'], row['Crossing_End_Point.1']
            )
            if row['End_Location_Point'] > 0:
                dist_bw_xing_end = haversine_distance(
                    row['Crossing_End_Point'], row['Crossing_End_Point.1'],
                    row['End_Location_Point'], row['End_Location_Point.1']
                )

        if row['End_Location_Point'] > 0:
            dist_bw_ls_end = haversine_distance(
                srvy_end_lat, srvy_end_long,
                row['End_Location_Point'], row['End_Location_Point.1']
            )

        total_stretch_length = (
                dist_bw_st_n_ls + dist_bw_ls_xing + crossing_length +
                dist_bw_xing_end + dist_bw_ls_end + row['distance']
        )

        return total_stretch_length

    except Exception as e:
        return row['distance']
def process_mapping(source_df, mapping_df):
    """Process the mapping instructions and create the output DataFrame."""
    # Initialize an empty DataFrame with the same number of xs as source_df
    output_df = pd.DataFrame(index=source_df.index)

    # Counters for summary
    copied_count = 0
    filled_later_count = 0
    calculated_count = 0

    # Iterate through each x in the mapping DataFrame
    for _, x in mapping_df.iterrows():
        src_col = x['Mapping Columns']
        dst_col = x['Excel_Sheet_2 (Columns)']
        condition = x['Condition for Calculation']

        # Handle "Copy as it is"
        if condition == "Copy as it is":
            if src_col in source_df.columns:
                output_df[dst_col] = source_df[src_col]
                copied_count += 1
                logging.info(f"Copied column '{src_col}' to '{dst_col}'")
            else:
                logging.warning(f"Source column '{src_col}' not found in source data")

        # Handle "Do Nothing" by creating column with "to be filled later"
        elif condition == "Do Nothing":
            output_df[dst_col] = "to be filled later"
            filled_later_count += 1
            logging.info(f"Created column '{dst_col}' with value 'to be filled later' for {len(source_df)} xs")

        # Handle custom calculations
        elif "TO BE CALCULATED" in str(condition):
            if "Calculate the distance between two lat longs" in condition:
                # Check if required columns exist
                if all(col in source_df.columns for col in
                       ['Road_Edge_Left', 'Road_Edge_Left.1', 'Road_Edge_Right', 'Road_Edge_Right.1']):
                    # Calculate distance between lat-long pairs
                    output_df[dst_col] = source_df.apply(
                        lambda x: haversine_distance(
                            x['Road_Edge_Left'], x['Road_Edge_Left.1'],
                            x['Road_Edge_Right'], x['Road_Edge_Right.1']
                        ) if all(pd.notnull([x['Road_Edge_Left'], x['Road_Edge_Left.1'], x['Road_Edge_Right'],
                                             x['Road_Edge_Right.1']])) else np.nan,
                        axis=1
                    )
                    calculated_count += 1
                    logging.info(f"Calculated road width for '{dst_col}'")
                else:
                    logging.warning(f"Missing columns for road width calculation in '{dst_col}'")

            elif "calculate chain-age" in condition:
                output_df[dst_col] = source_df.apply(lambda x: calculate_distances(x),
                axis = 1
                )

            elif "if end point location type contains the string kms then the End_Point_Location_Type + End_Location_Photo" in condition:
                if all(col in source_df.columns for col in ['end_point_', 'end_locati']):
                    output_df[dst_col] = source_df.apply(
                        lambda x: f"{x['end_point_']} {x['end_locati']}"
                        if pd.notnull(x['end_point_']) and 'kms' in x['end_point_'].lower()
                        else np.nan,
                        axis=1
                    )
                    calculated_count += 1
                    logging.info(f"Calculated road chainage for '{dst_col}'")
                else:
                    logging.warning(f"Missing columns for road chainage calculation in '{dst_col}'")

            # Handle "Crossing_Length + 2"
            elif "Value = Crossing_length + 2" in str(condition):
                if 'crossing_l' in source_df.columns:
                    output_df[dst_col] = source_df['crossing_l'].apply(
                        lambda x: x + 2 if pd.notnull(x) else np.nan
                    )
                    calculated_count += 1
                    logging.info(f"Calculated protection length for '{dst_col}'")
                else:
                    logging.warning(f"Source column 'Crossing_Length' not found for '{dst_col}'")

    # Print summary
    logging.info(
        f"Summary: {copied_count} columns copied, {filled_later_count} columns filled with 'to be filled later', {calculated_count} columns calculated")
    return output_df

def main():
    """Main function to load, process, and save the mapped data."""
    try:
        # Loading the mapping instructions
        mapping_df = pd.read_excel('map_excel_data.xlsx', sheet_name='Sheet1')
        logging.info("Loaded mapping instructions from map_excel_data.xlsx")

        # Loading the source data
        source_df = pd.read_excel('tarana_updated.xlsx', sheet_name='Sheet1')
        logging.info("Loaded source data from ofc-survey_updated.xlsx")

        # Processing the mapping
        output_df = process_mapping(source_df, mapping_df)

        # Saving the output to a new Excel file
        output_df.to_excel('mapped_tarana_output.xlsx', index=False)
        logging.info("Saved mapped data to mapped_output.xlsx")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")

if __name__ == "__main__":
    main()