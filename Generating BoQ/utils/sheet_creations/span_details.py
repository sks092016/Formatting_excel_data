from .. methods import *

cols_sd = ['FROM', 'TO', 'ROUTE NAME', 'RING NO.', 'ROUTE TYPE', 'OFC TYPE', 'LAYING TYPE', 'ROUTE ID',
               'TOTAL LENGTH(KM)',
               'OH', 'UG']
def span_details(boq_sd_df, excel_file):
    span_details = pd.DataFrame(columns=cols_sd)
    span_details['FROM'] = boq_sd_df['from_gp_na']
    span_details['TO'] = boq_sd_df['to_gp_name']
    span_details['ROUTE NAME'] = boq_sd_df['span_name']
    span_details['RING NO.'] = boq_sd_df['ring_no']
    span_details['ROUTE TYPE'] = 'OFC to be laid for Ring Formation (in Km)'
    span_details['OFC TYPE'] = '48F'
    span_details['LAYING TYPE'] = 'UG'
    span_details['ROUTE ID'] = boq_sd_df['span_id']
    span_details['TOTAL LENGTH(KM)'] = boq_sd_df['distance'] / 1000
    span_details['OH'] = 0
    span_details['UG'] = boq_sd_df['distance'] / 1000

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a',
                        if_sheet_exists='replace') as writer:
        span_details.to_excel(writer, sheet_name='Span Details', index=False)
    print('Span Details Created')