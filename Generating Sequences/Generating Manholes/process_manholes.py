from methods import *

block_name = "Bhitawar"
crs = "EPSG:4326"
input_shapefile = f'input/OFC_New_{block_name}-1_Seg_Span_Seq.shp'
output_json = f"temp/custom_points_{block_name}.json"

#-------------------------------Finding the Sharp-points ----------------------------------------
angle_threshold = 90
group_field = "span_name"
sharp_turn_shape = f"temp/sharp_turn_points_{block_name}.shp"

sharp_points, json_records, gdf = find_sharp_turns(input_shapefile, sharp_turn_shape, output_json, angle_threshold, group_field)
if sharp_points:
    out_gdf = gpd.GeoDataFrame(sharp_points, crs=gdf.crs)
    out_gdf.to_file(sharp_turn_shape)
    print(f"✅ Sharp turn points saved to: {sharp_turn_shape}")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(json_records, f, indent=4)
    print(f"✅ JSON file saved to: {output_json}")
else:
    print("No sharp turns found under the given threshold.")

#-----------------------------Processing the Brown Field Data--------------------------------
scope = "brown field data"
brown_field_label = "Brown Field Conn"
ptype = "Brown Field"
shape_file_data_field = 'ofc_laying'

brown_field_points = f"temp/brown_field_manholes_{block_name}.shp"

process_brown_field(input_shapefile, brown_field_points, output_json, scope,crs, brown_field_label, ptype, shape_file_data_field)

#-----------------------------Process final Manholes -----------------------------------------
gdf = gpd.read_file(input_shapefile)
span_list = gdf.sort_values('span_name').span_name.unique()
temp_merged = gpd.GeoDataFrame(columns=['label', 'ptype', 'dist_m', 'geometry', 'span'], crs=gdf.crs)
merged = gpd.GeoDataFrame(columns=['label', 'ptype', 'dist_m', 'geometry', 'span'], crs=gdf.crs)
for s in span_list:
    if s is not None:
        try:
            out_gdf, main_line, temp_gdf = process_shapefile(
                input_shapefile,
                span_filter=s,
                crossing_offset=10.0,
                feature_endpoint_offset=5.0,
                crossing_types=None,
                crossing_field="crossing_t",
                distance_interval=1800.0,
                min_buffer=150.0,
                small_crossing_thresh=100.0,
                manual_points_json=output_json  # set to "manual_points.json" to include manual points
            )
            temp_merged = gpd.GeoDataFrame(pd.concat([temp_merged, temp_gdf], ignore_index=True), crs=merged.crs)
            merged = gpd.GeoDataFrame(pd.concat([merged,out_gdf], ignore_index=True), crs=merged.crs)
            temp_merged.to_file(f"temp/Temp_manholes-{block_name}.shp")
            merged.to_file(f"output/manholes-{block_name}.shp")
        except:
            continue
    else:
        continue
