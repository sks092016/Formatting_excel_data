import geopandas as gpd

# Load shapefiles
source = gpd.read_file("input/OFC_NEW.shp")
target = gpd.read_file("input/OFC_New_Gangev-1_Seg_Span_Seq.shp")

target["crossing_t"] = source["crossing_t"]
target.to_file("output/OFC_New_Gangev-1_Seg_Span_Seq.shp")

print("✅ Field values copied successfully!")
