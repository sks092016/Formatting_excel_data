import pandas as pd
import geopandas as gpd
from math import radians, sin, cos, sqrt, atan2
import tkinter as tk
from tkinter import filedialog
import time
import difflib
import numpy as np
import shutil
from pathlib import Path
import re

import requests

root = tk.Tk()
root.withdraw()

######################################### CONSTANTS #############################################################
# ROAD WIDTHS
PMGY = 4
SH = 15
NH = 40
Grampanchyat = GP = 6
PWD = 6
ODR = 6
MDR = 6
Nagar_Parishad = 4
MPRRDA = 4
OTHERS = 6

# RM & MH INTERVAL
rm_interval = 200
mh_interval = 1800

# PROTECTION
culvert_protection = 'DWC + PCC'
bridge_protection = 'GI + Clamping'
hard_rock = 'DWC + PCC'

# VERSION
version = '1.0'

# PATH
# for Windows
# folder_path = 'D:\\bharat_net_data\\'
# for Mac
folder_path = '/Users/subhashsoni/Documents/Bharatnet_OFC_planning/'

# APIKEY
api_key = 'AIzaSyBpsTQbW0ax0c18wGhC46wLkIPNvOH1sb4'

# DEFAULT LAT-LONG
lat = 0
lon = 0
place_id = ''
############################################### API URLS ##########################################################
# GOOGLE
place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=50&key={api_key}"
roads_place_id_url = f"https://roads.googleapis.com/v1/nearestRoads?points={lat},{lon}&key={api_key}"
road_name_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name&key={api_key}"

# OPENSM
url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
headers_village_name = {
    'User-Agent': 'village-lookup-script'
}
headers_road_name = {
    'User-Agent': 'road-name-fetcher-script'
}
################################################ To Be Used ########################################################

# pd.DataFrame([0.0] + [sum(list(temp_df['distance'])[:i + 1]) for i in range(1, len(list(temp_df['distance'])))]).values

######################################### Reference Files ########################################################

base_url = "https://fieldsurvey.rbt-ltd.com/app"
gdf_reference = gpd.read_file("References/tarana_shape_file.shp")

######################################## Reading the Shape File ##################################################

shapefile_path = filedialog.askopenfilename(
    title="Select a shape file",
    filetypes=[("Shape Files", "*.shp"), ("All files", "*.*")]
)
gdf_working = gpd.read_file(shapefile_path)

###################################### Creating the Directory for file store #####################################
blockName = gdf_working['block_name'][0]
districtName = gdf_working['district_n'][0]

dir_path = Path(folder_path + districtName + "-" + blockName + version)

# If it exists, delete it
if dir_path.exists() and dir_path.is_dir():
    shutil.rmtree(dir_path)  # Deletes the entire folder and its contents

# Now create it fresh
dir_path.mkdir(parents=True, exist_ok=False)
###################################### Checking the Structure of the Files #######################################

is_structure_same = set(gdf_reference.columns) <= set(gdf_working.columns)
print(is_structure_same)
if not is_structure_same:
    col_diff_A = set(gdf_reference.columns) - set(gdf_working.columns)
    print("The Structure of the shape file is not matching the reference structure aborting. \n")
    time.sleep(0.5)
    print("Following columns are not present in the selected shape file:\n")
    time.sleep(0.5)
    print(col_diff_A)
else:
    print(gdf_working.columns)
###################################### Creating the Common Span Details #########################################

