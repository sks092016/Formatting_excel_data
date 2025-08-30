import geopandas as gpd
from shapely.geometry import Point
import os

# Input shapefile
in_path = "road_culvert_shape_file/Map Abbr_RD.shp"
out_folder = "output_centroids"

gdf = gpd.read_file(in_path)

# Make sure ID column exists (replace 'id' with your actual column name)
id_col = "id"  # <-- replace with your highest-id column

# Group by span_name and cluster_id
centroid_records = []
for (span, cluster), group in gdf.groupby(["span_name", "cluster_id"]):
    # compute mean x,y
    mean_x = group.geometry.x.mean()
    mean_y = group.geometry.y.mean()
    centroid = Point(mean_x, mean_y)

    # get row with highest ID
    max_row = group.loc[group[id_col].idxmax()]

    # create new record
    record = max_row.copy()
    record.geometry = centroid
    centroid_records.append(record)

# Create GeoDataFrame with centroids
centroids_gdf = gpd.GeoDataFrame(centroid_records, crs=gdf.crs)

# --- Option A: save one combined centroid shapefile
out_path = os.path.join(out_folder, "all_centroids.shp")
os.makedirs(out_folder, exist_ok=True)
centroids_gdf.to_file(out_path)

# --- Option B: save separate shapefiles for each span_name
for span, group in centroids_gdf.groupby("span_name"):
    span_out = os.path.join(out_folder, f"centroids_{span}.shp")
    group.to_file(span_out)
    print(f"Saved {len(group)} centroids → {span_out}")

print("✅ Done")
