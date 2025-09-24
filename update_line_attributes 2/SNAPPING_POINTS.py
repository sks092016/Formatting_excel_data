import geopandas as gpd
from shapely.geometry import LineString, Point
import numpy as np

# === Parameters ===
tolerance = 0.5  # snapping distance in map units (adjust as needed)

# Load your shapefile
gdf = gpd.read_file("INPUT/OFC_SURVEY.shp")

# Function to get endpoints of a LineString
def get_endpoints(line):
    coords = list(line.coords)
    return Point(coords[0]), Point(coords[-1])

# For each RING_NO group, snap lines
new_geoms = []
for ring, group in gdf.groupby("ring_no"):
    used_points = set()
    lines = list(group.geometry)

    # Convert all endpoints to a pool
    endpoints = []
    for i, line in enumerate(lines):
        p1, p2 = get_endpoints(line)
        endpoints.append((i, 0, p1))  # (line index, end=0 for start, point)
        endpoints.append((i, 1, p2))  # (line index, end=1 for end, point)

    # Try snapping
    for idx, end_flag, point in endpoints:
        if (idx, end_flag) in used_points:
            continue  # already snapped

        # Find nearest available endpoint within tolerance
        min_dist = float("inf")
        nearest = None
        for j, other_flag, other_point in endpoints:
            if (j, other_flag) in used_points or (j == idx):
                continue
            dist = point.distance(other_point)
            if dist < min_dist and dist <= tolerance:
                min_dist = dist
                nearest = (j, other_flag, other_point)

        # If found, snap them
        if nearest:
            j, other_flag, other_point = nearest
            # Modify coordinates
            coords = list(lines[idx].coords)
            coords_other = list(lines[j].coords)

            if end_flag == 0:
                coords[0] = (other_point.x, other_point.y)
            else:
                coords[-1] = (other_point.x, other_point.y)

            if other_flag == 0:
                coords_other[0] = (point.x, point.y)
            else:
                coords_other[-1] = (point.x, point.y)

            # Update lines
            lines[idx] = LineString(coords)
            lines[j] = LineString(coords_other)

            # Mark endpoints as used
            used_points.add((idx, end_flag))
            used_points.add((j, other_flag))

    new_geoms.extend(lines)

# Replace geometry
gdf["geometry"] = new_geoms

# Save output
gdf.to_file("OUTPUT/snapped_output.shp")
