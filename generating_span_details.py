import pandas as pd

porsa_survey = pd.read_excel('excel_files/porsa_block_survey_data.xlsx', sheet_name='Sheet1')
cols = ['FROM','TO','ROUTE NAME','RING NO.','ROUTE TYPE','OFC TYPE','LAYING TYPE','ROUTE ID','TOTAL LENGTH(KM)','OH','UG']
span_details = pd.DataFrame(columns = cols)

span_ = porsa_survey[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
span_dis= porsa_survey.groupby('span_name').agg({'distance': 'sum'})
merged_df = pd.merge(span_, span_dis, on=['span_name'], how='inner')

span_details['FROM'] = merged_df['from_gp_na']
span_details['TO'] = merged_df['to_gp_name']
span_details['ROUTE NAME'] = merged_df['span_name']
span_details['RING NO.'] = merged_df['ring_no']
span_details['ROUTE TYPE'] = merged_df['scope']
span_details['OFC TYPE'] = '24F'
span_details['LAYING TYPE'] = 'UG'
span_details['ROUTE ID'] = merged_df['span_id']
span_details['TOTAL LENGTH(KM)'] = merged_df['distance']
span_details['OH'] = 0
span_details['UG'] = merged_df['distance']


with pd.ExcelWriter('excel_files/mapped_output_Porsa.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    span_details.to_excel(writer, sheet_name='Span Details', index=False)
