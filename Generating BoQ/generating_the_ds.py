from utils.api_calls import *
from utils.sheet_creations.excel_formatting import *
from utils.sheet_creations.bom_boq import *
from utils.sheet_creations.gpon import *
from utils.sheet_creations.railway_crossing import *
from utils.sheet_creations.gas_xing import *
from utils.sheet_creations.table_b import *
from utils.sheet_creations.annexure_x import *
from utils.sheet_creations.asset_details import *
from utils.sheet_creations.index import *

root = tk.Tk()
root.withdraw()
with open('../References/village_district_code.json', 'r') as f:
    village_data = json.load(f)
######################################### CONSTANTS #############################################################

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

######################################### Reference Files ########################################################

base_url = "https://fieldsurvey.rbt-ltd.com/app"
gdf_reference = gpd.read_file("../References/Formats/OFC_NEW.shp")

######################################## Reading the Shape File ##################################################

shapefile_path = filedialog.askopenfilename(
    title="Select a shape file",
    filetypes=[("Shape Files", "*.shp"), ("All files", "*.*")]
)
gdf_working = gpd.read_file(shapefile_path)

###################################### Creating the Directory for file store #####################################
blockName = gdf_working['block_name'][0]
districtName = gdf_working['district_n'][0]

##################################### Select the Destination Folder ###################################

folder_path = filedialog.askdirectory(title="Select Destination Folder")

dir_path = Path(folder_path) / f"{districtName}-{blockName}-{version}"

# If it exists, delete it
if dir_path.exists() and dir_path.is_dir():
    shutil.rmtree(dir_path)  # Deletes the entire folder and its contents

# Now create it fresh
dir_path.mkdir(parents=True, exist_ok=False)

