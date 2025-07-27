from imports import *
from constants import *
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


def categorize_value(row):
    value = str(row['crossing_t'])  # Ensure value is string
    value2 = str(row['end_point_'])
    if any(sub in value.lower() for sub in ['road']):  # Check for 'Re' or 'RE'
        return 'Road'
    elif difflib.SequenceMatcher(None, value.lower(), "culvert").ratio() > 0.5:
        return 'Crossing'
    elif difflib.SequenceMatcher(None, value.lower(), "bridge").ratio() > 0.5:
        return 'Crossing'
    elif any(sub in value2.lower() for sub in ['gp', 'gram panchyat', 'grampanchayat']):  # Check for 'GP', 'Gp', etc.
        return 'Gram Panchyat'
    else:
        return 'Landmark'


def calculate_offset_width(row, param):
    try:
        value = str(row['road_autho']).upper()
        keywords = ['PMGY', 'SH', 'NH', 'NAGAR PARISHAD', 'GRAMPANCHAYAT', 'GP', 'PWD', 'ODR', 'MDR']
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
    except:
        return None


def finding_lat_lon(row, lat_lon):
    value_end_point = str(row['end_point_']).lower()
    value_crossing = str(row['crossing_t']).lower()
    att = lat_lon
    if att == 'lat':
        if any(sub in value_crossing for sub in ['culvert', 'bridge', 'road']):
            return row['Start_Lat']
        else:
            return row['End_Lat']
    elif att == 'lon':
        if any(sub in value_crossing for sub in ['culvert', 'bridge', 'road']):
            return row['Start_Long']
        else:
            return row['End_Long']
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

def extract_coords(geom):
    try:
        geom_str = str(geom)
        coords_part = geom_str.replace('LINESTRING (', '').replace(')', '')
        # Split by comma to separate coordinate pairs
        coords = [coord.strip() for coord in coords_part.split(',')]
        return coords
    except Exception as e:
        print(f"Error processing geom: {geom} -> {e}")
        return []