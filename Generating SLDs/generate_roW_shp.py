import geopandas as gpd
from shapely.geometry import LineString,Point
from pyproj import Geod
import json
from shapely.ops import transform
import pyproj
block = "Gandhwani"
def line_length_meter(line):
    geod = Geod(ellps="WGS84")
    length_m = geod.line_length(
        [p[0] for p in line.coords],  # longitudes
        [p[1] for p in line.coords]  # latitudes
    )
    return length_m

def reverse_geom(geom):
    return LineString(list(geom.coords)[::-1])

def merge_consecutive(group):
    """
    Merge only consecutive LineStrings with the same row_authority.
    If an authority repeats later (non-contiguous), it will be a new record.
    """
    merged = []
    current_geom = None
    current_auth = None
    first_seq = None
    st_ch = 0
    end_ch = 0
    current_length = 0
    ring = ''

    for idx, row in enumerate(group.itertuples()):
        if current_auth == row.road_autho:
            new_geom = row.geometry
            try:
                if current_geom.coords[-1] == new_geom.coords[0]:
                    # Case 1: Already aligned (end-to-start)
                    pass
                elif current_geom.coords[-1] == new_geom.coords[-1]:
                    # Case 2: Reverse new so end matches start
                    new_geom = LineString(list(new_geom.coords)[::-1])
                elif current_geom.coords[0] == new_geom.coords[-1]:
                    # Case 3: Reverse current so start matches end
                    current_geom = LineString(list(current_geom.coords)[::-1])
                    new_geom = LineString(list(new_geom.coords)[::-1])
                elif current_geom.coords[0] == new_geom.coords[0]:
                    # Case 4: Reverse both so they align
                    current_geom = LineString(list(current_geom.coords)[::-1])
                else:
                    # No match → skip or handle separately
                    continue
                coords = list(current_geom.coords) + list(new_geom.coords)[1:]
                current_geom = LineString(coords)
            except Exception as e:
                print(row.OBJECTID)
                print(row.geometry)
                print(e)
                continue
        else:
            # Save previous block before switching
            if current_geom is not None:
                current_length = line_length_meter(current_geom)
                end_ch += current_length
                next_geom = group.iloc[current_idx + 1].geometry
                if current_geom.coords[-1] == next_geom.coords[0]:
                    pass  # Already correct
                elif current_geom.coords[0] == next_geom.coords[0]:
                    current_geom = reverse_geom(current_geom)
                elif current_geom.coords[0] == next_geom.coords[-1]:
                    current_geom = reverse_geom(current_geom)
                merged.append((row.span_name, current_auth, row.span_id,ring,first_seq,current_length,st_ch,end_ch,current_geom))
            # Start a new merge block
            current_geom = row.geometry
            current_auth = row.road_autho
            first_seq = row.Sequqnce
            ring = row.ring_no
            current_idx = idx
            if first_seq == 1:
                st_ch = 0.0
            else:
                st_ch = end_ch
            current_length = 0
    # Save last block
    if current_geom is not None:
        current_length = line_length_meter(current_geom)
        end_ch += current_length
        merged.append(
            (row.span_name, current_auth, row.span_id, ring ,first_seq, current_length, st_ch, end_ch, current_geom))
    return merged

def process_shapefile(input_path, output_path):
    """Read, merge, and save shapefile with proper consecutive grouping."""
    gdf = gpd.read_file(input_path)

    results = []
    # Group by span & span_seq to preserve order
    for span, group in gdf.groupby(["span_name"], sort=False):
        group_sorted = group.sort_values(by="Sequqnce", key=lambda col: col.astype(float))  # ensure order
        merged = merge_consecutive(group_sorted)
        results.extend(merged)

    # Convert to GeoDataFrame
    out_gdf = gpd.GeoDataFrame(
        results,
        columns=["span_name","road_autho","span_seq","ring","first_segment",'length','st_ch','end_ch',"geometry"],
        geometry="geometry",
        crs=gdf.crs
    )

    out_gdf.to_file(output_path)
    print(f"✅ Output written to {output_path}")
    return out_gdf

def process_span_data(input_gdf, output_shapefile, output_json):
    # Ensure CRS is WGS84
    if input_gdf.crs is None or input_gdf.crs.to_epsg() != 4326:
        input_gdf = input_gdf.to_crs(epsg=4326)

    output_rows = []
    span_details = {}

    # Process each span_name separately
    for span, group in input_gdf.groupby("span_name", sort=False):
        group = group.sort_values(by="st_ch")

        # Add to JSON aggregation
        span_details[span] = group.groupby("road_autho")["length"].sum().to_dict()
        span_details[span]['Ring'] = group['ring'].unique().tolist()[0]
        span_details[span]['Span_id'] = group['span_seq'].unique().tolist()[0]
        # Extract start & end points with chainages
        start_point_name = span.split(" TO ")[0].strip()
        end_point_name = span.split(" TO ")[-1].strip()

        for idx, row in group.iterrows():
            coords = list(row.geometry.coords)

            # First row start point
            if row["st_ch"] == group["st_ch"].min():
                output_rows.append({
                    "span_name": span,
                    "Point Name": start_point_name,
                    "ring": span_details[span]["Ring"],
                    "Chainage": row["st_ch"],
                    "geometry": Point(coords[0])
                })

            # Intermediate points (start of segment except first)
            if row["st_ch"] != group["st_ch"].min():
                output_rows.append({
                    "span_name": span,
                    "Point Name": "",
                    "ring": span_details[span]["Ring"],
                    "Chainage": row["st_ch"],
                    "geometry": Point(coords[0])
                })

            # Last segment end point
            if row["end_ch"] == group["end_ch"].max():
                output_rows.append({
                    "span_name": span,
                    "Point Name": end_point_name,
                    "ring": span_details[span]["Ring"],
                    "Chainage": row["end_ch"],
                    "geometry": Point(coords[-1])
                })

    # Create output GeoDataFrame
    output_gdf = gpd.GeoDataFrame(output_rows, crs="EPSG:4326")

    # Save shapefile
    output_gdf.to_file(output_shapefile)

    # Save JSON
    with open(output_json, "w") as f:
        json.dump(span_details, f, indent=4)

    return output_gdf, span_details

if __name__ == "__main__":
    # Example: change these paths as needed
    input_file = "input/OFC_NEW.shp"
    output_file = f"output/RoW Authorities-{block}.shp"
    input_gdf = process_shapefile(input_file, output_file)

    input_shape_file = output_file
    output_shape_file = f"output/output_points-{block}.shp"
    output_json = f"output/span_details-{block}.json"
    gdf = gpd.read_file(input_shape_file)

    output_gdf, span_details = process_span_data(gdf, output_shape_file, output_json)

    print("✅ Shapefile saved:", output_shape_file)
    print("✅ JSON saved:", output_json)

