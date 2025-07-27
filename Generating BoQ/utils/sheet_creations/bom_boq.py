import pandas as pd
def bom_boq(excel_file):
    bom = {}
    df_bom = pd.DataFrame(bom)
    with pd.ExcelWriter(excel_file, engine='openpyxl',mode='a') as writer:
        df_bom.to_excel(writer, sheet_name='BOM', index=False)
    df_boq = pd.DataFrame(bom)
    with pd.ExcelWriter(excel_file, engine='openpyxl',mode='a') as writer:
        df_boq.to_excel(writer, sheet_name='BOQ', index=False)
    print('BOM BOQ Created')