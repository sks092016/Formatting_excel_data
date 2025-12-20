from utils.api_calls import *
from utils.sheet_creations.excel_formatting import *
from utils.sheet_creations.bom_boq import *
from utils.sheet_creations.gpon import *
from utils.sheet_creations.railway_crossing import *
from utils.sheet_creations.gas_xing import *
from utils.sheet_creations.table_b import *
from utils.sheet_creations.annexure_x import *
from utils.sheet_creations.asset_details import *
from utils.sheet_creations.index import *
from utils.sheet_creations.row_preSurvey import *
from utils.sheet_creations.protection_summery import *
from utils.sheet_creations.row_summery import *
from utils.sheet_creations.span_details import *
from utils.sheet_creations.details_sheet import *

root = tk.Tk()
root.withdraw()
with open('village_district_code.json', 'r') as f:
    village_data = json.load(f)

# Reference Files
base_url = "https://fieldsurvey.rbt-ltd.com/app"
gdf_reference = gpd.read_file("Formats/OFC_NEW.shp")

# Reading the Shape File
shapefile_path = filedialog.askopenfilename(
    title="Select a shape file",
    filetypes=[("Shape Files", "*.shp"), ("All files", "*.*")]
)
gdf_working = gpd.read_file(shapefile_path)

# Creating the Directory for file store
blockName = gdf_working['block_name'][0]
districtName = gdf_working['district_n'][0]

# Select the Destination Folder
folder_path = filedialog.askdirectory(title="Select Destination Folder")
dir_path = Path(folder_path) / f"{districtName}-{blockName}-{version}"

# If it exists, delete it
if dir_path.exists() and dir_path.is_dir():
    shutil.rmtree(dir_path)  # Deletes the entire folder and its contents

# Now create it fresh
dir_path.mkdir(parents=True, exist_ok=False)
excel_file = dir_path / f"{districtName}-{blockName}-{version}.xlsx"

# Checking the Structure of the Files
is_structure_same = set(gdf_reference.columns) <= set(gdf_working.columns)
print(is_structure_same)
if not is_structure_same:
    col_diff_A = set(gdf_reference.columns) - set(gdf_working.columns)
    print("The Structure of the shape file is not matching the reference structure aborting. \n")
    time.sleep(0.5)
    print("Following columns are not present in the selected shape file:\n")
    time.sleep(0.5)
    print(col_diff_A)
else:
    print(gdf_working.columns)

# Creating the Common Span Details
span_ = gdf_working[['from_gp_na', 'to_gp_name', 'span_name', 'ring_no', 'scope', 'span_id']].drop_duplicates()
gdf_working['distance'] = pd.to_numeric(gdf_working['distance'], errors='coerce')
span_dis = gdf_working.groupby('span_name').agg({'distance': 'sum'})
boq_sd_df = pd.merge(span_, span_dis, on=['span_name'], how='inner')

if is_structure_same:
    # Creating the Details Sheet
    details_sheet(gdf_working, excel_file)
    #Generating the Span Details
    span_details(boq_sd_df, excel_file)
    # Generating the RoW Details
    row_summery(gdf_working, boq_sd_df, excel_file)
    # Generating the Protection Details
    protection_summery(dir_path, districtName, blockName, boq_sd_df, excel_file)
    # RoW PreSurvey
    row_presurvey(gdf_working, excel_file, blockName, districtName)
#INDEX
index(excel_file)

#ASSET DETAILS
asset_details(village_data, boq_sd_df, blockName, districtName, excel_file)

# Annexure -X
annexure_x(excel_file)

# Table B
table_b(excel_file)

#Gas Crossing
gas_xing(excel_file)

# Railway Crossing
railway_xing(excel_file)

# GPON
gpon(excel_file)

# BoQ & BOM
bom_boq(excel_file)

#Formatting the Excel Sheet
formatting_excel_file(excel_file)