import pandas as pd

def finding_pipeline(row, df, auth):
    span_ = row['span_name']
    df = df[df.span_name == span_]
    count = df['end_point_'].str.contains(auth,case=False, na=False).sum()
    return count
def finding_xing_length(row, df, auth):
    span_ = row['span_name']
    df = df[df.span_name == span_]
    mask = df['end_point_'].str.contains(auth,case=False, na=False)
    length = df.loc[mask, 'crossing_l'].sum()
    return length

_survey = pd.read_excel('excel_files/Tarana Block/Tarana_block_survey.xlsx', sheet_name='Sheet1')
cols = ['ROUTE NAME','ROUTE TYPE','RING NO','ROUTE ID','TOTAL ROUTE LENGTH','NHAI','PWD NH','PWD','NAGAR PARISHAD','GP','MPRRDA','MUNICIPALITY','FOREST','SH','ODR','RAILWAY XINGS(LEN)',
'RAILWAY XINGS(NOs)','GAS XING(LEN)','GAS XING(NOs)','ADANI XING(LEN)','ADANI XING(NOs)','IOCL XING(LEN)','IOCL XING(NOs)','HPCL XING(LEN)','HPCL XING(NOs)','OTHERS']

row_details = pd.DataFrame(columns = cols)

span_ = _survey[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
span_dis= _survey.groupby('span_name').agg({'distance': 'sum'})
merged_df = pd.merge(span_, span_dis, on=['span_name'], how='inner')
df2 = _survey.pivot_table(values='distance', index='span_name', columns='road_autho', aggfunc='sum', fill_value=0).reset_index()
row_ = pd.merge(merged_df, df2, on=['span_name'], how='inner')

row_details['ROUTE NAME'] = row_['span_name']
row_details['ROUTE TYPE'] = row_['scope']
row_details['RING NO'] = row_['ring_no']
row_details['ROUTE ID'] = row_['span_id']
row_details['TOTAL ROUTE LENGTH'] = row_['distance']
row_details['NHAI'] = row_['NHAI']
row_details['PWD NH'] = 0
row_details['PWD'] = row_['PWD']
row_details['NAGAR PARISHAD'] = row_['Nagar Parishad']
row_details['GP'] = row_['Grampanchyat']
row_details['SH'] = row_['SH']
row_details['ODR'] = row_['ODR']
row_details['MPRRDA'] = row_['PMGY']
row_details['MUNICIPALITY'] = 0
row_details['FOREST'] = row_['Forest']
row_details['RAILWAY XINGS(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'railway'))
row_details['RAILWAY XINGS(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'railway'))
row_details['GAS XING(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'gas'))
row_details['GAS XING(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'gas'))
row_details['ADANI XING(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'adani'))
row_details['ADANI XING(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'adani'))
row_details['IOCL XING(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'iocl'))
row_details['IOCL XING(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'iocl'))
row_details['HPCL XING(LEN)'] = row_.apply(finding_xing_length, axis=1, args=(_survey, 'hpcl'))
row_details['HPCL XING(NOs)'] = row_.apply(finding_pipeline, axis=1, args=(_survey, 'hpcl'))
row_details['OTHERS'] = 0

with pd.ExcelWriter('excel_files/Tarana Block/Tarana-BoQ.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    row_details.to_excel(writer, sheet_name='RoW', index=False)

