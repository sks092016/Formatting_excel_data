#!/usr/bin/env python3
"""
Standalone sequencing script (NO QGIS REQUIRED)

- Reads point shapefile (points having ring_2 field)
- Reads line shapefile (line segments having ring field)
- For each ring:
    * Merge all line segments into a single polyline
    * If merge produces MultiLineString, pick the LONGEST branch
    * Project each point onto this line
    * Sort points by line-measured distance
    * Assign sequence numbers 1..N

Author: ChatGPT
"""

import geopandas as gpd
from shapely.ops import linemerge
from shapely.geometry import MultiLineString, LineString
import os


# ----------------------------------------------------------
# USER SETTINGS
# ----------------------------------------------------------

POINTS_FP = "References/input/joints.shp"          # your point file
LINES_FP  = "References/input/ofc_rings.shp"          # your line file

POINT_RING_FIELD = "ring_2"       # ring field in point layer
LINE_RING_FIELD  = "ring"         # ring field in line layer

SEQ_FIELD = "seq"                 # output field name
OUT_FP = os.path.splitext(POINTS_FP)[0] + "_sequenced.shp"


# ----------------------------------------------------------
# MERGE LINES :::::::::::::::::::::::::::::::::::::::::::::::
# ----------------------------------------------------------

def merge_lines(line_geoms):
    """
    Merge list of LineStrings into one continuous LineString.
    If result is MultiLineString, pick the LONGEST component.
    """
    merged = linemerge(line_geoms)

    # If we get MultiLineString, choose longest line as ring centerline
    # if isinstance(merged, MultiLineString):
    #     longest = max(list(merged), key=lambda ln: ln.length)
    #     return longest
    #
    # # Already a single LineString
    # if isinstance(merged, LineString):
    #     return merged
    return merged
    raise ValueError("merge_lines(): unexpected geometry type: " + str(type(merged)))


# ----------------------------------------------------------
# MAIN PROCESS
# ----------------------------------------------------------

def main():

    print("\nLoading data…")

    pts = gpd.read_file(POINTS_FP)
    lines = gpd.read_file(LINES_FP)

    print(f"Loaded {len(pts)} points")
    print(f"Loaded {len(lines)} lines")

    # Create seq field
    if SEQ_FIELD not in pts.columns:
        pts[SEQ_FIELD] = None

    # Unique rings
    rings = sorted(pts[POINT_RING_FIELD].dropna().unique())

    print(f"\nRings found in point layer: {rings}")

    for ring in rings:
        print(f"\n--- Processing ring {ring} ---")

        # Get line subset for this ring
        line_subset = lines[lines[LINE_RING_FIELD] == ring]

        if line_subset.empty:
            print(f"!! WARNING: No line geometry found for ring {ring} – skipping")
            continue

        # Merge all line segments for the ring
        merged_line = merge_lines(list(line_subset.geometry))

        # Get points of this ring
        pts_subset_idx = pts[pts[POINT_RING_FIELD] == ring].index
        if len(pts_subset_idx) == 0:
            print(f"!! WARNING: No points for ring {ring} – skipping")
            continue

        # Project points onto the merged line and measure distance
        distances = []
        for idx in pts_subset_idx:
            p = pts.loc[idx].geometry
            d = merged_line.project(p)

            distances.append((idx, d))

        # Sort the index list by distance
        distances.sort(key=lambda t: t[1])

        # Assign sequence numbers
        seq = 1
        for idx, dist in distances:
            pts.at[idx, SEQ_FIELD] = seq
            seq += 1

        print(f"Assigned {seq-1} sequence numbers for ring {ring}")

    print("\nSaving output…")
    pts.to_file(OUT_FP)
    print(f"Done! Output written to: {OUT_FP}")


# ----------------------------------------------------------

if __name__ == "__main__":
    main()
