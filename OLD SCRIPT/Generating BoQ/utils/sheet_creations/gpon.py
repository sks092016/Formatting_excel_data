import pandas as pd

def gpon(excel_file):
    columns_gpon = [
        "Block/GP Name",
        "Survey Location Type (Block/GP)",
        "Block/GP Address",
        "LGD Code",
        "Lat Long",
        "Location Type [BSNL Office/ BSNL Exchange/RSU/BTS/GP Office/School/ Other Building] in case of the other building pls specify the location type",
        "Location Secured and Locked/other. in case of the other pls specify",
        "Total Rack Available: 0/1/2",
        "FDF Installed [YES/NO]",
        "FDF Type [12F/24F/48F/other] in case of the other pls specify",
        "Terminated OFC Type 24/48F or other. in case of the other pls specify",
        "Nos of spare fiber available",
        "No of FDF PORT Used",
        "Make/Model",
        "Type",
        "Nos",
        "Types (SCM/PIC)",
        "Name",
        "Qty",
        "Working Status",
        "Equipment Type ((OLT/ONT))",
        "S.No",
        "Make",
        "Model",
        "CCU",
        "Battery",
        "OLT",
        "ONT",
        "Solar",
        "POWER Connection Status (Yes/No) if Yes please specify [1-Phase/3-Phase]",
        "Average Power Availability [No of Hours in a Day]",
        "POWER Back up Available (Yes/No)",
        "Solar/DC/AC Backup",
        "Capacity of backup in KVA/KWA",
        "Earth Pit-Lat/Long",
        "Strip (M) + Gauge",
        "Wire (M)",
        "ONT Installed / Commissioned [Yes/No]",
        "In case Yes, powered \"ON\" or \"OFF\"",
        "ZMH entry Location (Lat-Long)",
        "OFC entry Location (Lat-Long)"
    ]

    df_gpon = pd.DataFrame(columns=columns_gpon)
    with pd.ExcelWriter(excel_file, engine='openpyxl',
                        mode='a') as writer:
        df_gpon.to_excel(writer, sheet_name='GPON', index=False)

    print('GPON Created')
