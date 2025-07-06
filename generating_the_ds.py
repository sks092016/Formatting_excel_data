import pandas as pd
import geopandas as gpd
from math import radians, sin, cos, sqrt, atan2
import tkinter as tk
from tkinter import filedialog
import time
import difflib

root = tk.Tk()
root.withdraw()
######################################### Reference Files ########################################################

base_url = "https://fieldsurvey.rbt-ltd.com/app"
gdf_reference = gpd.read_file("References/tarana_shape_file.shp")

######################################## Reading the Shape File ###################################################

shapefile_path = filedialog.askopenfilename(
    title="Select a shape file",
    filetypes=[("Shape Files", "*.shp"), ("All files", "*.*")]
)
gdf_working = gpd.read_file(shapefile_path)

###################################### Checking the Structure of the Files ########################################

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

###################################### Creating the Details Sheet ##################################################
 def change_point_name(value):
    if str(value).upper() == "RE":
        return 'Road Edge'
    elif str(value).upper() == "RE":
        return 'Culvert Edge'
    elif difflib.SequenceMatcher(None, value.lower(), "culvert").ratio() > 0.6:
        return 'Culvert'
    elif difflib.SequenceMatcher(None, value.lower(), "road").ratio() > 0.6:
        return 'Road'



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


        boq_ds_df['POINT NAME'] = temp_df['end_point_'].apply(change_point_name)
        boq_ds_df['TYPE'] = temp_df['end_point_name'].apply(categorize_value)
        boq_ds_df['POSITION'] = temp_df['ofc_laying']
        boq_ds_df['OFFSET'] = 'NA'
        boq_ds_df['SPAN_CONTINUITY'] = temp_df['SEQ']
        boq_ds_df['CHAINAGE'] = pd.DataFrame([0.0] + [sum(list(temp_df['distance'])[:i + 1]) for i in range(1, len(list(temp_df['distance'])))]).values
        boq_ds_df['DISTENCE(M)'] = temp_df['distance']
        boq_ds_df['START_COORDINATE'] = temp_df['start_loc_cordinate']
        boq_ds_df['CROSSING_START'] = temp_df['crossing_Start']
        boq_ds_df['CROSSING_END'] = temp_df['crossing_end']
        boq_ds_df['END_COORDINATE'] = temp_df['end_loca_coordinate']
        boq_ds_df['ROUTE NAME'] = temp_df['span_name']
        boq_ds_df['ROUTE TYPE'] = temp_df['scope']
        boq_ds_df['OFC TYPE'] = '24F'
        boq_ds_df['LAYING TYPE'] = 'UG'
        boq_ds_df['ROUTE ID'] = temp_df['span_id']
        boq_ds_df['ROUTE MARKER'] = 'NOT VISIBLE'
        boq_ds_df['MANHOLE'] = 'NOT VISIBLE'
        boq_ds_df['ROAD NAME'] = temp_df['road_name']
        boq_ds_df['ROAD WIDTH(m)'] = temp_df.apply(calculate_road_width, axis=1)
        boq_ds_df['ROAD SURFACE'] = temp_df['road_surfa']
        boq_ds_df['OFC POSITION'] = temp_df['ofc_laying']
        boq_ds_df['APRX DISTANCE FROM RCL(m)'] = 'NA'
        boq_ds_df['AUTHORITY NAME'] = temp_df['road_autho']
        boq_ds_df['ROAD CHAINAGE'] = temp_df.apply(calculate_road_chainage, axis=1)
        boq_ds_df['ROAD STRUTURE TYPE'] = temp_df.apply(calculate_structure, axis=1)
        boq_ds_df['LENGTH (IN Mtr.)'] = temp_df.apply(calculate_xing_length, axis=1)
        boq_ds_df['PROTECTION TYPE'] = temp_df.apply(calculate_protec, axis=1)
        boq_ds_df['PROTECTION FOR'] = temp_df.apply(calculate_structure, axis=1)
        boq_ds_df['PROTECTION LENGTH (IN Mtr.)'] = temp_df.apply(calculate_protec_length, axis=1)
        boq_ds_df['UTILITY NAME'] = "NA"
        boq_ds_df['SIDE OF THE ROAD'] = "NA"
        boq_ds_df['SOIL TYPE'] = temp_df['strata_typ']
        boq_ds_df['TERRAIN'] = temp_df['terrain_ty']
        boq_ds_df['REMARKS'] = "NA"
        boq_ = pd.concat([boq_, boq_ds_df])

    with pd.ExcelWriter('References/Porsa Block/mapped_output_Porsa.xlsx', engine='openpyxl', mode='w') as writer:
        boq_.to_excel(writer, sheet_name='Details Sheet', index=False)




