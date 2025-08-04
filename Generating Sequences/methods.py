import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, Point
import networkx as nx
import logging
import re
def ensure_epsg4326(input_file, output_file=None):
    """
    Check CRS of a shapefile and reproject to EPSG:4326 if needed.

    Parameters
    ----------
    input_file : str
        Path to the input shapefile.
    output_file : str, optional
        Path for the output shapefile. If None, overwrites input.
    """
    gdf = gpd.read_file(input_file)

    # If CRS is missing, raise an error
    if gdf.crs is None:
        raise ValueError("❌ The shapefile has no CRS defined. Please set it manually.")

    # If already in EPSG:4326, no change
    if gdf.crs.to_epsg() == 4326:
        print("✅ CRS is already EPSG:4326, no reprojection needed.")
        return gdf

    # Otherwise reproject
    print(f"ℹ️ Reprojecting from {gdf.crs} → EPSG:4326")
    gdf = gdf.to_crs(epsg=4326)

    # Save output
    if output_file is None:
        output_file = input_file  # overwrite original
    gdf.to_file(output_file)

    print(f"✅ Saved reprojected file to {output_file}")
    return gdf


def smart_split(s):
    if " TO " in s.upper():  # case-insensitive
        return s.upper().split(" TO ")[0].strip()
    elif "-" in s:
        return s.split("-")[0].strip()
    elif " " in s:
        return s.split(" ")[0].strip()
    else:
        return s.strip()

def coords_match(c1, c2, tol):
    """Check if two coordinates are within tolerance (in CRS units)."""
    return Point(c1).distance(Point(c2)) <= tol

def get_coords(geom):
    try:
        return (geom.x, geom.y)
    except:
        return None

def merged_line_geometry(lines):
    merged_coords = []
    for line in lines:
        try:
            coords = list(line.coords)
            if not merged_coords:
                merged_coords.extend(coords)
            else:
                merged_coords.extend(coords[1:])
        except:
            continue
    return LineString(merged_coords)

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
def smart_split2(s):
    if " TO " in s.upper():  # case-insensitive
        return s.upper().split(" TO ")
    elif "-" in s:
        return s.split("-")
    elif " " in s:
        return s.split(" ")
    else:
        return s.strip()
def clean_name(name: str) -> str:
    # Remove extra spaces, uppercase everything
    s = name.strip().upper()
    # Replace multiple separators (-, _, space) with a single space
    s = re.sub(r"[-_\s]+", " ", s)
    # If it's a version of T POINT, drop it
    if s.startswith("T POINT"):
        s = s.replace("T POINT", "", 1).strip()
    return s

def check_gp_consistency(spans, gps):
    span_gps = set()
    for s in spans:
        parts = smart_split2(s)
        for p in parts:
            cleaned = clean_name(p)
            if cleaned:  # only add non-empty names
                span_gps.add(cleaned.strip().upper())

    gp_set = set(g.upper() for g in gps)
    return {
        "extra_in_spans": span_gps - gp_set,
        "unused_gps": gp_set - span_gps
    }

def checking_repetions(counter):
    repeats = [(name , count) for name, count in counter.items() if count > 1]
    if len(repeats) == 0:
        print("List is unique")
        return None
    else:
        return repeats
