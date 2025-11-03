#!/usr/bin/env python3
"""
process_existing_segments_v2.py

Processes an input LineString shapefile grouped by span_name and ordered by seg_seq.
For segments where 'scope' contains 'existing data' (case-insensitive):
 - Combines consecutive segments whose endpoints match exactly.
 - Extracts start and end coordinates for each combined group.
 - Appends unique (x,y) coordinates to a JSON array (creating file if needed).
 - Writes a shapefile of the resulting unique points (EPSG:4326).

Usage:
    python process_existing_segments_v2.py input.shp output_points.shp output.json

Expected fields in input shapefile:
    - span_name  (string)
    - seg_seq    (integer / numeric order)
    - scope      (string containing "existing data")

All output coordinates and shapefile CRS are EPSG:4326.
"""

import sys
import os
import json
import geopandas as gpd
from shapely.geometry import LineString, Point

# Parameters
SCOPE_KEYWORD = "existing scope"
OUTPUT_CRS = "EPSG:4326"
LABEL = "Brown Field Conn"
TYPE = "Brown Field"

# -------------------- Helper functions --------------------
def to_epsg4326(gdf):
    """Ensure GeoDataFrame is in EPSG:4326 CRS."""
    if gdf.crs is None:
        raise ValueError("Input shapefile must have a valid CRS.")
    if gdf.crs.to_string() != OUTPUT_CRS:
        return gdf.to_crs(OUTPUT_CRS)
    return gdf.copy()

def get_start_end(line):
    """Return start and end coordinates (lon, lat) of a LineString."""
    coords = list(line.coords)
    return coords[0], coords[-1]

def merge_consecutive_segments(lines):
    """Merge consecutive LineStrings whose endpoints match exactly."""
    if not lines:
        return []
    merged_groups = []
    current_group = [lines[0]]
    prev_end = get_start_end(lines[0])[1]
    for line in lines[1:]:
        start, end = get_start_end(line)
        if start == prev_end:
            # continuous
            current_group.append(line)
        else:
            # break in continuity, finalize current
            merged_groups.append(LineString([pt for seg in current_group for pt in seg.coords]))
            current_group = [line]
        prev_end = end
    # finalize last group
    if current_group:
        merged_groups.append(LineString([pt for seg in current_group for pt in seg.coords]))
    return merged_groups

# -------------------- Core processing --------------------

def process_shapefile(input_shp, output_points_shp, output_json_path):
    if not os.path.exists(input_shp):
        raise FileNotFoundError(f"Input shapefile not found: {input_shp}")
    gdf = gpd.read_file(input_shp)
    if gdf.empty:
        raise ValueError("Input shapefile is empty.")
    for f in ["span_name", "seg_seq", "scope"]:
        if f not in gdf.columns:
            raise ValueError(f"Missing required field '{f}' in input shapefile.")
    gdf = to_epsg4326(gdf)
    # Prepare JSON file
    if os.path.exists(output_json_path):
        try:
            with open(output_json_path, "r", encoding="utf-8") as jf:
                existing_data = json.load(jf)
                if not isinstance(existing_data, list):
                    print("Warning: JSON file not an array. Starting fresh.")
                    existing_data = []
        except Exception:
            existing_data = []
    else:
        existing_data = []
    existing_coords = {(float(e["x"]), float(e["y"])) for e in existing_data if "x" in e and "y" in e}
    new_entries = []
    new_points = []
    # Group by span_name
    for span, span_df in gdf.groupby("span_name"):
        # Filter only "existing data" scopes
        sub = span_df[span_df["scope"].str.lower().str.contains(SCOPE_KEYWORD)]
        if sub.empty:
            continue
        # Sort by seg_seq
        sub = sub.sort_values(by="seg_seq")
        # Merge consecutive segments with exact endpoint match
        merged_lines = merge_consecutive_segments(list(sub.geometry))
        # Extract start and end points from each merged group
        for merged in merged_lines:
            start, end = get_start_end(merged)
            for (lon, lat) in [start, end]:
                key = (float(lon), float(lat))
                if key not in existing_coords:
                    existing_coords.add(key)
                    entry = {
                        "x": lon,
                        "y": lat,
                        "crs": OUTPUT_CRS,
                        "label": LABEL,
                        "type": TYPE,
                        "span": span
                    }
                    new_entries.append(entry)
                    new_points.append(Point(lon, lat))
    # Append new entries to JSON array
    combined = existing_data + new_entries
    with open(output_json_path, "w", encoding="utf-8") as jf:
        json.dump(combined, jf, ensure_ascii=False, indent=2)
    print(f"Appended {len(new_entries)} new unique coordinates to {output_json_path}")
    # Write shapefile for new unique points only
    if new_points:
        out_gdf = gpd.GeoDataFrame({
            "label": [LABEL]*len(new_points),
            "type": [TYPE]*len(new_points),
            "span": [e["span"] for e in new_entries]
        }, geometry=new_points, crs=OUTPUT_CRS)
        out_gdf.to_file(output_points_shp)
        print(f"Saved {len(new_points)} unique endpoint points to {output_points_shp}")
    else:
        print("No new unique endpoints found. Shapefile not updated.")
    return len(new_entries)

if __name__ == "__main__":
    block_name = 'Khurai'
    input_shp = f'input/OFC_New_{block_name}-1_Seg_Span_Seq.shp'
    output_points_shp = f"temp/brown_field_manholes_{block_name}.shp"
    output_json = f"temp/sharp_turn_points_{block_name}.json"
    process_shapefile(input_shp, output_points_shp, output_json)
