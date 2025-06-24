import pandas as pd
cols = ['SrNo', 'FROM  AND TO GP','NHSHNo','RoadWidth','RowBoundaryLmt','KMStoneFromA','KMStoneToB','SuveryDist','LatAuth','LongAuth','LandmarkRHS',
'VlgTwnPoint','OFClaying','RdCrossing Req','ReasonRdCrossing','UtilityLHS','UtilityRHS',   'UtilityChecked',   'RowAuthorityName', 'AuthorityAddress', 'FeasibilityOfROWApproval', 'TypeOfOverlapArea',
'NearestLandmark', 'LengthOfOverlapArea','ExpansionInProg','ExpansionPlanned','TypeOfCrossing','LatCrossing','LongCrossing','LatLandmark','LongLandmark',
'LengthOfCrossing','SoilType','RouteRdSidePts','AlternateReq','AlternateProp','AlternatePathLgh','Remarks']

row_in_dep = pd.DataFrame(columns=cols)

_ds = pd.read_excel('excel_files/Tarana Block/Tarana-BoQ.xlsx', sheet_name='Details Sheet')


def process_kms_photo(value):
    if value is not None:
        return f"=IMAGE({value})"
    else:
        return ''


def find_lat(value):
    try:
        cords = value.strip('POINT()').split(' ')
    except:
        return 'NA'
    return cords[1]


def find_long(value):
    try:
        cords = value.strip('POINT()').split(' ')
    except:
        return 'NA'
    return cords[0]


def road_xing_req(value):
    if 'road' in str(value).lower() or 'rod' in str(value).lower():
        return 'Yes'
    else:
        return 'NA'


def road_xing_reas(value):
    if 'road' in str(value).lower():
        return "Conncting Road Coming Along OFC Path"
    else:
        return 'NA'


def finding_utility_lhs(row):
    if row['OFC POSITION'] == 'LHS':
        if 'rjil' in str(row['POINT NAME']).lower():
            return "Reliance Jio"
        elif 'airtel' in str(row['POINT NAME']).lower():
            return "Airtel"
        elif 'bsnl' in str(row['POINT NAME']).lower():
            return 'BSNL'
        elif 'gas' in str(row['POINT NAME']).lower():
            return 'Gas PipeLine ' + str(row['POINT NAME'])
        elif 'hpcl' in str(row['POINT NAME']).lower():
            return 'HPCL Pipeline'
        elif 'iocl' in str(row['POINT NAME']).lower():
            return 'IOCL Pipeline'
        elif 'railway' in str(row['POINT NAME']).lower():
            return 'railway'
        elif 'petrol' in str(row['POINT NAME']).lower():
            return 'Petroleum Pipeline ' + str(row['POINT NAME'])
        elif 'gail' in str(row['POINT NAME']).lower():
            return 'Gail Xing'
    else:
        return 'NA'


def finding_utility_rhs(row):
    if row['OFC POSITION'] == 'RHS':
        if 'rjil' in str(row['POINT NAME']).lower():
            return "Reliance Jio"
        elif 'airtel' in str(row['POINT NAME']).lower():
            return "Airtel"
        elif 'bsnl' in str(row['POINT NAME']).lower():
            return 'BSNL'
        elif 'gas' in str(row['POINT NAME']).lower():
            return 'Gas PipeLine ' + str(row['POINT NAME'])
        elif 'hpcl' in str(row['POINT NAME']).lower():
            return 'HPCL Pipeline'
        elif 'iocl' in str(row['POINT NAME']).lower():
            return 'IOCL Pipeline'
        elif 'railway' in str(row['POINT NAME']).lower():
            return 'railway'
        elif 'petrol' in str(row['POINT NAME']).lower():
            return 'Petroleum Pipeline ' + str(row['POINT NAME'])
        elif 'gail' in str(row['POINT NAME']).lower():
            return 'Gail Xing'
    else:
        return 'NA'


def utility_checked(row):
    value = row['POINT NAME']
    if any(sub in value.lower() for sub in ['rjil', 'airtel', 'bsnl', 'gas', 'hpcl', 'iocl', 'adani', 'railway', 'petrol', 'gail']):
        return "Route Marker"
    else:
        return "NA"


def road_authority(row):
    if 'pmgy' in str(row['AUTHORITY NAME']).lower():
        return f"PMGSY-{str(row['ROAD NAME']).upper()} (MPRRDA)"
    elif 'pwd' in str(row['AUTHORITY NAME']).lower() or 'sh' in str(row['AUTHORITY NAME']).lower() or 'odr' in str(row['AUTHORITY NAME']).lower():
        return f"PWD-(Ujjain)"
    elif 'NHAI' in str(row['AUTHORITY NAME']).lower():
        return f"NHAI-Ujjain"
    elif 'nagar' in str(row['AUTHORITY NAME']).lower():
        return f"Nagar Parishad-Tarana"
    else:
        return row['AUTHORITY NAME']


def road_auth_add(row):
    if 'pmgy' in str(row['AUTHORITY NAME']).lower():
        return f"General Manager, (PMGSY) MPRRDA, Ujjain"
    elif 'pwd' in str(row['AUTHORITY NAME']).lower() or 'sh' in str(row['AUTHORITY NAME']).lower() or 'odr' in str(row['AUTHORITY NAME']).lower():
        return f"Executive Engineer,  PWD-(Ujjain)"
    elif 'NHAI' in str(row['AUTHORITY NAME']).lower():
        return f"Project Director, NHAI-Ujjain"
    elif 'nagar' in str(row['AUTHORITY NAME']).lower():
        return f"CMO, Nagar Parishad-Tarana"
    else:
        return f"{row['AUTHORITY NAME']}, Ujjain"