# def finding_utility_lhs(row):
#     if row['OFC POSITION'] == 'LHS':
#         if 'rjil' in str(row['POINT NAME']).lower():
#             return "Reliance Jio"
#         elif 'airtel' in str(row['POINT NAME']).lower():
#             return "Airtel"
#         elif 'bsnl' in str(row['POINT NAME']).lower():
#             return 'BSNL'
#         elif 'gas' in str(row['POINT NAME']).lower():
#             return 'Gas PipeLine ' + str(row['POINT NAME'])
#         elif 'hpcl' in str(row['POINT NAME']).lower():
#             return 'HPCL Pipeline'
#         elif 'iocl' in str(row['POINT NAME']).lower():
#             return 'IOCL Pipeline'
#         elif 'railway' in str(row['POINT NAME']).lower():
#             return 'railway'
#         elif 'petrol' in str(row['POINT NAME']).lower():
#             return 'Petroleum Pipeline ' + str(row['POINT NAME'])
#         elif 'gail' in str(row['POINT NAME']).lower():
#             return 'Gail Xing'
#     else:
#         return 'NA'
#
#
# def finding_utility_rhs(row):
#     if row['OFC POSITION'] == 'RHS':
#         if 'rjil' in str(row['POINT NAME']).lower():
#             return "Reliance Jio"
#         elif 'airtel' in str(row['POINT NAME']).lower():
#             return "Airtel"
#         elif 'bsnl' in str(row['POINT NAME']).lower():
#             return 'BSNL'
#         elif 'gas' in str(row['POINT NAME']).lower():
#             return 'Gas PipeLine ' + str(row['POINT NAME'])
#         elif 'hpcl' in str(row['POINT NAME']).lower():
#             return 'HPCL Pipeline'
#         elif 'iocl' in str(row['POINT NAME']).lower():
#             return 'IOCL Pipeline'
#         elif 'railway' in str(row['POINT NAME']).lower():
#             return 'railway'
#         elif 'petrol' in str(row['POINT NAME']).lower():
#             return 'Petroleum Pipeline ' + str(row['POINT NAME'])
#         elif 'gail' in str(row['POINT NAME']).lower():
#             return 'Gail Xing'
#     else:
#         return 'NA'
#
#
# def utility_checked(row):
#     value = row['POINT NAME']
#     if any(sub in value.lower() for sub in ['rjil', 'airtel', 'bsnl', 'gas', 'hpcl', 'iocl', 'adani', 'railway', 'petrol', 'gail']):
#         return "Route Marker"
#     else:
#         return "NA"
#
#
# def road_authority(row):
#     if 'pmgy' in str(row['AUTHORITY NAME']).lower():
#         return f"PMGSY-{str(row['ROAD NAME']).upper()} (MPRRDA)"
#     elif 'pwd' in str(row['AUTHORITY NAME']).lower() or 'sh' in str(row['AUTHORITY NAME']).lower() or 'odr' in str(row['AUTHORITY NAME']).lower():
#         return f"PWD-(Ujjain)"
#     elif 'NHAI' in str(row['AUTHORITY NAME']).lower():
#         return f"NHAI-Ujjain"
#     elif 'nagar' in str(row['AUTHORITY NAME']).lower():
#         return f"Nagar Parishad-Tarana"
#     else:
#         return row['AUTHORITY NAME']
#
#
# def road_auth_add(row):
#     if 'pmgy' in str(row['AUTHORITY NAME']).lower():
#         return f"General Manager, (PMGSY) MPRRDA, Ujjain"
#     elif 'pwd' in str(row['AUTHORITY NAME']).lower() or 'sh' in str(row['AUTHORITY NAME']).lower() or 'odr' in str(row['AUTHORITY NAME']).lower():
#         return f"Executive Engineer,  PWD-(Ujjain)"
#     elif 'NHAI' in str(row['AUTHORITY NAME']).lower():
#         return f"Project Director, NHAI-Ujjain"
#     elif 'nagar' in str(row['AUTHORITY NAME']).lower():
#         return f"CMO, Nagar Parishad-Tarana"
#     else:
#         return f"{row['AUTHORITY NAME']}, Ujjain"
#
#
# def nearest_landmark(value):
#     if any(sub in value.lower() for sub in ['school', 'college', 'temple', 'gp', 'gram', 'kms']):
#         return value.upper()
#     else:
#         return "NA"
#
#
# def calculate_structure(row):
#     structure = ''
#     if 'cul' in str(row['POINT NAME']).lower():
#         structure = 'CULVERT'
#     elif 'bri' in str(row['POINT NAME']).lower():
#         structure = 'BRIDGE'
#     elif 'canal' in str(row['POINT NAME']).lower():
#         structure = 'CANAL'
#     else:
#         structure = ''
#     return structure
#
#
# def structure_xing_lat(row):
#     if any(sub in str(row['POINT NAME']).lower() for sub in ['cul', 'bri', 'canal']):
#         try:
#             return str(row['CROSSING_START']).strip('POINT()').split(' ')[1]
#         except:
#             return 'NA'
#     else:
#         return "NA"
#
#
# def structure_xing_long(row):
#     if any(sub in str(row['POINT NAME']).lower() for sub in ['cul', 'bri', 'canal']):
#         try:
#             return str(row['CROSSING_END']).strip('POINT()').split(' ')[0]
#         except:
#             return 'NA'
#     else:
#         return "NA"
#
#
# def landmark_lat(value):
#     try:
#         return value.strip('POINT()').split(' ')[1]
#     except:
#         return "NA"
#
#
# def landmark_long(value):
#     try:
#         return value.strip('POINT()').split(' ')[0]
#     except:
#         return "NA"
#
#
# def landmark(value):
#     if any(sub not in str(value).lower() for sub in
#            ['cul', 'bri', 'canal', 'rjil', 'airtel', 'bsnl', 'gas', 'hpcl', 'iocl', 'railway', 'petroleum', 'gail', 'rod', 'road', 'kacha']):
#         return str(value).upper()
#     else:
#         return ""
#
# def categorize_value(value):
#     value = str(value)  # Ensure value is string
#     if any(sub in value.lower() for sub in ['re', 're ']):  # Check for 'Re' or 'RE'
#         return 'CROSSING'
#     elif any(sub in value.lower() for sub in ['cul', 'culvert', 'bridge', 'canal']):  # Check for 'cul', 'Culvert', 'Bridge'
#         return 'ROAD STRUCTURE'
#     elif any(
#             sub in value.lower() for sub in ['gp', 'gram panchyat', 'grampanchayat']):  # Check for 'GP', 'Gp', etc.
#         return 'ASSET'
#     else:
#         return 'LANDMARK'
#
#
# def haversine_distance(lat1, lon1, lat2, lon2):
#     """Calculate the distance between two lat-long points using the Haversine formula."""
#     # Convert latitude and longitude to radians
#     lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
#     # Haversine formula
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))
#     r = 6371e3  # Earth's radius in meters
#     return c * r
#
#
# def calculate_road_width(row):
#     re1 = row['road_edge_'].strip('POINT()').split(' ')
#     re2 = row['road_edg_3'].strip('POINT()').split(' ')
#     road_width = haversine_distance(re1[1], re1[0], re2[1], re2[0])
#     return road_width
#
#
# def calculate_road_chainage(row):
#     chainage = ''
#     if 'kms' in str(str(row['end_point_name'])).lower():
#         chainage = str(row['end_point_name']) + ", https://fieldsurvey.rbt-ltd.com/app/" + row['end_loca_phpto']
#     else:
#         chainage = 'NA'
#     return chainage
#
#
# def calculate_structure(row):
#     structure = ''
#     if 'cul' in str(row['end_point_name']).lower():
#         structure = 'CULVERT'
#     elif 'bri' in str(row['end_point_name']).lower():
#         structure = 'BRIDGE'
#     elif 'canal' in str(row['end_point_name']).lower():
#         structure = 'CANAL'
#     else:
#         structure = ''
#     return structure
#
#
# def calculate_xing_length(row):
#     xing_length = 0
#     if 'cul' in str(row['end_point_name']).lower() or 'bri' in str(row['end_point_name']).lower() or 'canal' in str(row['end_point_name']).lower():
#         xing1 = row['crossing_Start'].strip('POINT()').split(' ')
#         xing2 = row['crossing_end'].strip('POINT()').split(' ')
#         xing_length = haversine_distance(xing1[1], xing1[0], xing2[1], xing2[0])
#     return xing_length
#
#
# def calculate_protec(row):
#     protection = ''
#     if 'cul' in str(row['end_point_name']).lower():
#         protection = 'DWC+PCC'
#     elif 'bri' in str(row['end_point_name']).lower() or 'canal' in str(row['end_point_name']).lower():
#         protection = 'GI+PCC'
#     else:
#         protection = ''
#     return protection
#
#
# def calculate_protec_length(row):
#     xing_length = 0
#     if 'cul' in str(row['end_point_name']).lower() or 'bri' in str(row['end_point_name']).lower() or 'canal' in str(row['end_point_name']).lower():
#         xing1 = row['crossing_Start'].strip('POINT()').split(' ')
#         xing2 = row['crossing_end'].strip('POINT()').split(' ')
#         xing_length = haversine_distance(xing1[1], xing1[0], xing2[1], xing2[0])
#         return xing_length + 2
#     else:
#         return 0
#
# def change_point_name(value):
#     if str(value).upper() == "RE":
#         return 'ROAD CROSS EDGE'
#     else:
#         return str(value).upper()
#
# def categorize_value(value):
#     value = str(value)  # Ensure value is string
#     if any(sub in value.lower() for sub in ['re', 're ']):  # Check for 'Re' or 'RE'
#         return 'CROSSING'
#     elif any(sub in value.lower() for sub in ['cul', 'culvert', 'bridge', 'canal']):  # Check for 'cul', 'Culvert', 'Bridge'
#         return 'ROAD STRUCTURE'
#     elif any(
#             sub in value.lower() for sub in ['gp', 'gram panchyat', 'grampanchayat']):  # Check for 'GP', 'Gp', etc.
#         return 'ASSET'
#     else:
#         return 'LANDMARK'
#
#
# def haversine_distance(lat1, lon1, lat2, lon2):
#     """Calculate the distance between two lat-long points using the Haversine formula."""
#     # Convert latitude and longitude to radians
#     lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
#     # Haversine formula
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))
#     r = 6371e3  # Earth's radius in meters
#     return c * r
#
#
# def calculate_road_width(row):
#     re1 = row['road_edge_'].strip('POINT()').split(' ')
#     re2 = row['road_edg_3'].strip('POINT()').split(' ')
#     road_width = haversine_distance(re1[1], re1[0], re2[1], re2[0])
#     return road_width
#
#
# def calculate_road_chainage(row):
#     chainage = ''
#     if 'kms' in str(str(row['end_point_name'])).lower():
#         chainage = str(row['end_point_name'])
#     else:
#         chainage = 'NA'
#     return chainage
#
#
# def calculate_structure(row):
#     structure = ''
#     if 'cul' in str(row['end_point_name']).lower():
#         structure = 'CULVERT'
#     elif 'bri' in str(row['end_point_name']).lower():
#         structure = 'BRIDGE'
#     elif 'canal' in str(row['end_point_name']).lower():
#         structure = 'CANAL'
#     else:
#         structure = ''
#     return structure
#
#
# def calculate_xing_length(row):
#     xing_length = 0
#     if 'cul' in str(row['end_point_name']).lower() or 'bri' in str(row['end_point_name']).lower() or 'canal' in str(row['end_point_name']).lower():
#         xing1 = row['crossing_Start'].strip('POINT()').split(' ')
#         xing2 = row['crossing_end'].strip('POINT()').split(' ')
#         xing_length = haversine_distance(xing1[1], xing1[0], xing2[1], xing2[0])
#     return xing_length
#
#
# def calculate_protec(row):
#     protection = ''
#     if 'cul' in str(row['end_point_name']).lower():
#         protection = 'DWC+PCC'
#     elif 'bri' in str(row['end_point_name']).lower() or 'canal' in str(row['end_point_name']).lower():
#         protection = 'GI+PCC'
#     else:
#         protection = ''
#     return protection
#
#
# def calculate_protec_length(row):
#     xing_length = 0
#     if 'cul' in str(row['end_point_name']).lower() or 'bri' in str(row['end_point_name']).lower() or 'canal' in str(row['end_point_name']).lower():
#         xing1 = row['crossing_Start'].strip('POINT()').split(' ')
#         xing2 = row['crossing_end'].strip('POINT()').split(' ')
#         xing_length = haversine_distance(xing1[1], xing1[0], xing2[1], xing2[0])
#         return xing_length + 2
#     else:
#         return 0
#
# def change_point_name(value):
#     if str(value).upper() == "RE":
#         return 'ROAD CROSS EDGE'
#     else:
#         return str(value).upper()
#
# def calculate_cordinate(row):
#     return f"POINT({str(row['lat'])} {str(row['lat'])})"
#
# def finding_utility(row):
#     if 'rjil' in str(row['end_point_name']).lower():
#         return "Reliance Jio"
#     elif 'airtel' in str(row['end_point_name']).lower():
#         return "Airtel"
#     elif 'bsnl' in str(row['end_point_name']).lower():
#         return 'BSNL'
#     elif 'gas' in str(row['end_point_name']).lower():
#         return 'Gas PipeLine'
#     elif 'hpcl' in str(row['end_point_name']).lower():
#         return 'HPCL Pipeline'
#     elif 'iocl' in str(row['end_point_name']).lower():
#         return 'IOCL Pipeline'
#     else:
#         return ''
#
# def calc_len(row):
#     value = str(row['end_point_name'])
#     if any(sub in value.lower() for sub in ['cul', 'culvert', 'bridge', 'canal']):
#         return row['crossing_l']
#     else:
#         return ''
#
# def calc_len_proc(row):
#     value = str(row['end_point_name'])
#     if any(sub in value.lower() for sub in ['cul', 'culvert', 'bridge', 'canal']):
#         return row['crossing_l'] + 2
#     else:
#         return 0
#
#


