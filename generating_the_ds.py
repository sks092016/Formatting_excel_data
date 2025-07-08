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

root = tk.Tk()
root.withdraw()

######################################### CONSTANTS #############################################################
#ROAD WIDTHS
PMGY = 4
SH = 15
NH = 40
Grampanchyat = GP = 6
PWD = 6
ODR = 6
MDR = 6
Nagar_Parishad = 4
OTHERS = 6

#RM & MH INTERVAL
rm_interval = 200
mh_interval = 1800

#PROTECTION
culvert_protection = 'DWC + PCC'
bridge_protection = 'GI + Clamping'
hard_rock = 'DWC + PCC'

#VERSION
version = 1.0

#PATH
folder_path = 'D:\\bharat_net_data\\'

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
blockName =  gdf_working['block_name'][0]
districtName = gdf_working['district_n'][0]

dir_path = Path(folder_path + districtName +"-"+ blockName + version)

# If it exists, delete it
if dir_path.exists() and dir_path.is_dir():
    shutil.rmtree(dir_path)  # Deletes the entire folder and its contents

# Now create it fresh
dir_path.mkdir(parents=True, exist_ok=False)
###################################### Checking the Structure of the Files #######################################

is_structure_same = set(gdf_reference.columns) == set(gdf_working.columns)
if not is_structure_same:
    col_diff = set(gdf_reference.columns) - set(gdf_working.columns)
    print("The Structure of the shape file is not matching the reference structure aborting. \n")
    time.sleep(0.5)
    print("Following columns are not present in the selected shape file:\n")
    time.sleep(0.5)
    print(col_diff)
else:
    print(gdf_working.columns)
###################################### Creating the Common Span Details #########################################

