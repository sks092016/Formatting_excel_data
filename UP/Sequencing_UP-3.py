#!/usr/bin/env python3
"""
Standalone ring sequencing script using line geometry.

REQUIREMENTS:
    pip install geopandas shapely

WHAT THIS SCRIPT DOES:
    1. Loads POINTS and LINES shapefiles.
    2. For each ring:
         - Merge all line segments into a single LineString.
         - Re-orient merged line so that its start is closest to the FIRST start point.
         - Project all ring points onto the line.
         - Sort by line-distance → ensures TRUE along-line ordering.
         - Ensure clockwise: reverse if needed.
         - Points far from line (> tolerance) are assigned last.
         - Start points always get the earliest sequence numbers.
    3. Writes output shapefile with sequencing.

NO QGIS REQUIRED. PURE PYTHON.
"""

import geopandas as gpd
from shapely.ops import linemerge
from shapely.geometry import LineString, Point, MultiLineString
import shapely
import numpy as np

# ---------------------------------------------------------------------
# USER CONFIGURATION
# ---------------------------------------------------------------------

POINTS_FILE = "References/input/joints.shp"
LINES_FILE  = "References/input/ofc_rings.shp"
OUTPUT_FILE = "sequenced_output-4.shp"

# tolerance for distance (meters)
DIST_TOLERANCE = 8.0

# Start points definition:
# IMPORTANT: A ring may have MULTIPLE start points in CORRECT ORDER.
# FIRST start point determines line orientation & seq #1.
START_POINTS = {
    "R01": [(81.84352657, 27.34670577)],
    "R02": [(81.77924116, 27.31722292)],
    "R03": [(81.79454680, 27.35097636)],
    "R04": [(81.84863632,27.36655973)],
    "R05": [(81.88279909,27.39370129)],
    "R06": [(81.87146766,27.42758226)],
    "C05.1": [(81.93172211,27.48183326)],
    "C06.1": [(81.86725713,27.44332136)],
}
MULTI_LINE = {
    "R05": Point(81.90167876,27.36530648)
}

# Field names
RING_FIELD_POINTS = "ring_2"   # field in point layer
RING_FIELD_LINES  = "ring"     # field in line layer
SEQ_FIELD = "seq"

# ---------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------
def endpoint_distance(line: LineString, point: Point):
    """Compute minimum distance between line endpoints and a point."""
    p0, p1 = Point(line.coords[0]), Point(line.coords[-1])
    return min(p0.distance(point), p1.distance(point))


def reorder_and_merge_shapely(multiline: MultiLineString, guide_point):
    """
    multiline: Shapely MultiLineString
    guide_points: list of Shapely Points (2 or more)

    Returns: Ordered, direction-corrected LINESTRING
    """

    # Extract individual LineStrings
    parts = list(multiline.geoms)

    # 1. Sort parts based on proximity to guide points
    parts_sorted = sorted(
        parts,
        key=lambda seg: seg.distance(guide_point)
    )

    # 2. Start with the first segment
    d1 = Point(parts_sorted[0].coords[0]).distance(guide_point)
    d2 = Point(parts_sorted[0].coords[-1]).distance(guide_point)

    if d1 < d2 :
        parts_sorted[0] = parts_sorted[0].coords[::-1]

    final_coords = list(LineString(parts_sorted[0]).coords)
    last_point = Point(final_coords[-1])

    # 3. For each next segment, connect intelligently
    for seg in parts_sorted[1:]:
        start_pt = Point(seg.coords[0])
        end_pt = Point(seg.coords[-1])

        # Compare distances to determine correct direction
        d_start = last_point.distance(start_pt)
        d_end = last_point.distance(end_pt)

        if d_end < d_start:
            seg = LineString(seg.coords[::-1])  # reverse

        # Merge coordinates, avoiding duplication
        final_coords.extend(seg.coords[1:])
        last_point = Point(final_coords[-1])

    # Return as LINESTRING
    return LineString(final_coords)

def merge_lines_geoms(geoms, ring_id):
    """Safely merge multiple LineStrings or MultiLineStrings into a single LineString."""
    merged = linemerge(list(geoms))

    # If merged gives MultiLineString (disconnected), choose the longest
    if isinstance(merged, shapely.geometry.MultiLineString):
        merged = reorder_and_merge_shapely(merged,MULTI_LINE[ring_id])
    return merged