excel_file = dir_path / f"{districtName}-{blockName}-{version}.xlsx"
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
        temp_df = gdf_working[gdf_working.span_name == s].sort_values('Sequqnce')
        boq_ds_df = pd.DataFrame(columns=cols_ds)
        boq_ds_df['SPAN_CONTINUITY'] = temp_df['Sequqnce']
        boq_ds_df['POINT NAME'] = temp_df['end_point_']
        if 'Type' in temp_df.columns and not temp_df['Type'].isnull().all():
            boq_ds_df['TYPE'] = temp_df['Type']
        else:
            boq_ds_df['TYPE'] = temp_df.apply(categorize_value, axis=1)
        boq_ds_df['POSITION'] = temp_df['ofc_laying']
        if 'ROW_Limit' in temp_df.columns:
            boq_ds_df['OFFSET'] = temp_df['ROW_Limit']
        else:
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
        if 'Road_Width' in temp_df.columns:
            boq_ds_df['ROAD WIDTH(m)'] = temp_df['Road_Width']
        else:
            boq_ds_df['ROAD WIDTH(m)'] = temp_df.apply(calculate_offset_width, axis=1, args=('width',))
        boq_ds_df['ROAD SURFACE'] = temp_df['road_surfa']
        boq_ds_df['OFC POSITION'] = temp_df['ofc_laying']
        if 'ROW_Limit' in temp_df.columns:
            boq_ds_df['APRX DISTANCE FROM RCL(m)'] = temp_df['ROW_Limit']
        else:
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

    with pd.ExcelWriter(excel_file, engine='openpyxl',
                        mode='w') as writer:
        boq_.to_excel(writer, sheet_name='Details Sheet', index=False)
    print('Details Sheet Created')
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
    span_details['TOTAL LENGTH(KM)'] = boq_sd_df['distance'] / 1000
    span_details['OH'] = 0
    span_details['UG'] = boq_sd_df['distance'] / 1000

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a',
                        if_sheet_exists='replace') as writer:
        span_details.to_excel(writer, sheet_name='Span Details', index=False)
    print('Span Details Created')
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
    row_details['TOTAL ROUTE LENGTH'] = row_['distance'] / 1000
    for auths in authorities:
        row_details[auths] = row_[auths] / 1000
    row_details['OTHERS'] = 0

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a',
                        if_sheet_exists='replace') as writer:
        row_details.to_excel(writer, sheet_name='RoW', index=False)
    print('RoW Summery Created')
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
    protection_details['TOTAL ROUTE LENGTH'] = protection_['distance'] / 1000
    protection_details['NO OF CULVERT'] = protection_['NO OF CULVERT']
    protection_details['LENGTH (IN Mtr) OF CULVERT'] = protection_['LENGTH (IN Mtr) OF CULVERT'].astype(float) - 6 * protection_[
        'NO OF CULVERT'].astype(float)
    protection_details['NO OF BRIDGE'] = protection_['NO OF BRIDGE']
    protection_details['LENGTH (IN Mtr) OF BRIDE'] = protection_['LENGTH (IN Mtr) OF BRIDGE'].astype(float) - 6 * protection_[
        'NO OF BRIDGE'].astype(float)
    protection_details['LENGTH (IN Mtr) OF PCC'] = 0
    protection_details['LENGTH (IN Mtr) OF DWC'] = protection_['LENGTH (IN Mtr) OF CULVERT']
    protection_details['LENGTH (IN Mtr) OF GI'] = protection_['LENGTH (IN Mtr) OF BRIDGE']
    if 'HARD ROCK (Length)' in protection_.columns:
        protection_details['LENGTH (IN Mtr) OF DWC+PCC'] = protection_['HARD ROCK (Length)']
        protection_details['HARD ROCK (Length)'] = protection_['HARD ROCK (Length)']
    else:
        protection_details['LENGTH (IN Mtr) OF DWC+PCC'] = ''
        protection_details['HARD ROCK (Length)'] = ''
    protection_details['Soil Details'] = ''
    protection_details['LENGTH (IN Mtr) OF ANCORING'] = 0

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a',
                        if_sheet_exists='replace') as writer:
        protection_details.to_excel(writer, sheet_name='Protection Details', index=False)

    print('Protection Summery Created')
    #
    ##################################################### RoW PreSurvey ######################################################
    #
    cols_row_ps = ['SrNo', 'Ring No', 'GP Name', 'Span Name', 'NHSHNo', 'RoadWidth', 'RowBoundaryLmt', 'KMStoneFromA',
                   'KMStoneToB', 'SuveryDist', 'st_Lat_Long_Auth', 'end_Lat_Long_Auth', 'LandmarkRHS',
                   'VlgTwnPoint', 'OFClaying', 'RdCrossing Req', 'ReasonRdCrossing', 'UtilityLHS', 'UtilityChecked',
                   'RowAuthorityName', 'AuthorityAddress', 'FeasibilityOfROWApproval', 'TypeOfOverlapArea',
                   'NearestLandmark', 'LengthOfOverlapArea', 'ExpansionInProg', 'ExpansionPlanned', 'TypeOfCrossing',
                   'st_Lat_Long_xing', 'end_Lat_Long_xing', 'LatLandmark', 'LongLandmark',
                   'LengthOfCrossing', 'Remarks']

    span = gdf_working.sort_values('span_name').span_name.unique()
    row_pre_survey = pd.DataFrame(columns=cols_row_ps)
    for s in span:
        temp_df = gdf_working[gdf_working.span_name == s].sort_values('Sequqnce')
        output = []
        group = None
        crossing_coords_start = []
        crossing_coords_end = []
        output_df = None
        for _, row in temp_df.iterrows():
            p_n, s_n, dist, auth, geom, ofc_side, ring = row["crossing_t"], row["span_name"], row["distance"], row[
                "road_autho"], \
                row["geometry"], row['ofc_laying'], row['ring_no']
            coords = extract_coords(geom)
            if not any(sub in p_n.lower() for sub in ['culvert', 'bridge']):
                if group is None:
                    group = {
                        'SrNo': '',
                        "Ring No":ring,
                        'GP Name':'',
                        'Span Name': s_n,
                        'NHSHNo': '',
                        'RoadWidth': '',
                        'RowBoundaryLmt': '',
                        'KMStoneFromA': "",
                        'KMStoneToB': "",
                        'SuveryDist': dist,
                        'st_Lat_Long_Auth': f"{coords[0].split(' ')[1]},{coords[0].split(' ')[0]}",
                        'end_Lat_Long_Auth': f"{coords[-1].split(' ')[1]},{coords[-1].split(' ')[0]}",
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
                        'end_Lat_Long_xing': '',
                        'LatLandmark': '',
                        'LongLandmark': '',
                        'LengthOfCrossing': '',
                        'Remarks': ''
                    }
                elif group["RowAuthorityName"] == auth:
                     group["SuveryDist"] += dist
                     group["end_Lat_Long_Auth"] = f"{coords[-1].split(' ')[1]},{coords[-1].split(' ')[0]}"
                else:
                    output.append(group)
                    group = {
                        'SrNo': '',
                        "Ring No": ring,
                        'GP Name': '',
                        'Span Name': s_n,
                        'NHSHNo': '',  # TODO Find Road Nmme
                        'RoadWidth': '',
                        'RowBoundaryLmt': '',
                        'KMStoneFromA': "",
                        'KMStoneToB': "",
                        'SuveryDist': dist,
                        'st_Lat_Long_Auth': f"{coords[0].split(' ')[1]},{coords[0].split(' ')[0]}",
                        'end_Lat_Long_Auth': f"{coords[-1].split(' ')[1]},{coords[-1].split(' ')[0]}",
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
                        'end_Lat_Long_xing': '',
                        'LatLandmark': '',  # TODO Latitude of LandMark
                        'LongLandmark': '',  # TODO Longitude of the LandMark
                        'LengthOfCrossing': '',
                        'Remarks': ''
                    }
                    crossing_coords_start = []
                    crossing_coords_end = []
            else:
                if group:
                    group["Ring No"] = ring
                    group["TypeOfCrossing"] = p_n.lower()
                    crossing_coords_start.append(f"{coords[0].split(' ')[1]},{coords[0].split(' ')[0]}")
                    crossing_coords_end.append(f"{coords[-1].split(' ')[1]},{coords[-1].split(' ')[0]}")
                    group["SuveryDist"] += dist
                    group["end_Lat_Long_Auth"] = f"{coords[-1].split(' ')[1]},{coords[-1].split(' ')[0]}"
                    group["st_Lat_Long_xing"] = ", ".join(crossing_coords_start)
                    group["end_Lat_Long_xing"] = ", ".join(crossing_coords_end)
        # Append final group
        if group:
            output.append(group)
        # Create output DataFrame
        output_df = pd.DataFrame(output)
        output_df.reset_index(drop=True, inplace=True)
        row_pre_survey = pd.concat([row_pre_survey, output_df])

    row_pre_survey_temp = row_pre_survey
    if api_key is not None:
        row_pre_survey['RoadWidth'] = row_pre_survey_temp.apply(calculate_offset_width, axis=1, args=('width',))
        row_pre_survey['NHSHNo'] = row_pre_survey_temp.apply(finding_road_name, axis=1)
        row_pre_survey['LandmarkRHS'] = row_pre_survey_temp.apply(finding_landmark, axis=1, args=('name',))
        row_pre_survey['VlgTwnPoint'] = row_pre_survey_temp.apply(finding_village, axis=1)
        row_pre_survey['NearestLandmark'] = row_pre_survey_temp.apply(finding_landmark, axis=1, args=('name', ))
        row_pre_survey['LatLandmark'] = row_pre_survey_temp.apply(finding_landmark, axis=1, args=('lat',))
        row_pre_survey['LongLandmark'] = row_pre_survey_temp.apply(finding_landmark, axis=1, args=('lng',))
    else:
        print("GOOGLE API KEY is Required for generating all the details")
    with pd.ExcelWriter(excel_file, engine='openpyxl',
                        mode='a') as writer:
        row_pre_survey.to_excel(writer, sheet_name='PreSurvey', index=False)
    print('RoW Pre Survey Created')

#INDEX
index(excel_file)

#ASSET DETAILS
asset_details(village_data, boq_sd_df, blockName, districtName, excel_file)

# Annexure -X
annexure_x(excel_file)

# Table B
table_b(excel_file)

#Gas Crossing
gas_xing(excel_file)

# Railway Crossing
railway_xing(excel_file)

# GPON
gpon(excel_file)

# BoQ & BOM
bom_boq(excel_file)

#Formatting the Excel Sheet
formatting_excel_file(excel_file)