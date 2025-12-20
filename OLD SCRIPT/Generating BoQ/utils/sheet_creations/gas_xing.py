import pandas as pd

def gas_xing(excel_file):
    columns_gas = [
        "Sub Route Name",
        "Ring-Name",
        "Name of Gas/Oil pipeline Xing Co. (GAIL/BPCL/IOCL/IHB)",
        "Pipeline name as per signboard",
        "Gas/Oil pipeline Chainage as per signboard",
        "Latitude",
        "Longitude",
        "Landmark",
        "Village name",
        "SLD Status",
        "Tehsil name",
        "District name"
    ]

    # Create empty DataFrame with these columns
    df_gas = pd.DataFrame(columns=columns_gas)
    with pd.ExcelWriter(excel_file, engine='openpyxl',
                        mode='a') as writer:
        df_gas.to_excel(writer, sheet_name='Gas Crossing', index=False)
    print('Gas Crossing Created')