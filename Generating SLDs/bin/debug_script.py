import geopandas as gpd

# --- SETTINGS ---
shapefile = "input/OFC_NEW.shp"   # path to your shapefile
field_name = "span_name"           # field you want to filter by
filter_value = "FURTALA TO SIRWAD"                # value to match

# --- LOAD SHAPEFILE ---
gdf = gpd.read_file(shapefile)

# --- FILTER FEATURES ---
filtered = gdf[gdf[field_name] == filter_value]

# --- PRINT GEOMETRIES ---
for idx, row in filtered.iterrows():
    print(f"Feature {idx} | {field_name}={row[field_name]} | {row.OBJECTID}")
    try:
        print(row.geometry.wkt)  # prints geometry as WKT (LINESTRING, POINT, etc.)
        print("-" * 60)
    except Exception as e:
        print(e)