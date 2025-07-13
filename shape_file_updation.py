import geopandas as gpd
import pandas as pd
# === CONFIGURATION ===
source_path = "/Users/subhashsoni/Documents/Bharatnet_OFC_planning/Shapefile Badarwas/Culvert_Bridge.shp"  # File that contains reference geometries and values
target_path = "/Users/subhashsoni/Documents/Bharatnet_OFC_planning/Shapefile Badarwas/OFC_NEW.shp"  # File you want to update

source_column = "Name"       # Column in source to copy value from
target_column_to_update = "end_point_"  # Column in target to update

# === LOAD SHAPEFILES ===
source_gdf = gpd.read_file(source_path)
target_gdf = gpd.read_file(target_path)

# Ensure same CRS
if source_gdf.crs != target_gdf.crs:
    target_gdf = target_gdf.to_crs(source_gdf.crs)
count = 0
for _, row in target_gdf.iterrows():
    for ind,r in source_gdf.iterrows():
        if row['geometry'] == r["geometry"]:
            print(row['distance'])
            row['end_point_'] = r['Name'] + "-" + "Crossing"
            count = count + 1
print(count)

# # === FIND OVERLAPS ===
# # Spatial join to find overlaps between target and source
# overlaps = gpd.sjoin(target_gdf, source_gdf[[source_column, 'geometry']], how="inner", predicate="intersects").reset_index(drop=True)
#
# # `overlaps` will now contain the source_column from source_gdf if overlapping, else NaN
#
# # === UPDATE ORIGINAL TARGET GDF ===
# # We'll update the original `target_gdf` only for rows where a match was found
#
# string_prefix = 'Crossing'
# target_gdf[target_column_to_update] = overlaps[source_column].apply(
#     lambda val: f"{string_prefix}-{val}" if pd.notna(val) else None
# )
#
# # === SAVE UPDATED TARGET FILE (overwriting original) ===
# target_gdf.to_file(target_path, driver="ESRI Shapefile")
#
# print(f"Updated {overlaps[source_column].notna().sum()} geometries in '{target_path}' based on overlaps with '{source_path}'.")
