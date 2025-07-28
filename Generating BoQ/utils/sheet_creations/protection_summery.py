from .. api_calls import *

cols_pro = ['ROUTE NAME', 'ROUTE TYPE', 'TOTAL ROUTE LENGTH', 'NO OF CULVERT', 'LENGTH (IN Mtr) OF CULVERT',
            'NO OF BRIDGE',
            'LENGTH (IN Mtr) OF BRIDE',
            'LENGTH (IN Mtr) OF PCC', 'LENGTH (IN Mtr) OF DWC', 'LENGTH (IN Mtr) OF GI',
            'LENGTH (IN Mtr) OF DWC+PCC',
            "Soil Detail", "LENGTH (IN Mtr) OF DWC+PCC (HARD ROCK)", 'LENGTH (IN Mtr) OF ANCORING']
def protection_summery(dir_path, districtName, blockName, boq_sd_df, excel_file):
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
    protection_details['LENGTH (IN Mtr) OF CULVERT'] = protection_['LENGTH (IN Mtr) OF CULVERT'].astype(float) - 6 * \
                                                       protection_[
                                                           'NO OF CULVERT'].astype(float)
    protection_details['NO OF BRIDGE'] = protection_['NO OF BRIDGE']
    protection_details['LENGTH (IN Mtr) OF BRIDE'] = protection_['LENGTH (IN Mtr) OF BRIDGE'].astype(float) - 6 * \
                                                     protection_[
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