span_ = gdf_working[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
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
    if any(sub in value.lower() for sub in ['re', 're ',  ' re']):
        return 'Road Edge'
    elif str(value).upper() == "SE":
        return 'Segment Edge'
    elif difflib.SequenceMatcher(None, value.lower(), "culvert").ratio() > 0.5:
        return 'Culvert'
    elif difflib.SequenceMatcher(None, value.lower(), "bridge").ratio() > 0.5:
        return 'Bridge'
    else:
        return value.capitalize()

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
    if any(sub in value for sub in ['PMGY', 'SH', 'NH', 'Nagar Parishad', 'Grampanchyat', 'GP', 'PWD', 'ODR', 'MDR']):
        value = globals()[value]
        if param == 'offset':
            return value/2 + 0.2 * value
        if param == 'width':
            return value
    else:
        if param == 'offset':
            return OTHERS / 2 + 0.2 * OTHERS
        if param == 'width':
            return OTHERS
    return None

def finding_lat_lon(row,lat_lon):
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


def calculating_rms(row, df):
    # Track cumulative distances
    cum_distance_start = 0
    rm_list = []
    for d in df['Distance']:
        cum_distance_end = cum_distance_start + d
        # Count new RMs in this segment
        rm_start_count = cum_distance_start // rm_interval
        rm_end_count = cum_distance_end // rm_interval
        new_rms = int(rm_end_count - rm_start_count)
        rm_list.append(new_rms)
        cum_distance_start = cum_distance_end
    return rm_list

def calculating_mhs(row, df):
    cum_distance_start = 0
    mh_list = []
    for d in df['Distance']:
        cum_distance_end = cum_distance_start + d
        # Count new MHs in this segment
        mh_start_count = cum_distance_start // mh_interval
        mh_end_count = cum_distance_end // mh_interval
        new_mhs = int(mh_end_count - mh_start_count)
        mh_list.append(new_mhs)
        cum_distance_start = cum_distance_end
    return mh_list

def calculate_road_chainage(row):
    chainage = ''
    if 'kms' in str(str(row['end_point_'])).lower():
        chainage = str(row['end_point_'])
    else:
        chainage = ''
    return chainage

def calculate_protec(row, param):
    value = str(row['end_point_'])
    length = float(row['distance'])
    strata = str(row['strata_typ'])
    if difflib.SequenceMatcher(None, value.lower(), "culvert").ratio() > 0.5 and length <= 20:
        if param == 'struct' or 'for':
            return 'Culvert'
        if param == 'type':
            return culvert_protection
        if param == 'length':
            return length + 6
    elif difflib.SequenceMatcher(None, value.lower(), "bridge").ratio() > 0.5 and length > 20:
        if param == 'struct' or 'for':
            return 'Bridge'
        if param == 'type':
            return bridge_protection
        if param == 'length':
            return length + 6
    elif strata == 'hard_rock':
        if param == 'for':
            return 'Hard Rock'
        if param == 'length':
            return length + 6
    return ''

def finding_utility(row):
    side = row['ofc_laying']
    value = str(row['end_point_']).lower()
    if row['ofc_laying'] == 'LHS':
        if 'rjil' in value:
            return "Reliance Jio"
        elif 'airtel' in value:
            return "Airtel"
        elif 'bsnl' in value:
            return 'BSNL'
        elif 'gas' in value:
            return 'Gas PipeLine ' + value
        elif 'hpcl' in value:
            return 'HPCL Pipeline'
        elif 'iocl' in value:
            return 'IOCL Pipeline'
        elif 'railway' in value:
            return 'railway'
        elif 'petrol' in value:
            return 'Petroleum Pipeline ' + value
        elif 'gail' in value:
            return 'Gail Xing'
    return None

if is_structure_same:
    cols= ['SPAN_CONTINUITY', 'POINT NAME','TYPE','POSITION','OFFSET','CHAINAGE','DISTENCE(M)','LATITUDE',"LONGITUDE",'ROUTE NAME','ROUTE TYPE',
           'OFC TYPE','LAYING TYPE','ROUTE ID','ROUTE MARKER','MANHOLE','ROAD NAME','ROAD WIDTH(m)','ROAD SURFACE','OFC POSITION','APRX DISTANCE FROM RCL(m)',
           'AUTHORITY NAME','ROAD CHAINAGE','ROAD STRUTURE TYPE','LENGTH (IN Mtr.)','PROTECTION TYPE','PROTECTION FOR','PROTECTION LENGTH (IN Mtr.)','UTILITY NAME',
           'SIDE OF THE ROAD','SOIL TYPE','REMARKS']

    boq_details_sheet = pd.DataFrame(columns=cols)
    span = gdf_working.sort_values('span_name').span_name.unique()
    for s in span:
        print(s)
        temp_df = gdf_working[gdf_working.span_name == s].sort_values('Sequqnce')
        boq_ds_df = pd.DataFrame(columns=cols)
        boq_ds_df['SPAN_CONTINUITY'] = temp_df['Sequqnce']
        boq_ds_df['POINT NAME'] = temp_df['end_point_'].apply(change_point_name)
        boq_ds_df['TYPE'] = temp_df['end_point_name'].apply(categorize_value)
        boq_ds_df['POSITION'] = temp_df['ofc_laying']
        boq_ds_df['OFFSET'] = temp_df.apply(calculate_offset_width, axis=1, args=('offset'))
        boq_ds_df['CHAINAGE'] = temp_df['distance'].cumsum().shift(fill_value=0)
        boq_ds_df['DISTENCE(M)'] = temp_df['distance']
        boq_ds_df['LATITUDE'] = temp_df.apply(finding_lat_lon, axis=1, args=('lat'))
        boq_ds_df['LONGITUDE'] = temp_df.apply(finding_lat_lon, axis=1, args=('lon'))
        boq_ds_df['ROUTE NAME'] = temp_df['span_name']
        boq_ds_df['ROUTE TYPE'] = temp_df['scope']
        boq_ds_df['OFC TYPE'] = '48F'
        boq_ds_df['LAYING TYPE'] = 'UG'
        boq_ds_df['ROUTE ID'] = temp_df['span_id']
        boq_ds_df['ROUTE MARKER'] = temp_df.apply(calculating_rms, axis=1, args=(temp_df))
        boq_ds_df['MANHOLE'] = temp_df.apply(calculating_mhs, axis=1, args=(temp_df))
        boq_ds_df['ROAD NAME'] = temp_df['road_name']
        boq_ds_df['ROAD WIDTH(m)'] = temp_df.apply(calculate_offset_width, axis=1, args=('width'))
        boq_ds_df['ROAD SURFACE'] = temp_df['road_surfa']
        boq_ds_df['OFC POSITION'] = temp_df['ofc_laying']
        boq_ds_df['APRX DISTANCE FROM RCL(m)'] = ''
        boq_ds_df['AUTHORITY NAME'] = temp_df['road_autho']
        boq_ds_df['ROAD CHAINAGE'] = temp_df.apply(calculate_road_chainage, axis=1)
        boq_ds_df['ROAD STRUTURE TYPE'] = temp_df.apply(calculate_protec, axis=1, args=('struct'))
        boq_ds_df['LENGTH (IN Mtr.)'] = temp_df['distance']
        boq_ds_df['PROTECTION TYPE'] = temp_df.apply(calculate_protec, axis=1, args=('type'))
        boq_ds_df['PROTECTION FOR'] = temp_df.apply(calculate_protec, axis=1, args=('for'))
        boq_ds_df['PROTECTION LENGTH (IN Mtr.)'] = temp_df.apply(calculate_protec, axis=1, args=('len'))
        boq_ds_df['UTILITY NAME'] = temp_df.apply(finding_utility, axis=1)
        boq_ds_df['SIDE OF THE ROAD'] = temp_df['ofc_laying'] if boq_ds_df['UTILITY NAME'] else None
        boq_ds_df['SOIL TYPE'] = temp_df['strata_typ']
        boq_ds_df['REMARKS'] = "NA"
        boq_ = pd.concat([boq_, boq_ds_df])

    with pd.ExcelWriter(str(dir_path)+f"\\{districtName}-{blockName}-{version}.xlsx", engine='openpyxl', mode='w') as writer:
        boq_.to_excel(writer, sheet_name='Details Sheet', index=False)

# ############################################## Generating the Span Details ########################################

cols = ['FROM','TO','ROUTE NAME','RING NO.','ROUTE TYPE','OFC TYPE','LAYING TYPE','ROUTE ID','TOTAL LENGTH(KM)','OH','UG']
span_details = pd.DataFrame(columns = cols)

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

with pd.ExcelWriter(str(dir_path)+f"\\{districtName}-{blockName}-{version}.xlsx", engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    span_details.to_excel(writer, sheet_name='Span Details', index=False)

# ############################################# Generating the RoW Details #########################################

authorities = gdf_working['road_autho'].unique()

cols = ['ROUTE NAME','ROUTE TYPE','RING NO','ROUTE ID','TOTAL ROUTE LENGTH'] + authorities

row_details = pd.DataFrame(columns = cols)

df2 = gdf_working.pivot_table(values='distance', index='span_name', columns='road_autho', aggfunc='sum', fill_value=0).reset_index()
row_ = pd.merge(boq_sd_df, df2, on=['span_name'], how='inner')

row_details['ROUTE NAME'] = row_['span_name']
row_details['ROUTE TYPE'] = row_['scope']
row_details['RING NO'] = row_['ring_no']
row_details['ROUTE ID'] = row_['span_id']
row_details['TOTAL ROUTE LENGTH'] = row_['distance']
for auths in authorities:
    row_details[auths] = row_[auths]
row_details['OTHERS'] = 0

with pd.ExcelWriter(str(dir_path)+f"\\{districtName}-{blockName}-{version}.xlsx", engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    row_details.to_excel(writer, sheet_name='RoW', index=False)

####################################### Generating the Protection Details ###########################################

cols = ['ROUTE NAME','ROUTE TYPE','TOTAL ROUTE LENGTH','NO OF CULVERT','LENGTH (IN Mtr) OF CULVERT','NO OF BRIDGE','LENGTH (IN Mtr) OF BRIDE',
'LENGTH (IN Mtr) OF PCC','LENGTH (IN Mtr) OF DWC','LENGTH (IN Mtr) OF GI','LENGTH (IN Mtr) OF DWC+PCC',"Soil Detail", 	"LENGTH (IN Mtr) OF DWC+PCC (HARD ROCK)",'LENGTH (IN Mtr) OF ANCORING']
protection_details = pd.DataFrame(columns = cols)

_details = pd.read_excel(str(dir_path)+f"\\{districtName}-{blockName}-{version}.xlsx", sheet_name='Details Sheet')

_protection = _details[['ROUTE NAME', 'ROAD STRUTURE TYPE', 'LENGTH (IN Mtr.)', 'PROTECTION TYPE','PROTECTION FOR', 'PROTECTION LENGTH (IN Mtr.)']]
r_agg = _protection.groupby(['ROUTE NAME', 'ROAD STRUTURE TYPE'])['LENGTH (IN Mtr.)'].agg(['count', 'sum']).unstack(fill_value=0)
r_agg.columns = ['NO OF BRIDGE','NO OF CULVERT', 'LENGTH (IN Mtr) OF BRIDGE','LENGTH (IN Mtr) OF CULVERT']  # Rename columns
r_agg = r_agg.reset_index()
p_agg = _protection.pivot_table(values='PROTECTION LENGTH (IN Mtr.)', index='ROUTE NAME', columns='PROTECTION TYPE', aggfunc='sum', fill_value=0).reset_index()
protection_ = pd.merge(r_agg, p_agg, on= 'ROUTE NAME', how='outer')

merged_df.rename(columns={'span_name' : 'ROUTE NAME'} ,inplace=True)
protection_ = pd.merge(protection_, merged_df, on='ROUTE NAME', how='outer')

protection_details['ROUTE NAME'] = protection_['ROUTE NAME']
protection_details['ROUTE TYPE'] = protection_['scope']
protection_details['TOTAL ROUTE LENGTH'] = protection_['distance']
protection_details['NO OF CULVERT'] = protection_['NO OF CULVERT']
protection_details['LENGTH (IN Mtr) OF CULVERT'] = protection_['LENGTH (IN Mtr) OF CULVERT']
protection_details['NO OF BRIDGE'] = protection_['NO OF BRIDGE']
protection_details['LENGTH (IN Mtr) OF BRIDE'] = protection_['LENGTH (IN Mtr) OF BRIDGE']
protection_details['LENGTH (IN Mtr) OF PCC'] = 0
protection_details['LENGTH (IN Mtr) OF DWC'] = protection_['NO OF CULVERT'] * 6 + protection_['LENGTH (IN Mtr) OF CULVERT']
protection_details['LENGTH (IN Mtr) OF GI'] = protection_['NO OF BRIDGE'] * 6 + protection_['LENGTH (IN Mtr) OF BRIDGE']
protection_details['LENGTH (IN Mtr) OF DWC+PCC'] = protection_['DWC+PCC']

protection_details['LENGTH (IN Mtr) OF ANCORING'] = 0

with pd.ExcelWriter('References/Porsa Block/Porsa-BoQ.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    protection_details.to_excel(writer, sheet_name='Protection Details', index=False)
#
# ###########################################################################################################################################
#
# cols = ['SrNo', 'FROM  AND TO GP','NHSHNo','RoadWidth','RowBoundaryLmt','KMStoneFromA','KMStoneToB','SuveryDist','LatAuth','LongAuth','LandmarkRHS',
# 'VlgTwnPoint','OFClaying','RdCrossing Req','ReasonRdCrossing','UtilityLHS','UtilityRHS',   'UtilityChecked',   'RowAuthorityName', 'AuthorityAddress', 'FeasibilityOfROWApproval', 'TypeOfOverlapArea',
# 'NearestLandmark', 'LengthOfOverlapArea','ExpansionInProg','ExpansionPlanned','TypeOfCrossing','LatCrossing','LongCrossing','LatLandmark','LongLandmark',
# 'LengthOfCrossing','SoilType','RouteRdSidePts','AlternateReq','AlternateProp','AlternatePathLgh','Remarks']
#
# row_in_dep = pd.DataFrame(columns=cols)
#
#
# row_in_dep['SrNo'] = _ds['SPAN_CONTINUITY']
# row_in_dep['FROM  AND TO GP'] = _ds['ROUTE NAME']
# # row_in_dep['NHSHNo'] = _ds['ROUTE KMS PHOTO']
# row_in_dep['NHSHNo'] = _ds['ROAD CHAINAGE']
# row_in_dep['RoadWidth'] = _ds['ROAD WIDTH(m)']
# row_in_dep['RowBoundaryLmt'] = 'NA'
# row_in_dep['KMStoneFromA'] = 'NA'
# row_in_dep['KMStoneToB'] = _ds['ROAD CHAINAGE']
# row_in_dep['SuveryDist'] = _ds['DISTENCE(M)']
# row_in_dep['LatAuth'] = _ds['START_COORDINATE'].apply(find_lat)
# row_in_dep['LongAuth'] = _ds['START_COORDINATE'].apply(find_long)
# row_in_dep['LandmarkRHS'] = _ds['POINT NAME'].apply(landmark)
# row_in_dep['VlgTwnPoint'] = _ds['ROAD NAME']
# row_in_dep['OFClaying'] = _ds['OFC POSITION']
# row_in_dep['RdCrossing Req'] = _ds['ROAD NAME'].apply(road_xing_req)
# row_in_dep['ReasonRdCrossing'] = _ds['ROAD NAME'].apply(road_xing_reas)
# row_in_dep['UtilityLHS'] = _ds.apply(finding_utility_lhs, axis=1)
# row_in_dep['UtilityRHS'] = _ds.apply(finding_utility_rhs, axis=1)
# row_in_dep['UtilityChecked'] = _ds.apply(utility_checked, axis=1)
# row_in_dep['RowAuthorityName'] = _ds.apply(road_authority, axis=1)
# row_in_dep['AuthorityAddress'] = _ds.apply(road_auth_add, axis=1)
# row_in_dep['FeasibilityOfROWApproval'] = 'Yes'
# row_in_dep['TypeOfOverlapArea'] = 'NA'
# row_in_dep['NearestLandmark'] = _ds['POINT NAME'].apply(nearest_landmark)
# row_in_dep['LengthOfOverlapArea'] = 'NA'
# row_in_dep['ExpansionInProg'] = 'NA'
# row_in_dep['ExpansionPlanned'] = 'NA'
# row_in_dep['TypeOfCrossing'] = _ds.apply(calculate_structure, axis=1)
# row_in_dep['LatCrossing'] = _ds.apply(structure_xing_lat, axis=1)
# row_in_dep['LongCrossing'] = _ds.apply(structure_xing_long, axis=1)
# row_in_dep['LatLandmark'] = _ds['END_COORDINATE'].apply(landmark_lat)
# row_in_dep['LongLandmark'] = _ds['END_COORDINATE'].apply(landmark_long)
# row_in_dep['LengthOfCrossing'] = _ds['LENGTH (IN Mtr.)']
# row_in_dep['SoilType'] = _ds['SOIL TYPE']
# row_in_dep['RouteRdSidePts'] = 'NA'
# row_in_dep['AlternateReq'] = 'NA'
# row_in_dep['AlternateProp'] = 'NA'
# row_in_dep['AlternatePathLgh'] = 'NA'
# row_in_dep['Remarks'] = ''
#
# with pd.ExcelWriter('References/Tarana Block/Tarana_RoW.xlsx', engine='openpyxl', mode='w') as writer:
#     row_in_dep.to_excel(writer, sheet_name='PreSurvey', index=False)