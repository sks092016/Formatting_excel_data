import pandas as pd
def index(excel_file):
    data_ad = [
        {"Sl.No": 1, "Descrption": "ASSET DETAILS", "Status": "Yes", "Remarks": ""},
        {"Sl.No": 2, "Descrption": "ANNEEXURE-X_TABLE A", "Status": "Yes", "Remarks": ""},
        {"Sl.No": 3, "Descrption": "ANNEXURE X_TABLE-B", "Status": "Yes", "Remarks": ""},
        {"Sl.No": 5, "Descrption": "SPAN DETAILS", "Status": "Yes", "Remarks": ""},
        {"Sl.No": 6, "Descrption": "ROW", "Status": "Yes", "Remarks": ""},
        {"Sl.No": 7, "Descrption": "LINE DIAGRAM", "Status": "Yes", "Remarks": ""},
        {"Sl.No": 8, "Descrption": "Bill of Materials(BOM)", "Status": "Yes", "Remarks": ""},
        {"Sl.No": 9, "Descrption": "Bill of Quantity(BOQ)", "Status": "Yes", "Remarks": ""},
        {"Sl.No": 10, "Descrption": "Low Level Diagram(HLD)", "Status": "", "Remarks": ""},
        {"Sl.No": 11, "Descrption": "High Level Diagram(LLD)", "Status": "", "Remarks": ""},
        {"Sl.No": 12, "Descrption": "GPON", "Status": "Yes", "Remarks": ""},
        {"Sl.No": 13, "Descrption": "OTDR(Incremental)", "Status": "NA", "Remarks": ""},
        {"Sl.No": 14, "Descrption": "RM/MH Pictures(Incremental)", "Status": "NA", "Remarks": ""},
        {"Sl.No": 15, "Descrption": "BLOCK/GP Infra Pictures", "Status": "", "Remarks": ""},
        {"Sl.No": 16, "Descrption": "Route VideoGraphy", "Status": "", "Remarks": ""}
    ]

    # Create DataFrame
    df_index = pd.DataFrame(data_ad)
    with pd.ExcelWriter(excel_file, engine='openpyxl',
                        mode='a') as writer:
        df_index.to_excel(writer, sheet_name='Index', index=False)
    print('Index Created')