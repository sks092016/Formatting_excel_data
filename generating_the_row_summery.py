import pandas as pd
porsa_survey = pd.read_excel('excel_files/porsa_block_survey_data.xlsx', sheet_name='Sheet1')
cols = ['ROUTE NAME','ROUTE TYPE','RING NO','ROUTE ID','TOTAL ROUTE LENGTH','NHAI','PWD NH','PWD','ZILA PARISHAD','GP','MPRRDA','MUNICIPALITY','FOREST','RAILWAY XINGS(LEN)',
'RAILWAY XINGS(NOs)','GAIL XING(LEN)','GAIL XING(NOs)','ADANI XING(LEN)','ADANI XING(NOs)','IOCL XING(LEN)','IOCL XING(NOs)','HPCL XING(LEN)','HPCL XING(NOs)','OTHERS']

row_details = pd.DataFrame(columns = cols)

span_ = porsa_survey[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
span_dis= porsa_survey.groupby('span_name').agg({'distance': 'sum'})
merged_df = pd.merge(span_, span_dis, on=['span_name'], how='inner')
df2 = porsa_survey.pivot_table(values='distance', index='span_name', columns='road_autho', aggfunc='sum', fill_value=0).reset_index()
row_ = pd.merge(merged_df, df2, on=['span_name'], how='inner')

row_details['ROUTE NAME'] = row_['span_name']
row_details['ROUTE TYPE'] = row_['scope']
row_details['RING NO'] = row_['ring_no']
row_details['ROUTE ID'] = row_['span_id']
row_details['TOTAL ROUTE LENGTH'] = row_['distance']
row_details['NHAI'] = row_['NHAI']
row_details['PWD NH'] = 0
row_details['PWD'] = row_['PWD']
row_details['ZILA PARISHAD'] = 0
row_details['GP'] = row_['Grampanchyat']
row_details['MPRRDA'] = row_['PMGY']
row_details['MUNICIPALITY'] = 0
row_details['FOREST'] = row_['NHAI']
row_details['RAILWAY XINGS(LEN)'] = 0
row_details['RAILWAY XINGS(NOs)'] = 0
row_details['GAIL XING(LEN)'] = 0
row_details['GAIL XING(NOs)'] = 0
row_details['ADANI XING(LEN)'] = 0
row_details['ADANI XING(NOs)'] = 0
row_details['IOCL XING(LEN)'] = 0
row_details['IOCL XING(NOs)'] = 0
row_details['HPCL XING(LEN)'] = 0
row_details['HPCL XING(NOs)'] = 0
row_details['OTHERS'] = 0

with pd.ExcelWriter('excel_files/mapped_output_Porsa.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    row_details.to_excel(writer, sheet_name='RoW', index=False)

