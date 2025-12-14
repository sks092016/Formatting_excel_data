import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, Point
import networkx as nx
import logging
import re

version = 1
def get_start_end_coords(geom):
    """
    Returns the start and end coordinates of a LineString or MultiLineString.
    For MultiLineString, considers the start of the first line and end of the last line.
    """
    try:
        if isinstance(geom, LineString):
            coords = list(geom.coords)
            return coords[0], coords[-1]

        elif isinstance(geom, MultiLineString):
            lines = list(geom.geoms)
            if not lines:
                raise ValueError("Empty MultiLineString.")
            start = list(lines[0].coords)[0]
            end = list(lines[-1].coords)[-1]
            logging.warning(f" ⚠️ The Geometry is multiline string starting at {start} & ending "
                            f"at {end}")
            return start, end

        else:
            raise TypeError(f"Unsupported geometry type: {type(geom)}")

    except Exception as e:
        logging.error(f"❌ Error in get_start_end_coords: {e}")
        return None, None

def build_span_graph(df):
    G = nx.DiGraph()
    for idx, row in df.iterrows():
        try:
            start, end = get_start_end_coords(row['geometry'])
            G.add_edge(start, end, index=idx)
        except:
            pass
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
