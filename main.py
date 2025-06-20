import pandas as pd
import openpyxl
# Reading the Excel file
df = pd.read_excel('tarana_ofc_survey.xlsx')

# Creating a dictionary to track serial numbers for each Span_Name
span_serials = {}
current_serial = 1

# Iterating through the DataFrame in original order
for index, row in df.iterrows():
    span_name = row['span_name']
    if span_name not in span_serials:
        # Start a new serial sequence for a new Span_Name
        span_serials[span_name] = 1
    else:
        # Increment the serial for the current Span_Name
        span_serials[span_name] += 1
    # Assign the serial number to the SPAN_CONTINUITY column
    df.at[index, 'SPAN_CONTINUITY'] = span_serials[span_name]

# Saving the modified DataFrame back to an Excel file
df.to_excel('tarana_updated.xlsx', index=False)
