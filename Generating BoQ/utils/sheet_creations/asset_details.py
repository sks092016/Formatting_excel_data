import pandas as pd
def asset_details(village_data, boq_sd_df, blockName, districtName, excel_file):
    district_code = next((item["District Code"] for item in village_data["Report"] if item["District Name"] == districtName.capitalize()), None)
    blockCode = next((item["Sub-District Code"] for item in village_data["Report"] if item["Sub-District Name"] == blockName.capitalize()), None)
    total_length = boq_sd_df['distance'].sum() / 1000
    # rings = boq_sd_df['ring_no'].unique()
    data_asset = {
        "Field": [
            "BLOCK NAME",
            "BLOCK CODE",
            "DISTRICT NAME",
            "DISTRICT CODE",
            "STATE NAME",
            "STATE CODE",
            "Block Router",
            "GP Router",
            "NO OF RING",
            "TOTAL INCRIMENTAL CABLE TO BE USE",
            "TOTAL PROPOSED CABLE TO BE LAID",
            "Block Type"
        ],
        "Value": [
            blockName,
            blockCode,
            districtName,
            district_code,
            "Madhya Pradesh",
            "23",
            "1",
            '',
            '',
            "0.00 KM",
            f"{total_length} KM",
            "Green Field"
        ]
    }

    # Create DataFrame
    df_asset = pd.DataFrame(data_asset)
    with pd.ExcelWriter(excel_file, engine='openpyxl',
                        mode='a') as writer:
        df_asset.to_excel(writer, sheet_name='Asset Details', index=False)
    print('Asset Details Created')