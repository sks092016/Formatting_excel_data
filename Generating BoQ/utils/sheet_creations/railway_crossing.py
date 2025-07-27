import pandas as pd
def railway_xing(excel_file):
    columns_rlwy = [
        "Sr. No.",
        "Block/GP Link Name",
        "Sub Route Name",
        "Latitude",
        "Longitude",
        "Pole no. 1 LHS",
        "Pole no. 2 LHS",
        "Pole no.1 RHS",
        "Pole no.2 RHS",
        "Village name",
        "Tehsil name",
        "District name",
        "Length of total railway land involved in crossing (Mtrs)",
        "Distance of proposed crossing from electric pole (Mtrs)",
        "Height of Rails from formation level (Mtrs)",
        "Height of Rails from ground level (Mtrs)",
        "Name of both sides of railway station",
        "Total no. of railway tracks (Nos.)",
        "Pit Latlong (in)",
        "Pit Latlong (Out)"
    ]
    # Create empty DataFrame with these columns
    df_rlwy = pd.DataFrame(columns=columns_rlwy)
    with pd.ExcelWriter(excel_file, engine='openpyxl',mode='a') as writer:
        df_rlwy.to_excel(writer, sheet_name='Railway Crossing', index=False)
    print('Railway Crossing Created')