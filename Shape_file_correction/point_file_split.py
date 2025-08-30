import geopandas as gpd
import os

# Input shapefile
in_path = "input_point_shape_file/clusters_final.shp"
out_folder = "road_culvert_shape_file"

# Explicit values to split out
values_to_export = ["RD", "CP"]   # <-- put your desired values here

split_col = "Map Abbr"  # <-- the column to filter on

# Read file
gdf = gpd.read_file(in_path)

values =  gdf["Map Abbr"]
print(values)
# Create output folder
os.makedirs(out_folder, exist_ok=True)

# Loop through your explicit values
for val in values_to_export:
    subset = gdf[gdf[split_col] == val]
    if not subset.empty:
        safe_val = str(val).replace(" ", "_").replace("/", "_")
        out_path = os.path.join(out_folder, f"{split_col}_{safe_val}.shp")
        subset.to_file(out_path)
        print(f"✅ Saved {len(subset)} features → {out_path}")
    else:
        print(f"⚠️ No features found for {val}")