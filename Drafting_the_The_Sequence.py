# Full corrected script based on your original logic with the first-segment-reversal fix included

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
from shapely.geometry import Point
import networkx as nx

############################ Reversing the Geometry and Filling up the sequence in Segments ################################
# ╔══════════════════════════════════════════════════════════════╗
# ║   WORK CREATING SEGMENT SEQUENCE & reversing Geometry        ║
# ╚══════════════════════════════════════════════════════════════╝

version = "1.0"

# Load the input shapefile
gdf = gpd.read_file('References/BHIND OFC/BHIND OFC.shp')

# Create empty GeoDataFrames with correct structures
gdf_new_sp = gdf.iloc[0:0].copy()
gdf_new_sp["seg_seq"] = None

gdf_span = gpd.GeoDataFrame(columns=['span_name', 'ring', 'start_cord', 'end_cord', 'span_seq', 'geometry'], geometry='geometry')

# Helper function
def get_start_end_coords(line):
    coords = list(line.coords)
    return coords[0], coords[-1]

def merged_line_geometry(lines):
    merged_coords = []
    for line in lines:
        coords = list(line.coords)
        if not merged_coords:
            merged_coords.extend(coords)
        else:
            merged_coords.extend(coords[1:])
    return LineString(merged_coords)

# Process each span
span_list = gdf.sort_values('span_name').span_name.unique()
for s in span_list:
    temp_df = gdf[gdf.span_name == s].sort_values('Sequqnce').copy()
    temp_df['start'] = temp_df.geometry.apply(lambda geom: get_start_end_coords(geom)[0])
    temp_df['end'] = temp_df.geometry.apply(lambda geom: get_start_end_coords(geom)[1])

    sorted_indices = []
    remaining = temp_df.copy()

    # === STEP 1: Handle possibly reversed first segment ===
    current_idx = remaining.index[0]
    current = remaining.loc[current_idx]
    current_start, current_end = current['start'], current['end']

    # Check if current start is not a true start (i.e., other segments connect to it)
    connected_to_start = remaining[
        ((remaining['start'] == current_start) | (remaining['end'] == current_start)) &
        (remaining.index != current_idx)
    ]

    if not connected_to_start.empty:
        # Reverse the first segment
        flipped_geom = LineString(list(current['geometry'].coords)[::-1])
        temp_df.at[current_idx, 'geometry'] = flipped_geom
        current = temp_df.loc[current_idx]
        current['start'], current['end'] = get_start_end_coords(flipped_geom)

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
            print(f"Warning: Disconnected segment remains in span '{s}'.")
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
gdf_new_sp.to_file(f'References/Output/OFC_NEW_{version}.shp')
gdf_span.to_file(f'References/Output/OFC_NEW_SPAN_{version}.shp')
print("✅ Sequence assigned and saved with original index preserved.")


# ╔══════════════════════════════════════════════════════════════╗
# ║                  WORK CREATING SPAN SEQUENCE                 ║
# ╚══════════════════════════════════════════════════════════════╝

# Load span-level geometry and segment-level geometry
gdf_span = gpd.read_file(f"References/Output/OFC_NEW_SPAN_{version}.shp")
gdf_segments = gpd.read_file(f"References/Output/OFC_NEW_{version}.shp")

# Ensure clean types
gdf_span['ring'] = gdf_span['ring'].astype(str)
gdf_span['span_name'] = gdf_span['span_name'].astype(str)
gdf_segments['span_name'] = gdf_segments['span_name'].astype(str)
gdf_segments['ring_no'] = gdf_segments['ring_no'].astype(str)

# Add span_seq column to segments if missing
if 'span_seq' not in gdf_segments.columns:
    gdf_segments['span_seq'] = None

# Helper functions
def get_start_end_coords(line):
    coords = list(line.coords)
    return coords[0], coords[-1]

def build_span_graph(df):
    G = nx.DiGraph()
    for idx, row in df.iterrows():
        start, end = get_start_end_coords(row['geometry'])
        G.add_edge(start, end, index=idx)
    return G

def dfs_order(G, start_node):
    visited = set()
    span_indices = []

    def dfs(node):
        for _, neighbor, data in G.out_edges(node, data=True):
            idx = data['index']
            if idx not in visited:
                visited.add(idx)
                span_indices.append(idx)
                dfs(neighbor)

    dfs(start_node)
    return span_indices

### Import start points
from ring_start_point_cordinates import rings


# MAIN LOGIC — iterate over each ring
span_sequence_map = {}  # span_name -> sequence number
unique_rings = sorted(gdf_span['ring'].unique())

print(f"🔄 Found {len(unique_rings)} rings: {unique_rings}")

for ring in unique_rings:
    print(f"\n🔁 Processing ring: {ring}")

    # Filter span geometries by ring
    ring_df = gdf_span[gdf_span['ring'] == ring].copy()
    G = build_span_graph(ring_df)

    # Ask user for starting coordinate
    coord_str = rings[f'{ring}']
    try:
        x_str, y_str = coord_str.strip().split()
        start_coord = (float(x_str), float(y_str))
    except Exception as e:
        print(f"❌ Invalid input: {e}")
        continue

    # Check if provided point matches any node
    if start_coord not in G.nodes:
        print(f"❌ Start coordinate {start_coord} not found in this ring's geometry.")
        continue

    # Traverse and assign span sequence
    ordered_indices = dfs_order(G, start_coord)

    for seq, idx in enumerate(ordered_indices, 1):
        span_name = ring_df.loc[idx, 'span_name']
        span_sequence_map[span_name] = seq
        gdf_span.loc[gdf_span['span_name'] == span_name, 'span_seq'] = seq
        gdf_segments.loc[gdf_segments['span_name'] == span_name, 'span_seq'] = seq

    print(f"✅ Completed ring {ring} with {len(ordered_indices)} spans.")

# Save updated files
gdf_segments.to_file(f"References/Output/OFC_NEW_{version}_with_spanseq.shp")
gdf_span.to_file(f"References/Output/OFC_NEW_SPAN_{version}_with_seq.shp")

"✅ All rings processed. Span sequence updated and saved."

