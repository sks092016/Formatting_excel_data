import pandas as pd
cols = ['ROUTE NAME','ROUTE TYPE','TOTAL ROUTE LENGTH','NO OF CULVERT','LENGTH (IN Mtr) OF CULVERT','NO OF CANAL','LENGTH (IN Mtr) OF CANAL','NO OF BRIDGE','LENGTH (IN Mtr) OF BRIDE',
'LENGTH (IN Mtr) OF PCC','LENGTH (IN Mtr) OF DWC','LENGTH (IN Mtr) OF GI','LENGTH (IN Mtr) OF DWC+PCC','LENGTH (IN Mtr) OF ANCORING']
protection_details = pd.DataFrame(columns = cols)

survey = pd.read_excel('excel_files/Tarana Block/Tarana_block_survey.xlsx', sheet_name='Sheet1')
span_ = survey[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
span_dis = survey.groupby('span_name').agg({'distance': 'sum'})
merged_df = pd.merge(span_, span_dis, on=['span_name'], how='inner')

_details = pd.read_excel('excel_files/Tarana Block/Tarana-BoQ.xlsx', sheet_name='Details Sheet')

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
# protection_details['NO OF CANAL'] = protection_['NO OF CANAL']
# protection_details['LENGTH (IN Mtr) OF CANAL'] = protection_['LENGTH (IN Mtr) OF CANAL']
protection_details['NO OF BRIDGE'] = protection_['NO OF BRIDGE']
protection_details['LENGTH (IN Mtr) OF BRIDE'] = protection_['LENGTH (IN Mtr) OF BRIDGE']
protection_details['LENGTH (IN Mtr) OF PCC'] = protection_['DWC+PCC'] + protection_['GI+PCC']
protection_details['LENGTH (IN Mtr) OF DWC'] = protection_['DWC+PCC']
protection_details['LENGTH (IN Mtr) OF GI'] = protection_['GI+PCC']
protection_details['LENGTH (IN Mtr) OF DWC+PCC'] = protection_['DWC+PCC']
# protection_details['LENGTH (IN Mtr) OF ANCORING'] = (protection_['NO OF CULVERT'] + protection_['NO OF CANAL'] + protection_['NO OF BRIDGE'])*8
protection_details['LENGTH (IN Mtr) OF ANCORING'] = (protection_['NO OF CULVERT'] + protection_['NO OF BRIDGE'])*8

with pd.ExcelWriter('excel_files/Tarana Block/Tarana-BoQ.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    protection_details.to_excel(writer, sheet_name='Protection Details', index=False)