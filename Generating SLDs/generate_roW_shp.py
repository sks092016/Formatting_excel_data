import geopandas as gpd
from shapely.geometry import LineString

def merge_consecutive(group):
    """
    Merge only consecutive LineStrings with the same row_authority.
    If an authority repeats later (non-contiguous), it will be a new record.
    """
    merged = []
    current_geom = None
    current_auth = None
    current_seg = None

    for row in group.itertuples():
        if current_auth == row.road_autho:
            # Extend current line (merge consecutive segments)
            coords = list(current_geom.coords) + list(row.geometry.coords)[1:]
            current_geom = LineString(coords)
            current_seg = int(row.seg_seq)
        else:
            # Save previous block before switching
            if current_geom is not None:
                merged.append((row.span_name, current_auth, row.span_seq, current_geom))
            # Start a new merge block
            current_geom = row.geometry
            current_auth = row.road_autho
            current_seg = int(row.seg_seq)

    # Save last block
    if current_geom is not None:
        merged.append((row.span_name, current_auth, row.span_seq, current_geom))
    return merged


def process_shapefile(input_path, output_path):
    """Read, merge, and save shapefile with proper consecutive grouping."""
    gdf = gpd.read_file(input_path)

    results = []
    # Group by span & span_seq to preserve order
    for span, group in gdf.groupby(["span_name"], sort=False):
        group_sorted = group.sort_values(by="seg_seq", key=lambda col: col.astype(int))  # ensure order
        merged = merge_consecutive(group_sorted)
        results.extend(merged)

    # Convert to GeoDataFrame
    out_gdf = gpd.GeoDataFrame(
        results,
        columns=["span_name", "road_autho", "span_seq", "geometry"],
        geometry="geometry",
        crs=gdf.crs
    )

    out_gdf.to_file(output_path)
    print(f"✅ Output written to {output_path}")


if __name__ == "__main__":
    # Example: change these paths as needed
    input_file = "input/Ofc_New_Khaniadhana_1.0_Seg_Span_Seq.shp"
    output_file = "output/row_clubbed_file.shp"
    process_shapefile(input_file, output_file)
