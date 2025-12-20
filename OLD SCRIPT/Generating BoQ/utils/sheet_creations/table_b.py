import pandas as pd
def table_b(excel_file):
    columns_table_b = [
        "S.No.",
        "Block Name with LGD Code",
        "Name of GP",
        "GP LGD Code",
        "Availability of space Yes/ No",
        "Commercial Electric Supply Availability Yes/No",
        "Availability of Power Supply in Hrs.",
        "OLT Avalable/Not available",
        "Remarks",
        "Router"
    ]
    # Create empty DataFrame with these columns
    df_table_b = pd.DataFrame(columns=columns_table_b)
    with pd.ExcelWriter(excel_file, engine='openpyxl',
                        mode='a') as writer:
        df_table_b.to_excel(writer, sheet_name='Table B', index=False)
    print('Table B Created')