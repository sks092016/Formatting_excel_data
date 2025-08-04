# Full corrected script based on your original logic with the first-segment-reversal fix included
import pandas as pd
from collections import Counter
from ring_start_point_cordinates import *
from methods import *

############################ Reversing the Geometry and Filling up the sequence in Segments ################################
# ╔══════════════════════════════════════════════════════════════╗
# ║   WORK CREATING SEGMENT SEQUENCE & reversing Geometry        ║
# ╚══════════════════════════════════════════════════════════════╝

ensure_epsg4326(segments_shape_file, "References/GUNA-SHP/GUNA-SHP_4326.shp")

# Load the input shapefile
gdf = gpd.read_file(segments_shape_file)

gdf_gp = gpd.read_file(gps_shape_file)

# Create empty GeoDataFrames with correct structures
gdf_new_sp = gdf.iloc[0:0].copy()
gdf_new_sp["seg_seq"] = None

gdf_span = gpd.GeoDataFrame(columns=['span_name', 'ring', 'start_cord', 'end_cord', 'span_seq', 'geometry'], geometry='geometry')
error_gdf = gpd.GeoDataFrame(columns=['span_name', 'error','geometry'], geometry='geometry')

# Process each span
span_list = gdf.sort_values('span_name').span_name.unique()

for s in span_list:
    temp_df = gdf[gdf.span_name == s].copy()
    temp_df['geometry'].to_clipboard(index=False, header=False)
    temp_df['start'] = temp_df.geometry.apply(lambda geom: get_start_end_coords(geom)[0])
    temp_df['end'] = temp_df.geometry.apply(lambda geom: get_start_end_coords(geom)[1])

    start_gp = smart_split(s)
    try:
        s_c = gdf_gp[gdf_gp.name == start_gp].geometry.iloc[0]
    except:
        print(f"GP Cordinate not matching {start_gp} and {s}")
        s_c = None
    gp_node = get_coords(s_c)
    sorted_indices = []
    remaining = temp_df.copy()
    #___________
    # === STEP 1: Find the true starting segment ===
    # Count how many times each endpoint appears
    all_endpoints = list(temp_df['start']) + list(temp_df['end'])
    counts = Counter(all_endpoints)

    # True start nodes are endpoints that appear only once
    true_starts = [pt for pt, c in counts.items() if c == 1]

    node1 = true_starts[0]
    node2 = true_starts[1]

    if gp_node is not None:
        try:
            segment_of_gp_node = temp_df[
                (temp_df['start'] == gp_node) | (temp_df['end'] == gp_node)].iloc[0]
            start_row = segment_of_gp_node
            start_node = gp_node
        except:
            candidates = temp_df["start"].tolist() + temp_df["end"].tolist()
            candidate_points = [Point(x, y) for (x, y) in candidates]
            nearest = min(candidate_points, key=lambda pt: pt.distance(Point(gp_node)))
            nearest_coords = (nearest.x, nearest.y)
            segment_of_nearest_node = temp_df[
                (temp_df['start'] == nearest_coords) | (temp_df['end'] == nearest_coords)].iloc[0]
            start_row = segment_of_nearest_node
            start_node = nearest
            print("Gp Node executed")
    else:
        segment_of_node1 = temp_df[
            (temp_df['start'] == node1) | (temp_df['end'] == node1)].iloc[0]

        segment_of_node2 = temp_df[
            (temp_df['start'] == node2) | (temp_df['end'] == node2)].iloc[0]

        print("Node logic executed")
        if int(segment_of_node1.OBJECTID) < int(segment_of_node2.OBJECTID):
            start_row = segment_of_node1
            start_node = node1
        else:
            start_row = segment_of_node2
            start_node = node2
    # Find the row (segment) that touches the chosen start node

    current_idx = start_row.name
    current = start_row.copy()

    # If the segment is reversed (end == start_node), flip geometry
    if current['end'] == start_node:
        flipped_geom = LineString(list(current['geometry'].coords)[::-1])
        temp_df.at[current_idx, 'geometry'] = flipped_geom
        current['geometry'] = flipped_geom
        current['start'], current['end'] = list(flipped_geom.coords)[0], list(flipped_geom.coords)[-1]

    # Initialize sorted list with this true starting segment
    sorted_indices.append(current_idx)
    remaining = remaining.drop(index=current_idx)

    # === STEP 2: Traverse and sequence segments ===
    while not remaining.empty:
        found = False
        for idx, row in remaining.iterrows():
            # Case 1: Normal forward connection
            if row['start'] == current['end']:
                sorted_indices.append(idx)
                current = row
                remaining = remaining.drop(idx)
                found = True
                break
            # Case 2: Reversed row connects forward
            elif row['end'] == current['end']:
                reversed_geom = LineString(list(row['geometry'].coords)[::-1])
                temp_df.at[idx, 'geometry'] = reversed_geom
                row['geometry'] = reversed_geom
                row['start'], row['end'] = get_start_end_coords(reversed_geom)
                sorted_indices.append(idx)
                current = row
                remaining = remaining.drop(idx)
                found = True
                break
            # Case 3: Reversed row connects to current start (if path loops backward)
            elif row['end'] == current['start']:
                reversed_geom = LineString(list(row['geometry'].coords)[::-1])
                temp_df.at[idx, 'geometry'] = reversed_geom
                row['geometry'] = reversed_geom
                row['start'], row['end'] = get_start_end_coords(reversed_geom)
                sorted_indices.insert(0, idx)
                current = row
                remaining = remaining.drop(idx)
                found = True
                break
        if not found:
            logging.warning(f"⚠️ Warning: Disconnected segment remains in span '{s}'.")
            logging.warning(f"⚠️ The Span {s} is disconnected at this point {current['end']}")
            error_row = gpd.GeoDataFrame([{
                'span_name': s,
                'error': "The Span {s} is disconnected at this point",
                'geometry': Point(current['end']),
            }], geometry='geometry', crs=temp_df.crs)
            error_gdf = pd.concat([error_gdf, error_row], ignore_index=True)
            break

    # Assign segment sequence
    sequence_series = temp_df.index.to_series().apply(
        lambda x: sorted_indices.index(x) + 1 if x in sorted_indices else None
    )
    temp_df['seg_seq'] = sequence_series
    temp_df = temp_df.drop(columns=['start', 'end'])

    # Merge geometry
    complete_span_line = merged_line_geometry(temp_df.loc[sorted_indices].geometry)

    # Add span-level geometry
    new_span_row = gpd.GeoDataFrame([{
        'span_name': s,
        'ring': str(temp_df.loc[temp_df.index[0], 'ring_no']),
        'start_cord': get_start_end_coords(complete_span_line)[0],
        'end_cord': get_start_end_coords(complete_span_line)[1],
        'span_seq': '',
        'geometry': complete_span_line
    }], geometry='geometry', crs=temp_df.crs)

    gdf_span = pd.concat([gdf_span, new_span_row], ignore_index=True)

    # Append ordered segments to master output
    assert gdf_new_sp.crs == temp_df.crs, "CRS mismatch!"
    gdf_new_sp = pd.concat([gdf_new_sp, temp_df])

