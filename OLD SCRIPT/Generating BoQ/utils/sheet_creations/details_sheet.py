from .. methods import *

cols_ds = ['SPAN_CONTINUITY', 'POINT NAME', 'TYPE', 'POSITION', 'OFFSET', 'CHAINAGE', 'DISTENCE(M)', 'LATITUDE',
               "LONGITUDE", 'ROUTE NAME', 'ROUTE TYPE',
               'OFC TYPE', 'LAYING TYPE', 'ROUTE ID', 'ROUTE MARKER', 'MANHOLE', 'ROAD NAME', 'ROAD WIDTH(m)',
               'ROAD SURFACE', 'OFC POSITION', 'APRX DISTANCE FROM RCL(m)',
               'AUTHORITY NAME', 'ROAD CHAINAGE', 'ROAD STRUTURE TYPE', 'LENGTH (IN Mtr.)', 'PROTECTION TYPE',
               'PROTECTION FOR', 'PROTECTION LENGTH (IN Mtr.)', 'UTILITY NAME',
               'SIDE OF THE ROAD', 'SOIL TYPE', 'REMARKS']
def details_sheet(gdf_working, excel_file):
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