import pandas as pd

def annexure_x(excel_file):
    data_annex = {}
    df_annex = pd.DataFrame(data_annex)
    with pd.ExcelWriter(excel_file, engine='openpyxl',
                        mode='a') as writer:
        df_annex.to_excel(writer, sheet_name='Annexure X', index=False)
    print('Annexure X Created')