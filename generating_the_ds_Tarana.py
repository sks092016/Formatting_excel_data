
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

def categorize_value(value):
    value = str(value)  # Ensure value is string
    if any(sub in value.lower() for sub in ['re', 're ']):  # Check for 'Re' or 'RE'
        return 'CROSSING'
    elif any(sub in value.lower() for sub in ['cul', 'culvert', 'bridge', 'canal']):  # Check for 'cul', 'Culvert', 'Bridge'
        return 'ROAD STRUCTURE'
    elif any(
            sub in value.lower() for sub in ['gp', 'gram panchyat', 'grampanchayat']):  # Check for 'GP', 'Gp', etc.
        return 'ASSET'
    else:
        return 'LANDMARK'


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


def calculate_road_width(row):
    re1 = row['road_edge_'].strip('POINT()').split(' ')
    re2 = row['road_edg_3'].strip('POINT()').split(' ')
    road_width = haversine_distance(re1[1], re1[0], re2[1], re2[0])
    return road_width


def calculate_road_chainage(row):
    chainage = ''
    if 'kms' in str(str(row['end_point_name'])).lower():
        chainage = str(row['end_point_name'])
    else:
        chainage = 'NA'
    return chainage


def calculate_structure(row):
    structure = ''
    if 'cul' in str(row['end_point_name']).lower():
        structure = 'CULVERT'
    elif 'bri' in str(row['end_point_name']).lower():
        structure = 'BRIDGE'
    elif 'canal' in str(row['end_point_name']).lower():
        structure = 'CANAL'
    else:
        structure = ''
    return structure


def calculate_xing_length(row):
    xing_length = 0
    if 'cul' in str(row['end_point_name']).lower() or 'bri' in str(row['end_point_name']).lower() or 'canal' in str(row['end_point_name']).lower():
        xing1 = row['crossing_Start'].strip('POINT()').split(' ')
        xing2 = row['crossing_end'].strip('POINT()').split(' ')
        xing_length = haversine_distance(xing1[1], xing1[0], xing2[1], xing2[0])
    return xing_length


def calculate_protec(row):
    protection = ''
    if 'cul' in str(row['end_point_name']).lower():
        protection = 'DWC+PCC'
    elif 'bri' in str(row['end_point_name']).lower() or 'canal' in str(row['end_point_name']).lower():
        protection = 'GI+PCC'
    else:
        protection = ''
    return protection


def calculate_protec_length(row):
    xing_length = 0
    if 'cul' in str(row['end_point_name']).lower() or 'bri' in str(row['end_point_name']).lower() or 'canal' in str(row['end_point_name']).lower():
        xing1 = row['crossing_Start'].strip('POINT()').split(' ')
        xing2 = row['crossing_end'].strip('POINT()').split(' ')
        xing_length = haversine_distance(xing1[1], xing1[0], xing2[1], xing2[0])
        return xing_length + 2
    else:
        return 0

def change_point_name(value):
    if str(value).upper() == "RE":
        return 'ROAD CROSS EDGE'
    else:
        return str(value).upper()

def calculate_cordinate(row):
    return f"POINT({str(row['lat'])} {str(row['lat'])})"

def finding_utility(row):
    if 'rjil' in str(row['end_point_name']).lower():
        return "Reliance Jio"
    elif 'airtel' in str(row['end_point_name']).lower():
        return "Airtel"
    elif 'bsnl' in str(row['end_point_name']).lower():
        return 'BSNL'
    elif 'gas' in str(row['end_point_name']).lower():
        return 'Gas PipeLine'
    elif 'hpcl' in str(row['end_point_name']).lower():
        return 'HPCL Pipeline'
    elif 'iocl' in str(row['end_point_name']).lower():
        return 'IOCL Pipeline'
    else:
        return ''

def calc_len(row):
    value = str(row['end_point_name'])
    if any(sub in value.lower() for sub in ['cul', 'culvert', 'bridge', 'canal']):
        return row['crossing_l']
    else:
        return ''

def calc_len_proc(row):
    value = str(row['end_point_name'])
    if any(sub in value.lower() for sub in ['cul', 'culvert', 'bridge', 'canal']):
        return row['crossing_l'] + 2
    else:
        return 0

cols= ['POINT NAME','TYPE','POSITION','OFFSET','SPAN_CONTINUITY','CHAINAGE','DISTENCE(M)',"START_COORDINATE", 'CROSSING_START','CROSSING_END','END_COORDINATE','ROUTE NAME','ROUTE TYPE',
       'OFC TYPE','LAYING TYPE','ROUTE ID','ROUTE MARKER','MANHOLE','ROAD NAME','ROAD WIDTH(m)','ROAD SURFACE','OFC POSITION','APRX DISTANCE FROM RCL(m)',
       'AUTHORITY NAME','ROAD CHAINAGE','ROAD STRUTURE TYPE','LENGTH (IN Mtr.)','PROTECTION TYPE','PROTECTION FOR','PROTECTION LENGTH (IN Mtr.)','UTILITY NAME',
       'SIDE OF THE ROAD','SOIL TYPE','TERRAIN','REMARKS']
boq_ = pd.DataFrame(columns=cols)

