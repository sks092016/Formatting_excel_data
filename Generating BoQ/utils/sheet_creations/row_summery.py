from .. methods import *

def row_summery(gdf_working,boq_sd_df, excel_file):
    authorities = gdf_working['road_autho'].unique()
    cols_row = ['ROUTE NAME', 'ROUTE TYPE', 'RING NO', 'ROUTE ID', 'TOTAL ROUTE LENGTH'] + list(authorities)
    row_details = pd.DataFrame(columns=cols_row)
    df2 = gdf_working.pivot_table(values='distance', index='span_name', columns='road_autho', aggfunc='sum',
                                  fill_value=0).reset_index()
    row_ = pd.merge(boq_sd_df, df2, on=['span_name'], how='inner')
    row_details['ROUTE NAME'] = row_['span_name']
    row_details['ROUTE TYPE'] = row_['scope']
    row_details['RING NO'] = row_['ring_no']
    row_details['ROUTE ID'] = row_['span_id']
    row_details['TOTAL ROUTE LENGTH'] = row_['distance'] / 1000
    for auths in authorities:
        row_details[auths] = row_[auths] / 1000
    row_details['OTHERS'] = 0

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a',
                        if_sheet_exists='replace') as writer:
        row_details.to_excel(writer, sheet_name='RoW', index=False)
    print('RoW Summery Created')