def orient_line_by_startpoint(line, start_points):
    """Reverse line if needed so that its start is closest to first start point."""
    if not start_points:
        return line

    sp = Point(start_points[0])

    d1 = sp.distance(Point(line.coords[0]))
    print(Point(line.coords[0]))
    d2 = sp.distance(Point(line.coords[-1]))
    print(Point(line.coords[-1]))
    print(d1, d2)
    if d2 < d1:
        # Reverse line
        return LineString(list(line.coords)[::-1])
    return line


def angle_of_linestring(line):
    """Determine if line is clockwise or anticlockwise by signed area of dense sampling."""
    coords = np.array([line.interpolate(d).coords[0] for d in np.linspace(0, line.length, 200)])
    x = coords[:, 0]
    y = coords[:, 1]
    area = 0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])
    return "CW" if area < 0 else "CCW"


def force_clockwise(line):
    """Re-orient line so that the traversal direction is clockwise."""
    if angle_of_linestring(line) == "CW":
        return line
    return LineString(list(line.coords)[::-1])


# ---------------------------------------------------------------------
# MAIN SEQUENCING LOGIC
# ---------------------------------------------------------------------

def sequence_ring(points_gdf, lines_gdf, ring_id):
    """Sequence all points of one ring."""

    pts = points_gdf[points_gdf[RING_FIELD_POINTS] == ring_id].copy()
    if pts.empty:
        return pts

    ls = lines_gdf[lines_gdf[RING_FIELD_LINES] == ring_id]
    if ls.empty:
        print(f"WARNING: No line geometry found for ring {ring_id}. Skipping.")
        return pts

    # 1. Merge line segments
    merged_line = merge_lines_geoms(ls.geometry,ring_id)
    # 2. Re-orient toward FIRST start point
    start_pts = START_POINTS.get(ring_id, [])
    merged_line = orient_line_by_startpoint(merged_line, start_pts)

    # 3. Force clockwise direction
    # merged_line = force_clockwise(merged_line)

    # 4. Compute projections
    projections = []
    far_points = []

    for idx, row in pts.iterrows():
        p = row.geometry

        # Nearest point on line
        proj_dist = merged_line.project(p)
        p_on_line = merged_line.interpolate(proj_dist)
        off_dist  = p.distance(p_on_line)

        if off_dist > DIST_TOLERANCE:
            # Save separately — sorted later
            far_points.append((idx, proj_dist, off_dist))
        else:
            projections.append((idx, proj_dist, row.OBJECTID))

    # 5. Sort near-line points by projected distance
    projections.sort(key=lambda x: x[1])
    print(projections)
    # 6. Sort far points by projected distance (but appended last)
    far_points.sort(key=lambda x: x[1])

    # 7. Handle multiple start points (ordered)
    ordered_ids = []

    if start_pts:
        # Compute which actual point matches each start point best
        start_point_objs = [Point(sp) for sp in start_pts]

        for sp in start_point_objs:
            closest_idx = min(pts.index, key=lambda i: pts.loc[i].geometry.distance(sp))
            if closest_idx in [x for x, _, _ in projections]:  # must be a near-line point
                if closest_idx not in ordered_ids:
                    ordered_ids.append(closest_idx)

        start_pos = [x[0] for x in projections].index(closest_idx)
        projections = projections[start_pos:] + projections[:start_pos]

    # 8. Assign sequence
    seq_num = 1

    for idx, dist, _ in projections:
        pts.at[idx, SEQ_FIELD] = seq_num
        seq_num += 1

    # 9. Add far points LAST
    for idx, dist, off in far_points:
        pts.at[idx, SEQ_FIELD] = seq_num
        seq_num += 1

    return pts


# ---------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------

def main():
    print("Loading data...")

    pts = gpd.read_file(POINTS_FILE)
    ls  = gpd.read_file(LINES_FILE)

    # ensure seq field exists
    if SEQ_FIELD not in pts.columns:
        pts[SEQ_FIELD] = None

    # output
    out = []

    # unique rings
    rings = sorted(pts[RING_FIELD_POINTS].dropna().unique())

    for r in rings:
        print(f"\nProcessing ring {r} ...")
        res = sequence_ring(pts, ls, r)
        out.append(res)

    final = gpd.GeoDataFrame(pd.concat(out), crs=pts.crs)

    print("\nSaving output:", OUTPUT_FILE)
    final.to_file(OUTPUT_FILE)
    print("Done.")

# ----------------------------------------------------------

if __name__ == "__main__":
    import pandas as pd
    main()