survey = pd.read_excel('excel_files/Tarana Block/Tarana_block_survey.xlsx', sheet_name='Sheet1')
survey.rename(columns = {"end_point_":"end_point_name", "Sequqnce":"SEQ"}, inplace=True)
span = survey.sort_values('span_name').span_name.unique()
for s in span:
    print(s)
    temp_df = survey[survey.span_name == s].sort_values('SEQ')
    temp_df.insert(11, "chainage", "NA")
    new_row = temp_df.iloc[[0]].copy()
    new_row['chainage'] = 0
    new_row['distance'] = 0
    new_row['SEQ'] = 0
    new_row['end_point_name'] = "GP " + s.split('TO')[0]
    pd.DataFrame(new_row)
    temp_df = pd.concat([temp_df, new_row])
    temp_df = temp_df.sort_values('SEQ')

    cols = ['POINT NAME', 'TYPE', 'POSITION', 'OFFSET', 'SPAN_CONTINUITY', 'CHAINAGE', 'DISTENCE(M)', "START_COORDINATE", 'CROSSING_START',
            'CROSSING_END', "END_COORDINATE",'ROUTE NAME', 'ROUTE TYPE',
            'OFC TYPE', 'LAYING TYPE', 'ROUTE ID', 'ROUTE MARKER', 'MANHOLE', 'ROAD NAME', 'ROAD WIDTH(m)',
            'ROAD SURFACE', 'OFC POSITION', 'APRX DISTANCE FROM RCL(m)',
            'AUTHORITY NAME', 'ROAD CHAINAGE', 'ROAD STRUTURE TYPE', 'LENGTH (IN Mtr.)', 'PROTECTION TYPE',
            'PROTECTION FOR', 'PROTECTION LENGTH (IN Mtr.)', 'UTILITY NAME',
            'SIDE OF THE ROAD', 'SOIL TYPE', 'TERRAIN', 'REMARKS']
    boq_ds_df = pd.DataFrame(columns=cols)

    boq_ds_df['POINT NAME'] = temp_df['end_point_name'].apply(change_point_name)
    boq_ds_df['TYPE'] = temp_df['end_point_name'].apply(categorize_value)
    boq_ds_df['POSITION'] = temp_df['ofc_laying']
    boq_ds_df['OFFSET'] = 'NA'
    boq_ds_df['SPAN_CONTINUITY'] = temp_df['SEQ']
    boq_ds_df['CHAINAGE'] = pd.DataFrame([0.0] + [sum(list(temp_df['distance'])[:i + 1]) for i in range(1, len(list(temp_df['distance'])))]).values
    boq_ds_df['DISTENCE(M)'] = temp_df['distance']
    boq_ds_df['START_COORDINATE'] = "NA"
    boq_ds_df['CROSSING_START'] = "NA"
    boq_ds_df['CROSSING_END'] = "NA"
    boq_ds_df['END_COORDINATE'] = temp_df.apply(calculate_cordinate, axis=1)
    boq_ds_df['ROUTE NAME'] = temp_df['span_name']
    boq_ds_df['ROUTE TYPE'] = temp_df['scope']
    boq_ds_df['OFC TYPE'] = '48F'
    boq_ds_df['LAYING TYPE'] = 'UG'
    boq_ds_df['ROUTE ID'] = temp_df['span_id']
    boq_ds_df['ROUTE MARKER'] = 'NOT VISIBLE'
    boq_ds_df['MANHOLE'] = 'NOT VISIBLE'
    boq_ds_df['ROAD NAME'] = temp_df['road_name']
    boq_ds_df['ROAD WIDTH(m)'] = "NA"
    boq_ds_df['ROAD SURFACE'] = temp_df['road_surfa']
    boq_ds_df['OFC POSITION'] = temp_df['ofc_laying']
    boq_ds_df['APRX DISTANCE FROM RCL(m)'] = 'NA'
    boq_ds_df['AUTHORITY NAME'] = temp_df['road_autho']
    boq_ds_df['ROAD CHAINAGE'] = temp_df.apply(calculate_road_chainage, axis=1)
    boq_ds_df['ROAD STRUTURE TYPE'] = temp_df.apply(calculate_structure, axis=1)
    boq_ds_df['LENGTH (IN Mtr.)'] = temp_df.apply(calc_len, axis=1)
    boq_ds_df['PROTECTION TYPE'] = temp_df.apply(calculate_protec, axis=1)
    boq_ds_df['PROTECTION FOR'] = temp_df.apply(calculate_structure, axis=1)
    boq_ds_df['PROTECTION LENGTH (IN Mtr.)'] = temp_df.apply(calc_len_proc, axis=1)
    boq_ds_df['UTILITY NAME'] = temp_df.apply(finding_utility, axis=1)
    boq_ds_df['SIDE OF THE ROAD'] = "NA"
    boq_ds_df['SOIL TYPE'] = temp_df['strata_typ']
    boq_ds_df['TERRAIN'] = temp_df['terrain_ty']
    boq_ds_df['REMARKS'] = "NA"
    boq_ = pd.concat([boq_, boq_ds_df])

with pd.ExcelWriter('excel_files/Tarana Block/Tarana-BoQ.xlsx', engine='openpyxl', mode='a',if_sheet_exists='replace') as writer:
    boq_.to_excel(writer, sheet_name='Details Sheet', index=False)