# Save outputs
gdf_new_sp.to_file(f'References/Output/Temp/OFC_NEW_{version}.shp')
gdf_span.to_file(f'References/Output/Temp/OFC_NEW_SPAN_{version}.shp')
logging.info("✅ Sequence assigned and saved with original index preserved.")
error_gdf.to_file(f"References/Output/Temp/error_{version}.shp")

# ╔══════════════════════════════════════════════════════════════╗
# ║                  WORK CREATING SPAN SEQUENCE                 ║
# ╚══════════════════════════════════════════════════════════════╝

# Load span-level geometry and segment-level geometry
gdf_span = gpd.read_file(f"References/Output/Temp/OFC_NEW_SPAN_{version}.shp")
gdf_segments = gpd.read_file(f"References/Output/Temp/OFC_NEW_{version}.shp")

# Ensure clean types
gdf_span['ring'] = gdf_span['ring'].astype(str)
gdf_span['span_name'] = gdf_span['span_name'].astype(str)
gdf_segments['span_name'] = gdf_segments['span_name'].astype(str)
gdf_segments['ring_no'] = gdf_segments['ring_no'].astype(str)

# Add span_seq column to segments if missing
if 'span_seq' not in gdf_segments.columns:
    gdf_segments['span_seq'] = None


# MAIN LOGIC — iterate over each ring
span_sequence_map = {}  # span_name -> sequence number
unique_rings = sorted(gdf_span['ring'].unique())

logging.info(f"🔄 Found {len(unique_rings)} rings: {unique_rings}")

for ring in unique_rings:
    logging.info(f"\n🔁 Processing ring: {ring}")

    # Filter span geometries by ring
    ring_df = gdf_span[gdf_span['ring'] == ring].copy()
    G = build_span_graph(ring_df)

    # Ask user for starting coordinate
    coord_str = rings[f'{ring}']
    try:
        x_str, y_str = coord_str.strip().split()
        start_coord = (float(x_str), float(y_str))
    except Exception as e:
        logging.error(f"❌ Invalid start point input: {e}")
        continue

    # Check if provided point matches any node
    start_point = Point(start_coord)

    # Find the closest node in G.nodes to the given start_coord
    closest_node = min(G.nodes, key=lambda node: Point(node).distance(start_point))

    # Optional: Warn if too far (e.g., more than 0.001 degrees)
    if Point(closest_node).distance(start_point) > 0.001:
        logging.warning(f"⚠️  Warning: Closest node {closest_node} is far from given start {start_coord}")
        continue  # skip this ring if distance too far

    # Traverse and assign span sequence
    ordered_indices = dfs_order(G, closest_node)

    for seq, idx in enumerate(ordered_indices, 1):
        span_name = ring_df.loc[idx, 'span_name']
        span_sequence_map[span_name] = seq
        gdf_span.loc[gdf_span['span_name'] == span_name, 'span_seq'] = seq
        gdf_segments.loc[gdf_segments['span_name'] == span_name, 'span_seq'] = seq

    logging.info(f"✅ Completed ring {ring} with {len(ordered_indices)} spans.")

# Save updated files
gdf_segments.to_file(f"References/Output/Final/OFC_New_{version}_Seg_Span_Seq.shp")
gdf_span.to_file(f"References/Output/Final/Spans_Geo_{version}.shp")
logging.info("✅ All rings processed. Span sequence updated and saved.")

