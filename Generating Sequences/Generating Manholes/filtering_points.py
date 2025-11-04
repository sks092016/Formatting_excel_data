import geopandas as gpd
from shapely.geometry import Point, LineString, MultiLineString

def filter_points(points_path, lines_path, output_path,
                  line_field, line_value, point_field=None, keep_value=None):
    print("[*] Loading shapefiles...")
    points = gpd.read_file(points_path)
    lines = gpd.read_file(lines_path)

    # Ensure CRS matches
    if points.crs != lines.crs:
        print("[*] Aligning CRS...")
        lines = lines.to_crs(points.crs)

    # Filter lines with specified attribute
    print(f"[*] Filtering lines where {line_field} == '{line_value}' ...")
    target_lines = lines[lines[line_field] == line_value]
    if target_lines.empty:
        print("[!] No matching lines found, all points will be kept.")
        points.to_file(output_path)
        return

    # Combine geometries for faster processing
    line_union = target_lines.unary_union

    # --- Filtering logic ---
    keep_mask = []

    print("[*] Checking points...")

    for idx, pt in points.iterrows():
        point_geom = pt.geometry

        # Always keep point if it matches the compulsory keep condition
        if point_field and keep_value is not None:
            if pt[point_field] == keep_value:
                keep_mask.append(True)
                continue

        # Otherwise, remove if point lies exactly on line geometry
        on_line = point_geom.intersects(line_union)
        keep_mask.append(not on_line)

    # Apply mask
    filtered_points = points[keep_mask]

    print(f"[✔] Done. Input points: {len(points)}, kept: {len(filtered_points)}, removed: {len(points) - len(filtered_points)}")

    # Save filtered output
    print(f"[*] Writing to {output_path} ...")
    filtered_points.to_file(output_path)
    print("[✔] Output shapefile saved successfully.")

# --- Main entry point ---
if __name__ == "__main__":
    block_name = "Karanjiya"
    points_path = f"output/manholes-{block_name}.shp"
    lines_path = f'input/OFC_New_{block_name}-1_Seg_Span_Seq.shp'
    output_path = f"output/manholes-{block_name}-final.shp"
    line_field = 'scope'
    line_value = 'Karanjiya Brown Field GIS Data; To be replecement'
    point_field = 'ptype'
    keep_value = 'Brown Field'


    filter_points(points_path, lines_path, output_path, line_field, line_value, point_field, keep_value)