span_ = gdf_working[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
gdf_working['distance'] = pd.to_numeric(gdf_working['distance'], errors='coerce')
span_dis = gdf_working.groupby('span_name').agg({'distance': 'sum'})
boq_sd_df = pd.merge(span_, span_dis, on=['span_name'], how='inner')

###################################### Creating the Details Sheet ################################################
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


def change_point_name(value):
    if value is not None:
        if any(sub in value.lower() for sub in ['re', 're ', ' re']):
            return 'Road Edge'
        elif str(value).upper() == "SE":
            return 'Segment Edge'
        elif difflib.SequenceMatcher(None, value.lower(), "culvert").ratio() > 0.5:
            return 'Culvert'
        elif difflib.SequenceMatcher(None, value.lower(), "bridge").ratio() > 0.5:
            return 'Bridge'
        else:
            return value.capitalize()
    else:
        return 'NA'


def categorize_value(value):
    value = str(value)  # Ensure value is string
    if any(sub in value.lower() for sub in ['road crossing']):  # Check for 'Re' or 'RE'
        return 'Road Crossing'
    elif difflib.SequenceMatcher(None, value.lower(), "culvert").ratio() > 0.5:
        return 'Crossing'
    elif difflib.SequenceMatcher(None, value.lower(), "bridge").ratio() > 0.5:
        return 'Crossing'
    elif any(sub in value.lower() for sub in ['gp', 'gram panchyat', 'grampanchayat']):  # Check for 'GP', 'Gp', etc.
        return 'Gram Panchyat'
    else:
        return 'Landmark'


def calculate_offset_width(row, param):
    value = str(row['road_autho']).upper()
    keywords = ['PMGY', 'SH', 'NH', 'Nagar Parishad', 'Grampanchyat', 'GP', 'PWD', 'ODR', 'MDR']
    matched = next((sub for sub in keywords if sub in value), None)
    if any(sub in value for sub in ['PMGY', 'SH', 'NH', 'Nagar Parishad', 'Grampanchyat', 'GP', 'PWD', 'ODR', 'MDR']):
        value = globals()[matched]
        if param == 'offset':
            return value / 2 + 0.2 * value
        if param == 'width':
            return value
    else:
        if param == 'offset':
            return OTHERS / 2 + 0.2 * OTHERS
        if param == 'width':
            return OTHERS
    return None


def finding_lat_lon(row, lat_lon):
    value = str(row['end_point_']).lower()
    att = lat_lon
    if att == 'lat':
        if any(sub in value for sub in ['culvert', 'bridge', 'road crossing']):
            return row['start_lat']
        else:
            return row['lat']
    elif att == 'lon':
        if any(sub in value for sub in ['culvert', 'bridge', 'road crossing']):
            return row['start_lon']
        else:
            return row['Long']
    return None


def calculating_rms(df):
    # Track cumulative distances
    cum_distance_start = 0
    rm_list = []
    for d in df['distance']:
        cum_distance_end = cum_distance_start + float(d)
        # Count new RMs in this segment
        rm_start_count = cum_distance_start // rm_interval
        rm_end_count = cum_distance_end // rm_interval
        new_rms = int(rm_end_count - rm_start_count)
        rm_list.append(new_rms)
        cum_distance_start = cum_distance_end
    rm_df = pd.DataFrame(rm_list, columns=['rm'], index=df.index)
    return rm_df


def calculating_mhs(df):
    cum_distance_start = 0
    mh_list = []
    for d in df['distance']:
        cum_distance_end = cum_distance_start + float(d)
        # Count new MHs in this segment
        mh_start_count = cum_distance_start // mh_interval
        mh_end_count = cum_distance_end // mh_interval
        new_mhs = int(mh_end_count - mh_start_count)
        mh_list.append(new_mhs)
        cum_distance_start = cum_distance_end
    mh_df = pd.DataFrame(mh_list, columns=['mh'], index=df.index)
    return mh_df


def calculate_road_chainage(row):
    chainage = ''
    if 'kms' in str(str(row['end_point_'])).lower():
        chainage = str(row['end_point_'])
    else:
        chainage = ''
    return chainage


def calculate_protec(row, param):
    value = str(row['crossing_t'])
    length = float(row['distance'])
    strata = str(row['strata_typ'])
    if difflib.SequenceMatcher(None, value.lower(), "culvert").ratio() > 0.5 and length <= 20:
        if param == 'struct' or param == 'for':
            return 'Culvert'
        elif param == 'type':
            return culvert_protection
        elif param == 'len':
            return length + 6
        elif param == 'length':
            return length
    elif difflib.SequenceMatcher(None, value.lower(), "bridge").ratio() > 0.5 and length > 20:
        if param == 'struct' or param == 'for':
            return 'Bridge'
        elif param == 'type':
            return bridge_protection
        elif param == 'len':
            return length + 6
        elif param == 'length':
            return length

    if strata == 'hard_rock' or strata == 'Hard Rock':
        if param == 'for':
            return 'Hard Rock'
        elif param == 'type':
            return hard_rock
        elif param == 'len':
            return length + 6
        elif param == 'length':
            return None
    return ''


def finding_utility(row, param):
    side = row['ofc_laying']
    value = str(row['end_point_']).lower()
    utility = None
    if 'rjil' in value:
        utility = "Reliance Jio"
    elif 'airtel' in value:
        utility = "Airtel"
    elif 'bsnl' in value:
        utility = 'BSNL'
    elif 'gas' in value:
        utility = 'Gas PipeLine ' + value
    elif 'hpcl' in value:
        utility = 'HPCL Pipeline'
    elif 'iocl' in value:
        utility = 'IOCL Pipeline'
    elif 'railway' in value:
        utility = 'railway'
    elif 'petrol' in value:
        utility = 'Petroleum Pipeline ' + value
    elif 'gail' in value:
        utility = 'Gail Xing'
    if param == 'utility':
        return utility
    if param == 'side' and utility is not None:
        return side
    return None

if is_structure_same:
    cols_ds = ['SPAN_CONTINUITY', 'POINT NAME', 'TYPE', 'POSITION', 'OFFSET', 'CHAINAGE', 'DISTENCE(M)', 'LATITUDE',
               "LONGITUDE", 'ROUTE NAME', 'ROUTE TYPE',
               'OFC TYPE', 'LAYING TYPE', 'ROUTE ID', 'ROUTE MARKER', 'MANHOLE', 'ROAD NAME', 'ROAD WIDTH(m)',
               'ROAD SURFACE', 'OFC POSITION', 'APRX DISTANCE FROM RCL(m)',
               'AUTHORITY NAME', 'ROAD CHAINAGE', 'ROAD STRUTURE TYPE', 'LENGTH (IN Mtr.)', 'PROTECTION TYPE',
               'PROTECTION FOR', 'PROTECTION LENGTH (IN Mtr.)', 'UTILITY NAME',
               'SIDE OF THE ROAD', 'SOIL TYPE', 'REMARKS']

    boq_ = pd.DataFrame(columns=cols_ds)
    span = gdf_working.sort_values('span_name').span_name.unique()
    for s in span:
        print(s)
        temp_df = gdf_working[gdf_working.span_name == s].sort_values('Sequqnce')
        boq_ds_df = pd.DataFrame(columns=cols_ds)
        boq_ds_df['SPAN_CONTINUITY'] = temp_df['Sequqnce']
        boq_ds_df['POINT NAME'] = temp_df.apply(change_point_name, axis=1)
        boq_ds_df['TYPE'] = temp_df['end_point_'].apply(categorize_value)
        boq_ds_df['POSITION'] = temp_df['ofc_laying']
        boq_ds_df['OFFSET'] = temp_df.apply(calculate_offset_width, axis=1, args=('offset',))
        boq_ds_df['CHAINAGE'] = pd.DataFrame([sum(list(temp_df['distance'].astype(float))[:i - 1]) for i in range(1, len(list(temp_df['distance']))+1)]).values
        boq_ds_df['DISTENCE(M)'] = temp_df['distance']
        boq_ds_df['LATITUDE'] = temp_df.apply(finding_lat_lon, axis=1, args=('lat',))
        boq_ds_df['LONGITUDE'] = temp_df.apply(finding_lat_lon, axis=1, args=('lon',))
        boq_ds_df['ROUTE NAME'] = temp_df['span_name']
        boq_ds_df['ROUTE TYPE'] = temp_df['scope']
        boq_ds_df['OFC TYPE'] = '48F'
        boq_ds_df['LAYING TYPE'] = 'UG'
        boq_ds_df['ROUTE ID'] = temp_df['span_id']
        boq_ds_df['ROUTE MARKER'] = calculating_rms(temp_df)
        boq_ds_df['MANHOLE'] = calculating_mhs(temp_df)
        boq_ds_df['ROAD NAME'] = temp_df['road_name']
        boq_ds_df['ROAD WIDTH(m)'] = temp_df.apply(calculate_offset_width, axis=1, args=('width',))
        boq_ds_df['ROAD SURFACE'] = temp_df['road_surfa']
        boq_ds_df['OFC POSITION'] = temp_df['ofc_laying']
        boq_ds_df['APRX DISTANCE FROM RCL(m)'] = ''
        boq_ds_df['AUTHORITY NAME'] = temp_df['road_autho']
        boq_ds_df['ROAD CHAINAGE'] = temp_df.apply(calculate_road_chainage, axis=1)
        boq_ds_df['ROAD STRUTURE TYPE'] = temp_df.apply(calculate_protec, axis=1, args=('struct',))
        boq_ds_df['LENGTH (IN Mtr.)'] = temp_df.apply(calculate_protec, axis=1, args=('length',))
        boq_ds_df['PROTECTION TYPE'] = temp_df.apply(calculate_protec, axis=1, args=('type',))
        boq_ds_df['PROTECTION FOR'] = temp_df.apply(calculate_protec, axis=1, args=('for',))
        boq_ds_df['PROTECTION LENGTH (IN Mtr.)'] = temp_df.apply(calculate_protec, axis=1, args=('len',))
        boq_ds_df['UTILITY NAME'] = temp_df.apply(finding_utility, axis=1, args=('utility',))
        boq_ds_df['SIDE OF THE ROAD'] = temp_df.apply(finding_utility, axis=1, args=('side',))
        boq_ds_df['SOIL TYPE'] = temp_df['strata_typ']
        boq_ds_df['REMARKS'] = "NA"
        boq_ = pd.concat([boq_, boq_ds_df])

    with pd.ExcelWriter(str(dir_path) + f"/{districtName}-{blockName}-{version}.xlsx", engine='openpyxl',
                        mode='w') as writer:
        boq_.to_excel(writer, sheet_name='Details Sheet', index=False)

    # ############################################## Generating the Span Details ########################################

    cols_sd = ['FROM', 'TO', 'ROUTE NAME', 'RING NO.', 'ROUTE TYPE', 'OFC TYPE', 'LAYING TYPE', 'ROUTE ID',
               'TOTAL LENGTH(KM)',
               'OH', 'UG']
    span_details = pd.DataFrame(columns=cols_sd)

    span_details['FROM'] = boq_sd_df['from_gp_na']
    span_details['TO'] = boq_sd_df['to_gp_name']
    span_details['ROUTE NAME'] = boq_sd_df['span_name']
    span_details['RING NO.'] = boq_sd_df['ring_no']
    span_details['ROUTE TYPE'] = 'OFC to be laid for Ring Formation (in Km)'
    span_details['OFC TYPE'] = '48F'
    span_details['LAYING TYPE'] = 'UG'
    span_details['ROUTE ID'] = boq_sd_df['span_id']
    span_details['TOTAL LENGTH(KM)'] = boq_sd_df['distance']
    span_details['OH'] = 0
    span_details['UG'] = boq_sd_df['distance']

    with pd.ExcelWriter(str(dir_path) + f"/{districtName}-{blockName}-{version}.xlsx", engine='openpyxl', mode='a',
                        if_sheet_exists='replace') as writer:
        span_details.to_excel(writer, sheet_name='Span Details', index=False)

    # ############################################# Generating the RoW Details #########################################

    authorities = gdf_working['road_autho'].unique()

    cols_row = ['ROUTE NAME', 'ROUTE TYPE', 'RING NO', 'ROUTE ID', 'TOTAL ROUTE LENGTH'] + list(authorities)

    row_details = pd.DataFrame(columns=cols_row)

    df2 = gdf_working.pivot_table(values='distance', index='span_name', columns='road_autho', aggfunc='sum',
                                  fill_value=0).reset_index()
    row_ = pd.merge(boq_sd_df, df2, on=['span_name'], how='inner')

    row_details['ROUTE NAME'] = row_['span_name']
    row_details['ROUTE TYPE'] = row_['scope']
    row_details['RING NO'] = row_['ring_no']
    row_details['ROUTE ID'] = row_['span_id']
    row_details['TOTAL ROUTE LENGTH'] = row_['distance']
    for auths in authorities:
        row_details[auths] = row_[auths]
    row_details['OTHERS'] = 0

    with pd.ExcelWriter(str(dir_path) + f"/{districtName}-{blockName}-{version}.xlsx", engine='openpyxl', mode='a',
                        if_sheet_exists='replace') as writer:
        row_details.to_excel(writer, sheet_name='RoW', index=False)

    ####################################### Generating the Protection Details ###########################################

    cols_pro = ['ROUTE NAME', 'ROUTE TYPE', 'TOTAL ROUTE LENGTH', 'NO OF CULVERT', 'LENGTH (IN Mtr) OF CULVERT',
                'NO OF BRIDGE',
                'LENGTH (IN Mtr) OF BRIDE',
                'LENGTH (IN Mtr) OF PCC', 'LENGTH (IN Mtr) OF DWC', 'LENGTH (IN Mtr) OF GI',
                'LENGTH (IN Mtr) OF DWC+PCC',
                "Soil Detail", "LENGTH (IN Mtr) OF DWC+PCC (HARD ROCK)", 'LENGTH (IN Mtr) OF ANCORING']
    protection_details = pd.DataFrame(columns=cols_pro)

    _details = pd.read_excel(str(dir_path) + f"/{districtName}-{blockName}-{version}.xlsx", sheet_name='Details Sheet')

    _protection = _details[['ROUTE NAME', 'ROAD STRUTURE TYPE', 'LENGTH (IN Mtr.)', 'PROTECTION TYPE', 'PROTECTION FOR',
                            'PROTECTION LENGTH (IN Mtr.)']]
    r_agg = _protection.groupby(['ROUTE NAME', 'PROTECTION FOR'])['PROTECTION LENGTH (IN Mtr.)'].agg(
        ['count', 'sum']).unstack(fill_value=0)
    if len(r_agg.columns) == 4:
        r_agg.columns = ['NO OF BRIDGE', 'NO OF CULVERT', 'LENGTH (IN Mtr) OF BRIDGE',
                         'LENGTH (IN Mtr) OF CULVERT']  # Rename columns
    else:
        r_agg.columns = ['NO OF BRIDGE', 'NO OF CULVERT', 'HARD ROCK', 'LENGTH (IN Mtr) OF BRIDGE',
                         'LENGTH (IN Mtr) OF CULVERT', 'HARD ROCK (Length)']  # Rename columns
    r_agg = r_agg.reset_index()
    p_agg = _protection.pivot_table(values='PROTECTION LENGTH (IN Mtr.)', index='ROUTE NAME', columns='PROTECTION TYPE',
                                    aggfunc='sum', fill_value=0).reset_index()
    protection_ = pd.merge(r_agg, p_agg, on='ROUTE NAME', how='outer')

    merged_df = boq_sd_df
    merged_df.rename(columns={'span_name': 'ROUTE NAME'}, inplace=True)
    protection_ = pd.merge(protection_, merged_df, on='ROUTE NAME', how='outer')

    protection_details['ROUTE NAME'] = protection_['ROUTE NAME']
    protection_details['ROUTE TYPE'] = 'OFC to be laid for Ring Formation (in Km)'
    protection_details['TOTAL ROUTE LENGTH'] = protection_['distance']
    protection_details['NO OF CULVERT'] = protection_['NO OF CULVERT']
    protection_details['LENGTH (IN Mtr) OF CULVERT'] = protection_['LENGTH (IN Mtr) OF CULVERT'].astype(float) - 6 * protection_[
        'NO OF CULVERT'].astype(float)
    protection_details['NO OF BRIDGE'] = protection_['NO OF BRIDGE']
    protection_details['LENGTH (IN Mtr) OF BRIDE'] = protection_['LENGTH (IN Mtr) OF BRIDGE'].astype(float) - 6 * protection_[
        'NO OF BRIDGE'].astype(float)
    protection_details['LENGTH (IN Mtr) OF PCC'] = 0
    protection_details['LENGTH (IN Mtr) OF DWC'] = protection_['LENGTH (IN Mtr) OF CULVERT']
    protection_details['LENGTH (IN Mtr) OF GI'] = protection_['LENGTH (IN Mtr) OF BRIDGE']
    protection_details['LENGTH (IN Mtr) OF DWC+PCC'] = protection_['HARD ROCK (Length)']
    protection_details['Soil Details'] = ''
    protection_details['HARD ROCK (Length)'] = protection_['HARD ROCK (Length)']
    protection_details['LENGTH (IN Mtr) OF ANCORING'] = 0

    with pd.ExcelWriter(str(dir_path) + f"/{districtName}-{blockName}-{version}.xlsx", engine='openpyxl', mode='a',
                        if_sheet_exists='replace') as writer:
        protection_details.to_excel(writer, sheet_name='Protection Details', index=False)


    #
    ##################################################### RoW PreSurvey ######################################################
    #

    def extract_coords(geom):
        try:
            geom_str = str(geom)
            coords = re.findall(r"x\d+\s+y\d+", geom_str)
            return coords
        except Exception as e:
            print(f"Error processing geom: {geom} -> {e}")
            return []


    cols_row_ps = ['SrNo', 'Ring No', 'GP Name', 'Span Name', 'NHSHNo', 'RoadWidth', 'RowBoundaryLmt', 'KMStoneFromA',
                   'KMStoneToB', 'SuveryDist', 'st_Lat_Long_Auth', 'end_lat_Long_Auth', 'LandmarkRHS',
                   'VlgTwnPoint', 'OFClaying', 'RdCrossing Req', 'ReasonRdCrossing', 'UtilityLHS', 'UtilityChecked',
                   'RowAuthorityName', 'AuthorityAddress', 'FeasibilityOfROWApproval', 'TypeOfOverlapArea',
                   'NearestLandmark', 'LengthOfOverlapArea', 'ExpansionInProg', 'ExpansionPlanned', 'TypeOfCrossing',
                   'st_Lat_Long_xing', 'end_lat_Long_xing', 'LatLandmark', 'LongLandmark',
                   'LengthOfCrossing', 'Remarks']

    span = gdf_working.sort_values('span_name').span_name.unique()
    row_pre_survey = pd.DataFrame(columns=cols_row_ps)
    for s in span:
        print(s)
        temp_df = gdf_working[gdf_working.span_name == s].sort_values('Sequqnce')

        output = []
        group = None
        crossing_coords_start = []
        crossing_coords_end = []
        output_df = None

        for _, row in temp_df.iterrows():
            p_n, s_n, dist, auth, geom, ofc_side = row["end_point_"], row["span_name"], row["distance"], row[
                "road_autho"], \
                row["geometry"], row['ofc_laying']
            coords = extract_coords(geom)
            if not any(sub in p_n for sub in ['culvert', 'bridge']):
                if group is None:
                    group = {
                        'SrNo': '',
                        'FROM AND TO GP': s_n,
                        'NHSHNo': '',
                        'RoadWidth': globals()[auth.upper()],
                        'RowBoundaryLmt': '',
                        'KMStoneFromA': "",
                        'KMStoneToB': "",
                        'SuveryDist': dist,
                        'st_Lat_Long_Auth': f"{coords[0][1]},{coords[0][0]}",
                        'end_lat_Long_Auth': f"{coords[-1][1]},{coords[-1][0]}",
                        'LandmarkRHS': "",
                        'VlgTwnPoint': "",
                        'OFClaying': ofc_side,
                        'RdCrossing Req': '',
                        'ReasonRdCrossing': '',
                        'UtilityLHS': '',
                        'UtilityRHS': "",
                        'UtilityChecked': '',
                        'RowAuthorityName': auth,
                        'AuthorityAddress': f"{blockName}, {districtName}",
                        'FeasibilityOfROWApproval': 'Yes',
                        'TypeOfOverlapArea': '',
                        'NearestLandmark': "",
                        'LengthOfOverlapArea': '',
                        'ExpansionInProg': '',
                        'ExpansionPlanned': '',
                        'TypeOfCrossing': '',
                        'st_Lat_Long_xing': '',
                        'end_lat_Long_xing': '',
                        'LatLandmark': '',
                        'LongLandmark': '',
                        'LengthOfCrossing': '',
                        'Remarks': ''
                    }
                elif group["RowAuthorityName"] == auth:
                    group["SuveryDist"] += dist
                    group["end_lat_Long_Auth"] = f"{coords[-1][1]},{coords[-1][0]}"
                else:
                    output.append(group)
                    group = {
                        'SrNo': '',
                        'FROM AND TO GP': s_n,
                        'NHSHNo': '',  # TODO Find Road Nmme
                        'RoadWidth': globals()[auth.upper()],
                        'RowBoundaryLmt': '',
                        'KMStoneFromA': "",
                        'KMStoneToB': "",
                        'SuveryDist': dist,
                        'st_Lat_Long_Auth': f"{coords[0][1]},{coords[0][0]}",
                        'end_lat_Long_Auth': f"{coords[-1][1]},{coords[-1][0]}",
                        'LandmarkRHS': "",  # TODO Find LandMark
                        'VlgTwnPoint': "",  # TODO Find Village from-to
                        'OFClaying': ofc_side,
                        'RdCrossing Req': '',
                        'ReasonRdCrossing': '',
                        'UtilityLHS': '',
                        'UtilityRHS': "",
                        'UtilityChecked': '',
                        'RowAuthorityName': auth,
                        'AuthorityAddress': f"{blockName}, {districtName}",
                        'FeasibilityOfROWApproval': 'Yes',
                        'TypeOfOverlapArea': '',
                        'NearestLandmark': "",  # TODO Find LandMark
                        'LengthOfOverlapArea': '',
                        'ExpansionInProg': '',
                        'ExpansionPlanned': '',
                        'TypeOfCrossing': '',
                        'st_Lat_Long_xing': '',
                        'end_lat_Long_xing': '',
                        'LatLandmark': '',  # TODO Latitude of LandMark
                        'LongLandmark': '',  # TODO Longitude of the LandMark
                        'LengthOfCrossing': '',
                        'Remarks': ''
                    }
                    crossing_coords_start = []
                    crossing_coords_end = []
            else:
                if group:
                    group["TypeOfCrossing"] = p_n.lower()
                    crossing_coords_start.append(f"({coords[0][1]},{coords[0][0]})")
                    crossing_coords_end.append(f"({coords[-1][1]},{coords[-1][0]})")
                    group["SuveryDist"] += dist
                    group["end_lat_Long_Auth"] = f"{coords[-1][1]},{coords[-1][0]}"
                    group["st_Lat_Long_xing"] = ", ".join(crossing_coords_start)
                    group["end_lat_Long_xing"] = ", ".join(crossing_coords_end)

            # Append final group
            if group:
                output.append(group)

            # Create output DataFrame
            output_df = pd.DataFrame(output)
            output_df.reset_index(drop=True, inplace=True)
        row_pre_survey = pd.concat([row_pre_survey, output_df])


    def finding_road_name(row):
        lat, lon = row['st_Lat_Long_Auth'].split(',')
        roads_place_id_url = f"https://roads.googleapis.com/v1/nearestRoads?points={lat},{lon}&key={api_key}"
        response_pid = requests.get(roads_place_id_url)
        data = response_pid.json()
        road_name = []
        for loc in data['snappedPoints']:
            place_id = loc["placeId"]
            road_name_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name&key={api_key}"
            response_pname = requests.get(road_name_url)
            data = response_pname.json()
            if data['result']['name'] == 'Unnamed Road':
                road_name.append('')
            else:
                road_name.append(data['result']['name'])
        return ", ".join(road_name)


    def finding_landmark(row, value):
        lat, lon = row['st_Lat_Long_Auth'].split(',')
        place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=100&type=establishment&key={api_key}"
        response = requests.get(place_url)
        data = response.json()
        landmark = []
        for r in data['results']:
            landmark.append(r['name'])
        if value == 'name':
            return ', '.join(landmark)


    def finding_village(row):
        lat1, lon1 = row['st_Lat_Long_Auth'].split(',')
        place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat1},{lon1}&radius=20&key={api_key}"
        response_1 = requests.get(place_url)
        data_1 = response_1.json()
        lat2, lon2 = row['end_Lat_Long_Auth'].split(',')
        place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat2},{lon2}&radius=20&key={api_key}"
        response_2 = requests.get(place_url)
        data_2 = response_2.json()
        name = []
        for r in data_1['results']:
            name.append(r['name'])
        for r in data_2['results']:
            name.append(r['name'])
        return ', '.join(name)


    row_pre_survey_temp = row_pre_survey

    row_pre_survey['NHSHNo'] = row_pre_survey_temp.apply(finding_road_name, axis=1)
    row_pre_survey['LandmarkRHS'] = row_pre_survey_temp.apply(finding_landmark, axis=1)
    row_pre_survey['VlgTwnPoint'] = row_pre_survey_temp.apply(finding_village, axis=1)
    row_pre_survey['NearestLandmark'] = row_pre_survey_temp.apply(finding_landmark, axis=1)
    row_pre_survey['LatLandmark'] = row_pre_survey_temp.apply(finding_landmark, axis=1)
    row_pre_survey['LongLandmark'] = row_pre_survey_temp.apply(finding_landmark, axis=1)

    with pd.ExcelWriter(str(dir_path) + f"/{districtName}-{blockName}-{version}.xlsx", engine='openpyxl',
                        mode='w') as writer:
        row_pre_survey.to_excel(writer, sheet_name='PreSurvey', index=False)
