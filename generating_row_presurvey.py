import pandas as pd
cols = ['SrNo', 'FROM  AND TO GP','NHSHNo','RoadWidth','RowBoundaryLmt','KMStoneFromA','KMStoneToB','SuveryDist','LatAuth','LongAuth','LandmarkRHS',
'VlgTwnPoint','OFClaying','RdCrossing Req','ReasonRdCrossing','UtilityLHS','UtilityRHS',   'UtilityChecked',   'RowAuthorityName', 'AuthorityAddress', 'FeasibilityOfROWApproval', 'TypeOfOverlapArea',
'NearestLandmark', 'LengthOfOverlapArea','ExpansionInProg','ExpansionPlanned','TypeOfCrossing','LatCrossing','LongCrossing','LatLandmark','LongLandmark',
'LengthOfCrossing','SoilType','RouteRdSidePts','AlternateReq','AlternateProp','AlternatePathLgh','Remarks']

row_in_dep = pd.DataFrame(columns=cols)

porsa_ds = pd.read_excel('excel_files/mapped_output_Porsa.xlsx', sheet_name='Details Sheet')


def process_kms_photo(value):
    if value is not None:
        return f"=IMAGE({value})"
    else:
        return ''


def find_lat(value):
    cords = value.strip('POINT()').split(' ')
    return cords[1]


def find_long(value):
    cords = value.strip('POINT()').split(' ')
    return cords[0]


def road_xing_req(value):
    if 'road' in str(value).lower():
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
            return 'Gas PipeLine'
        elif 'hpcl' in str(row['POINT NAME']).lower():
            return 'HPCL Pipeline'
        elif 'iocl' in str(row['POINT NAME']).lower():
            return 'IOCL Pipeline'
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
            return 'Gas PipeLine'
        elif 'hpcl' in str(row['POINT NAME']).lower():
            return 'HPCL Pipeline'
        elif 'iocl' in str(row['POINT NAME']).lower():
            return 'IOCL Pipeline'
    else:
        return 'NA'


def utility_checked(row):
    value = row['POINT NAME']
    if any(sub in value.lower() for sub in ['rjil', 'airtel', 'bsnl', 'gas', 'hpcl', 'iocl']):
        return "Route Marker"
    else:
        return "NA"


def road_authority(row):
    if 'pmgy' in str(row['AUTHORITY NAME']).lower():
        return f"PMGSY-{str(row['ROAD NAME']).upper()}(MPRRDA)"
    elif 'pwd' in str(row['AUTHORITY NAME']).lower():
        return f"PWD-(Morena)"
    elif 'NHAI' in str(row['AUTHORITY NAME']).lower():
        return f"NHAI-Morena"
    else:
        return row['AUTHORITY NAME']


def road_auth_add(row):
    if 'pmgy' in str(row['AUTHORITY NAME']).lower():
        return f"General Manager, (PMGSY) MPRRDA, Morena"
    elif 'pwd' in str(row['AUTHORITY NAME']).lower():
        return f"Executive Engineer,  PWD-(Morena)"
    elif 'NHAI' in str(row['AUTHORITY NAME']).lower():
        return f"Project Director, NHAI-Morena"
    else:
        return f"{row['AUTHORITY NAME']}, Morena"


def nearest_landmark(value):
    if any(sub in value.lower() for sub in ['school', 'college', 'temple']):
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
        return str(row['CROSSING_START']).strip('POINT()').split(' ')[1]
    else:
        return ""


def structure_xing_long(row):
    if any(sub in str(row['POINT NAME']).lower() for sub in ['cul', 'bri', 'canal']):
        return str(row['CROSSING_END']).strip('POINT()').split(' ')[0]
    else:
        return ""


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
           ['cul', 'bri', 'canal', 'rjil', 'airtel', 'bsnl', 'gas', 'hpcl', 'iocl']):
        return str(value).upper()
    else:
        return ""


row_in_dep['SrNo'] = porsa_ds['SPAN_CONTINUITY']
row_in_dep['FROM  AND TO GP'] = porsa_ds['ROUTE NAME']
row_in_dep['NHSHNo'] = porsa_ds['ROUTE KMS PHOTO']
row_in_dep['RoadWidth'] = porsa_ds['ROAD WIDTH(m)']
row_in_dep['RowBoundaryLmt'] = 'NA'
row_in_dep['KMStoneFromA'] = porsa_ds['ROAD CHAINAGE']
row_in_dep['KMStoneToB'] = 'NA'
row_in_dep['SuveryDist'] = porsa_ds['DISTENCE(M)']
row_in_dep['LatAuth'] = porsa_ds['START_COORDINATE'].apply(find_lat)
row_in_dep['LongAuth'] = porsa_ds['START_COORDINATE'].apply(find_long)
row_in_dep['LandmarkRHS'] = porsa_ds['POINT NAME'].apply(landmark)
row_in_dep['VlgTwnPoint'] = porsa_ds['ROAD NAME']
row_in_dep['OFClaying'] = porsa_ds['OFC POSITION']
row_in_dep['RdCrossing Req'] = porsa_ds['ROAD NAME'].apply(road_xing_req)
row_in_dep['ReasonRdCrossing'] = porsa_ds['ROAD NAME'].apply(road_xing_reas)
row_in_dep['UtilityLHS'] = porsa_ds.apply(finding_utility_lhs, axis=1)
row_in_dep['UtilityRHS'] = porsa_ds.apply(finding_utility_rhs, axis=1)
row_in_dep['UtilityChecked'] = porsa_ds.apply(utility_checked, axis=1)
row_in_dep['RowAuthorityName'] = porsa_ds.apply(road_authority, axis=1)
row_in_dep['AuthorityAddress'] = porsa_ds.apply(road_auth_add, axis=1)
row_in_dep['FeasibilityOfROWApproval'] = 'Yes'
row_in_dep['TypeOfOverlapArea'] = 'NA'
row_in_dep['NearestLandmark'] = porsa_ds['POINT NAME'].apply(nearest_landmark)
row_in_dep['LengthOfOverlapArea'] = 'NA'
row_in_dep['ExpansionInProg'] = 'NA'
row_in_dep['ExpansionPlanned'] = 'NA'
row_in_dep['TypeOfCrossing'] = porsa_ds.apply(calculate_structure, axis=1)
row_in_dep['LatCrossing'] = porsa_ds.apply(structure_xing_lat, axis=1)
row_in_dep['LongCrossing'] = porsa_ds.apply(structure_xing_long, axis=1)
row_in_dep['LatLandmark'] = porsa_ds['END_COORDINATE'].apply(landmark_lat)
row_in_dep['LongLandmark'] = porsa_ds['END_COORDINATE'].apply(landmark_long)
row_in_dep['LengthOfCrossing'] = porsa_ds['LENGTH (IN Mtr.)']
row_in_dep['SoilType'] = porsa_ds['SOIL TYPE']
row_in_dep['RouteRdSidePts'] = 'NA'
row_in_dep['AlternateReq'] = 'NA'
row_in_dep['AlternateProp'] = 'NA'
row_in_dep['AlternatePathLgh'] = 'NA'
row_in_dep['Remarks'] = ''

with pd.ExcelWriter('excel_files/Porsa_RoW.xlsx', engine='openpyxl', mode='w') as writer:
    row_in_dep.to_excel(writer, sheet_name='PreSurvey', index=False)