#
# #################################################################################################################
#
# survey = pd.read_excel('References/Tarana Block/Tarana_block_survey.xlsx', sheet_name='Sheet1')
# cols = ['FROM','TO','ROUTE NAME','RING NO.','ROUTE TYPE','OFC TYPE','LAYING TYPE','ROUTE ID','TOTAL LENGTH(KM)','OH','UG']
# span_details = pd.DataFrame(columns = cols)
#
# span_ = survey[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
# span_dis= survey.groupby('span_name').agg({'distance': 'sum'})
# merged_df = pd.merge(span_, span_dis, on=['span_name'], how='inner')
#
# span_details['FROM'] = merged_df['from_gp_na']
# span_details['TO'] = merged_df['to_gp_name']
# span_details['ROUTE NAME'] = merged_df['span_name']
# span_details['RING NO.'] = merged_df['ring_no']
# span_details['ROUTE TYPE'] = merged_df['scope']
# span_details['OFC TYPE'] = '48F'
# span_details['LAYING TYPE'] = 'UG'
# span_details['ROUTE ID'] = merged_df['span_id']
# span_details['TOTAL LENGTH(KM)'] = merged_df['distance']
# span_details['OH'] = 0
# span_details['UG'] = merged_df['distance']
#
#
# with pd.ExcelWriter('References/Tarana Block/Tarana-BoQ.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
#     span_details.to_excel(writer, sheet_name='Span Details', index=False)
#
# ####################################################################################################################
#
# import pandas as pd
#
# def finding_pipeline(row, df, auth):
#     span_ = row['span_name']
#     df = df[df.span_name == span_]
#     count = df['end_point_'].str.contains(auth,case=False, na=False).sum()
#     return count
# def finding_xing_length(row, df, auth):
#     span_ = row['span_name']
#     df = df[df.span_name == span_]
#     mask = df['end_point_'].str.contains(auth,case=False, na=False)
#     length = df.loc[mask, 'crossing_l'].sum()
#     return length
#
# _survey = pd.read_excel('References/Tarana Block/Tarana_block_survey.xlsx', sheet_name='Sheet1')
# cols = ['ROUTE NAME','ROUTE TYPE','RING NO','ROUTE ID','TOTAL ROUTE LENGTH','NHAI','PWD NH','PWD','NAGAR PARISHAD','GP','MPRRDA','MUNICIPALITY','FOREST','SH','ODR','RAILWAY XINGS(LEN)',
# 'RAILWAY XINGS(NOs)','GAS XING(LEN)','GAS XING(NOs)','ADANI XING(LEN)','ADANI XING(NOs)','IOCL XING(LEN)','IOCL XING(NOs)','HPCL XING(LEN)','HPCL XING(NOs)','OTHERS']
#
# row_details = pd.DataFrame(columns = cols)
#
# span_ = _survey[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
# span_dis= _survey.groupby('span_name').agg({'distance': 'sum'})
# merged_df = pd.merge(span_, span_dis, on=['span_name'], how='inner')
# df2 = _survey.pivot_table(values='distance', index='span_name', columns='road_autho', aggfunc='sum', fill_value=0).reset_index()
# row_ = pd.merge(merged_df, df2, on=['span_name'], how='inner')
#
# row_details['ROUTE NAME'] = row_['span_name']
# row_details['ROUTE TYPE'] = row_['scope']
# row_details['RING NO'] = row_['ring_no']
# row_details['ROUTE ID'] = row_['span_id']
# row_details['TOTAL ROUTE LENGTH'] = row_['distance']
# row_details['NHAI'] = row_['NHAI']
# row_details['PWD NH'] = 0
# row_details['PWD'] = row_['PWD']
# row_details['NAGAR PARISHAD'] = row_['Nagar Parishad']
# row_details['GP'] = row_['Grampanchyat']
# row_details['SH'] = row_['SH']
# row_details['ODR'] = row_['ODR']
# row_details['MPRRDA'] = row_['PMGY']
# row_details['MUNICIPALITY'] = 0
# row_details['FOREST'] = row_['Forest']
# row_details['RAILWAY XINGS(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'railway'))
# row_details['RAILWAY XINGS(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'railway'))
# row_details['GAS XING(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'gas'))
# row_details['GAS XING(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'gas'))
# row_details['ADANI XING(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'adani'))
# row_details['ADANI XING(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'adani'))
# row_details['IOCL XING(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'iocl'))
# row_details['IOCL XING(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'iocl'))
# row_details['HPCL XING(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'hpcl'))
# row_details['HPCL XING(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'hpcl'))
# row_details['OTHERS'] = 0
#
# with pd.ExcelWriter('References/Tarana Block/Tarana-BoQ.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
#     row_details.to_excel(writer, sheet_name='RoW', index=False)
#
# ###################################################################################################################################
#
#
# import pandas as pd
# cols = ['ROUTE NAME','ROUTE TYPE','TOTAL ROUTE LENGTH','NO OF CULVERT','LENGTH (IN Mtr) OF CULVERT','NO OF BRIDGE','LENGTH (IN Mtr) OF BRIDE',
# 'LENGTH (IN Mtr) OF PCC','LENGTH (IN Mtr) OF DWC','LENGTH (IN Mtr) OF GI','LENGTH (IN Mtr) OF DWC+PCC','LENGTH (IN Mtr) OF ANCORING']
# protection_details = pd.DataFrame(columns = cols)
#
# survey = pd.read_excel('References/Porsa Block/porsa_block_survey_data.xlsx', sheet_name='Sheet1')
# span_ = survey[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
# span_dis = survey.groupby('span_name').agg({'distance': 'sum'})
# merged_df = pd.merge(span_, span_dis, on=['span_name'], how='inner')
#
# _details = pd.read_excel('References/Porsa Block/Porsa-BoQ.xlsx', sheet_name='Details Sheet')
#
# _protection = _details[['ROUTE NAME', 'ROAD STRUTURE TYPE', 'LENGTH (IN Mtr.)', 'PROTECTION TYPE','PROTECTION FOR', 'PROTECTION LENGTH (IN Mtr.)']]
#
# r_agg = _protection.groupby(['ROUTE NAME', 'ROAD STRUTURE TYPE'])['LENGTH (IN Mtr.)'].agg(['count', 'sum']).unstack(fill_value=0)
# r_agg.columns = ['NO OF BRIDGE','NO OF CULVERT', 'LENGTH (IN Mtr) OF BRIDGE','LENGTH (IN Mtr) OF CULVERT']  # Rename columns
# r_agg = r_agg.reset_index()
# p_agg = _protection.pivot_table(values='PROTECTION LENGTH (IN Mtr.)', index='ROUTE NAME', columns='PROTECTION TYPE', aggfunc='sum', fill_value=0).reset_index()
# protection_ = pd.merge(r_agg, p_agg, on= 'ROUTE NAME', how='outer')
#
# merged_df.rename(columns={'span_name' : 'ROUTE NAME'} ,inplace=True)
# protection_ = pd.merge(protection_, merged_df, on='ROUTE NAME', how='outer')
#
# protection_details['ROUTE NAME'] = protection_['ROUTE NAME']
# protection_details['ROUTE TYPE'] = protection_['scope']
# protection_details['TOTAL ROUTE LENGTH'] = protection_['distance']
# protection_details['NO OF CULVERT'] = protection_['NO OF CULVERT']
# protection_details['LENGTH (IN Mtr) OF CULVERT'] = protection_['LENGTH (IN Mtr) OF CULVERT']
# protection_details['NO OF BRIDGE'] = protection_['NO OF BRIDGE']
# protection_details['LENGTH (IN Mtr) OF BRIDE'] = protection_['LENGTH (IN Mtr) OF BRIDGE']
# protection_details['LENGTH (IN Mtr) OF PCC'] = 0
# protection_details['LENGTH (IN Mtr) OF DWC'] = protection_['NO OF CULVERT'] * 6 + protection_['LENGTH (IN Mtr) OF CULVERT']
# protection_details['LENGTH (IN Mtr) OF GI'] = protection_['NO OF BRIDGE'] * 6 + protection_['LENGTH (IN Mtr) OF BRIDGE']
# protection_details['LENGTH (IN Mtr) OF DWC+PCC'] = protection_['DWC+PCC']
#
# protection_details['LENGTH (IN Mtr) OF ANCORING'] = 0
#
# with pd.ExcelWriter('References/Porsa Block/Porsa-BoQ.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
#     protection_details.to_excel(writer, sheet_name='Protection Details', index=False)
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