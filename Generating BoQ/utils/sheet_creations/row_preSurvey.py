from .. api_calls import *

cols_row_ps = ['SrNo', 'Ring No', 'GP Name', 'Span Name', 'NHSHNo', 'RoadWidth', 'RowBoundaryLmt', 'KMStoneFromA',
                   'KMStoneToB', 'SuveryDist', 'st_Lat_Long_Auth', 'end_Lat_Long_Auth', 'LandmarkRHS',
                   'VlgTwnPoint', 'OFClaying', 'RdCrossing Req', 'ReasonRdCrossing', 'UtilityLHS', 'UtilityChecked',
                   'RowAuthorityName', 'AuthorityAddress', 'FeasibilityOfROWApproval', 'TypeOfOverlapArea',
                   'NearestLandmark', 'LengthOfOverlapArea', 'ExpansionInProg', 'ExpansionPlanned', 'TypeOfCrossing',
                   'st_Lat_Long_xing', 'end_Lat_Long_xing', 'LatLandmark', 'LongLandmark',
                   'LengthOfCrossing', 'Remarks']
def row_presurvey(gdf_working,excel_file, blockName,districtName):
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