def nearest_landmark(value):
    if any(sub in value.lower() for sub in ['school', 'college', 'temple', 'gp', 'gram', 'kms']):
        return value.upper()
    else:
        return "NA"


def calculate_structure(row):
    structure = ''
    if 'cul' in str(row['POINT NAME']).lower():
        structure = 'CULVERT'
    elif 'bri' in str(row['POINT NAME']).lower():
        structure = 'BRIDGE'
    elif 'canal' in str(row['POINT NAME']).lower():
        structure = 'CANAL'
    else:
        structure = ''
    return structure


def structure_xing_lat(row):
    if any(sub in str(row['POINT NAME']).lower() for sub in ['cul', 'bri', 'canal']):
        try:
            return str(row['CROSSING_START']).strip('POINT()').split(' ')[1]
        except:
            return 'NA'
    else:
        return "NA"


def structure_xing_long(row):
    if any(sub in str(row['POINT NAME']).lower() for sub in ['cul', 'bri', 'canal']):
        try:
            return str(row['CROSSING_END']).strip('POINT()').split(' ')[0]
        except:
            return 'NA'
    else:
        return "NA"


def landmark_lat(value):
    try:
        return value.strip('POINT()').split(' ')[1]
    except:
        return "NA"


def landmark_long(value):
    try:
        return value.strip('POINT()').split(' ')[0]
    except:
        return "NA"


def landmark(value):
    if any(sub not in str(value).lower() for sub in
           ['cul', 'bri', 'canal', 'rjil', 'airtel', 'bsnl', 'gas', 'hpcl', 'iocl', 'railway', 'petroleum', 'gail', 'rod', 'road', 'kacha']):
        return str(value).upper()
    else:
        return ""


row_in_dep['SrNo'] = _ds['SPAN_CONTINUITY']
row_in_dep['FROM  AND TO GP'] = _ds['ROUTE NAME']
# row_in_dep['NHSHNo'] = _ds['ROUTE KMS PHOTO']
row_in_dep['NHSHNo'] = _ds['ROAD CHAINAGE']
row_in_dep['RoadWidth'] = _ds['ROAD WIDTH(m)']
row_in_dep['RowBoundaryLmt'] = 'NA'
row_in_dep['KMStoneFromA'] = 'NA'
row_in_dep['KMStoneToB'] = _ds['ROAD CHAINAGE']
row_in_dep['SuveryDist'] = _ds['DISTENCE(M)']
row_in_dep['LatAuth'] = _ds['START_COORDINATE'].apply(find_lat)
row_in_dep['LongAuth'] = _ds['START_COORDINATE'].apply(find_long)
row_in_dep['LandmarkRHS'] = _ds['POINT NAME'].apply(landmark)
row_in_dep['VlgTwnPoint'] = _ds['ROAD NAME']
row_in_dep['OFClaying'] = _ds['OFC POSITION']
row_in_dep['RdCrossing Req'] = _ds['ROAD NAME'].apply(road_xing_req)
row_in_dep['ReasonRdCrossing'] = _ds['ROAD NAME'].apply(road_xing_reas)
row_in_dep['UtilityLHS'] = _ds.apply(finding_utility_lhs, axis=1)
row_in_dep['UtilityRHS'] = _ds.apply(finding_utility_rhs, axis=1)
row_in_dep['UtilityChecked'] = _ds.apply(utility_checked, axis=1)
row_in_dep['RowAuthorityName'] = _ds.apply(road_authority, axis=1)
row_in_dep['AuthorityAddress'] = _ds.apply(road_auth_add, axis=1)
row_in_dep['FeasibilityOfROWApproval'] = 'Yes'
row_in_dep['TypeOfOverlapArea'] = 'NA'
row_in_dep['NearestLandmark'] = _ds['POINT NAME'].apply(nearest_landmark)
row_in_dep['LengthOfOverlapArea'] = 'NA'
row_in_dep['ExpansionInProg'] = 'NA'
row_in_dep['ExpansionPlanned'] = 'NA'
row_in_dep['TypeOfCrossing'] = _ds.apply(calculate_structure, axis=1)
row_in_dep['LatCrossing'] = _ds.apply(structure_xing_lat, axis=1)
row_in_dep['LongCrossing'] = _ds.apply(structure_xing_long, axis=1)
row_in_dep['LatLandmark'] = _ds['END_COORDINATE'].apply(landmark_lat)
row_in_dep['LongLandmark'] = _ds['END_COORDINATE'].apply(landmark_long)
row_in_dep['LengthOfCrossing'] = _ds['LENGTH (IN Mtr.)']
row_in_dep['SoilType'] = _ds['SOIL TYPE']
row_in_dep['RouteRdSidePts'] = 'NA'
row_in_dep['AlternateReq'] = 'NA'
row_in_dep['AlternateProp'] = 'NA'
row_in_dep['AlternatePathLgh'] = 'NA'
row_in_dep['Remarks'] = ''

with pd.ExcelWriter('excel_files/Tarana Block/Tarana_RoW.xlsx', engine='openpyxl', mode='w') as writer:
    row_in_dep.to_excel(writer, sheet_name='PreSurvey', index=False)