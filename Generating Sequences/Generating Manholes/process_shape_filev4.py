#!/usr/bin/env python3
"""
process_shapefile_v4.py

Upgraded from process_shapefile_v3.py:
 - Configurable offsets for crossing start/end points (so they are not placed exactly at the segment start/end).
 - Configurable small-offset used for placing other feature points.
 - Configurable crossing types to include (list).
 - Place points at both ends of crossings with an offset (per crossing types list).
 - Insert distance points every `distance_interval` meters between feature anchors.
 - Sequential cleaning pass to remove points too close (min_buffer) with prioritized deletion:
     * Always keep the absolute first point in the overall sequence.
     * When crossing start/end conflicts with distance-point -> delete crossing endpoint (start or end as appropriate).
     * Between end of one crossing and start of another crossing -> delete both (unless one is the absolute first point).
     * For small crossings (length < small_crossing_thresh) when the crossing produces both start & end points,
       choose the one farther from the previous retained point.
 - Manual points can be read from a JSON file; they are integrated and cleaned the same as other points.
 - Lots of comments and usage examples at the bottom.

Author: Upgraded by ChatGPT (based on user's v3 script)
"""

import geopandas as gpd
from shapely.geometry import Point, LineString
from pyproj import Geod, CRS, Transformer
import re
import math
import json
import matplotlib.pyplot as plt
import warnings
from collections import defaultdict
from typing import List, Optional
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

# -------------------- Utility --------------------

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split("([0-9]+)", str(s))]

def ordered_merge(lines: List[LineString]) -> LineString:
    """Merge LineStrings in the given order, preserving direction (best-effort)."""
    merged_coords = []
    for i, line in enumerate(lines):
        coords = list(line.coords)
        if i == 0:
            merged_coords.extend(coords)
        else:
            if coords[0] == merged_coords[-1]:
                merged_coords.extend(coords[1:])
            elif coords[-1] == merged_coords[-1]:
                merged_coords.extend(coords[-2::-1])
            else:
                # Not connected in expected way: append anyway (keeps order)
                merged_coords.extend(coords)
    return LineString(merged_coords)

# -------------------- Geodesic helpers --------------------

geod = Geod(ellps="WGS84")

def segment_lengths_and_cumulatives(coords, is_projected):
    seg_lens = []
    cumul = [0.0]
    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]):
        if is_projected:
            d = math.hypot(x2 - x1, y2 - y1)
        else:
            _, _, d = geod.inv(x1, y1, x2, y2)
        seg_lens.append(d)
        cumul.append(cumul[-1] + d)
    return seg_lens, cumul

def total_length_from_cumulatives(cumul):
    return cumul[-1] if cumul else 0.0

def point_at_distance_along_line(line: LineString, distance_m: float, is_projected: bool) -> Point:
    """
    Return a shapely Point located distance_m meters along 'line'.
    For projected CRSes it uses shapely.interpolate; for geographic uses geodesic interpolation.
    """
    if is_projected:
        # shapely interpolate uses the line length in same units as coordinates
        return line.interpolate(min(distance_m, line.length))
    else:
        coords = list(line.coords)
        cum = 0.0
        for (lon1, lat1), (lon2, lat2) in zip(coords[:-1], coords[1:]):
            az12, az21, seglen = geod.inv(lon1, lat1, lon2, lat2)
            if cum + seglen >= distance_m:
                remaining = distance_m - cum
                lon, lat, _ = geod.fwd(lon1, lat1, az12, remaining)
                return Point(lon, lat)
            cum += seglen
        x, y = coords[-1]
        return Point(x, y)

# -------------------- Main processing --------------------

def process_shapefile(
    input_path: str,
    span_filter: Optional[str] = None,
    # Configurable parameters (defaults per your request)
    crossing_offset: float = 50.0,           # distance from crossing start/end for *major* crossings like road-cross
    feature_endpoint_offset: float = 10.0,   # small offset used when placing feature endpoints (per 2.a)
    crossing_types: Optional[List[str]] = None,  # list of values (case-insensitive) in the input field to treat as crossings
    crossing_field: str = "crossing_t",      # field in input with crossing type (fallback to 'feature_type')
    distance_interval: float = 1800.0,       # spacing of distance points (2.b)
    min_buffer: float = 150.0,               # minimum allowed distance between any two points (2.c)
    small_crossing_thresh: float = 150.0,    # small crossing length threshold (meters)
    manual_points_json: Optional[str] = None # path to JSON with manual points to add
):
    """
    Process segments shapefile and return GeoDataFrame of points + the merged main line.

    Manual points JSON format (list of entries):
    [
       {"x": 77.1, "y": 28.6, "crs": "EPSG:4326", "label": "Manual_A", "type":"manual"},
       {"x": 500000.0, "y": 3000000.0, "crs": "EPSG:32643", "label": "Manual_B", "type":"manual"}
    ]
    If `crs` omitted, coordinates are assumed to be in input shapefile CRS.

    crossing_types: if None -> default to ["road cross", "bridge", "railway", "rail_cross", ...] (typical variants).
    """

    gdf = gpd.read_file(input_path)
    if gdf.empty:
        raise ValueError("Input shapefile is empty or unreadable.")

    # Filter span_name if requested
    if span_filter is not None:
        if "span_name" not in gdf.columns:
            raise ValueError("Input shapefile lacks 'span_name' field required for filtering.")
        gdf = gdf[gdf["span_name"] == span_filter]
    if gdf.empty:
        raise ValueError(f"No records found for span_name '{span_filter}'")

    # Sorting segments in their sequence order
    if "seg_seq" not in gdf.columns:
        raise ValueError("Input shapefile must have 'seg_seq' field.")
    gdf["sort_key"] = gdf["seg_seq"].apply(natural_sort_key)
    gdf = gdf.sort_values(by="sort_key").reset_index(drop=True)

    # Ordered merge into main_line
    lines = list(gdf.geometry)
    main_line = ordered_merge(lines)
    coords = list(main_line.coords)

    # Determine CRS type
    crs = gdf.crs
    if crs is None:
        raise ValueError("Input shapefile has no CRS. Provide a valid CRS.")

    is_projected = not crs.is_geographic  # geographic indicates degrees
    # compute segment lengths and cumulative distances for merged line
    seg_lens, cumul = segment_lengths_and_cumulatives(coords, is_projected)
    total_len = total_length_from_cumulatives(cumul)

    print(f"CRS: {crs.to_string()} | Projected: {is_projected} | Total length (m): {total_len:.3f}")

    # Default crossing_types if not provided
    if crossing_types is None:
        crossing_types = ["road cross", "road_cross", "roadcross", "roadcrossing", "bridge", "railway", "rail_cross", "rail crossing"]

    # Normalize crossing types to lower-case for comparison
    crossing_types = [t.strip().lower() for t in crossing_types]

    # ----------------- Place feature points (2.a) -----------------
    # We'll create a list of dicts representing feature anchors along the merged line:
    # { 'dist': float, 'label': str, 'ptype': 'first|cross_start|cross_end|bridge_before|bridge_after|manual|span_end|distance', 'meta': {...} }
    feature_points = []

    # include small initial First_Point at feature_endpoint_offset (or 10m earlier behaviour)
    first_pt_dist = min(feature_endpoint_offset, total_len)
    feature_points.append({'dist': first_pt_dist, 'label': 'First_Point', 'ptype': 'first', 'meta': {'reason': 'StartOffset'}})

    # We'll iterate through ordered original segments to compute their start/end distances along merged_line.
    current_pos = 0.0
    crossing_counter = 0
    bridge_counter = 0
    eps = 1e-3

    for idx, row in gdf.iterrows():
        seg_geom: LineString = row.geometry
        seg_coords = list(seg_geom.coords)

        # compute length of this segment (projected or geodesic)
        seg_length = 0.0
        if is_projected:
            for (x1, y1), (x2, y2) in zip(seg_coords[:-1], seg_coords[1:]):
                seg_length += math.hypot(x2 - x1, y2 - y1)
        else:
            for (lon1, lat1), (lon2, lat2) in zip(seg_coords[:-1], seg_coords[1:]):
                _, _, d = geod.inv(lon1, lat1, lon2, lat2)
                seg_length += d

        start_dist = current_pos
        end_dist = current_pos + seg_length

        # determine crossing/feature type for this segment
        ctype = None
        if crossing_field in gdf.columns:
            ctype = row.get(crossing_field, None)
        elif "feature_type" in gdf.columns:
            ctype = row.get("feature_type", None)

        ctype_clean = None
        if isinstance(ctype, str):
            ctype_clean = ctype.strip().lower()

        # If this segment matches one of the crossing_types, place points at both ends offset inward by feature_endpoint_offset
        if ctype_clean in crossing_types:
            crossing_counter += 1
            # compute offsets clipped to inside the segment
            # start_offset_point = start_dist + feature_endpoint_offset
            # end_offset_point = end_dist - feature_endpoint_offset
            # start_offset = min(max(start_dist + feature_endpoint_offset, start_dist), end_dist)
            # end_offset = max(min(end_dist - feature_endpoint_offset, end_dist), start_dist)
            start_offset = max(0.0, start_dist - crossing_offset)
            end_offset = min(total_len, end_dist + crossing_offset)

            label_s = f"Cross_{crossing_counter}_Start"
            label_e = f"Cross_{crossing_counter}_End"
            feature_points.append({'dist': start_offset, 'label': label_s, 'ptype': 'cross_start',
                                   'meta': {'seg_index': idx, 'crossing_id': crossing_counter, 'seg_length': seg_length}})
            feature_points.append({'dist': end_offset, 'label': label_e, 'ptype': 'cross_end',
                                   'meta': {'seg_index': idx, 'crossing_id': crossing_counter, 'seg_length': seg_length}})

        # Additionally handle explicit "bridge" handling (with crossing_offset behavior if segment is a bridge)
        if ctype_clean == "bridge":
            # For larger bridges, we want to add before/after points relative to the segment's extent.
            # We'll use crossing_offset for before/after placement, clipped.
            bridge_counter += 1
            if seg_length > small_crossing_thresh:
                before_d = max(0.0, start_dist - crossing_offset)
                after_d = min(total_len, end_dist + crossing_offset)
                # label these as Bridge_before/after
                feature_points.append({'dist': before_d, 'label': f"Bridge_{bridge_counter}_Before", 'ptype': 'bridge_before',
                                       'meta': {'seg_index': idx, 'crossing_id': f"bridge_{bridge_counter}", 'seg_length': seg_length}})
                feature_points.append({'dist': after_d, 'label': f"Bridge_{bridge_counter}_After", 'ptype': 'bridge_after',
                                       'meta': {'seg_index': idx, 'crossing_id': f"bridge_{bridge_counter}", 'seg_length': seg_length}})
            else:
                # small bridge -> single anchor (choose one farther from previous feature)
                prev_dist = feature_points[-1]['dist'] if feature_points else 0.0
                dstart = abs(start_dist - prev_dist)
                dend = abs(end_dist - prev_dist)
                chosen = start_dist if dstart > dend else end_dist
                feature_points.append({'dist': chosen, 'label': f"Bridge_{bridge_counter}", 'ptype': 'bridge_single',
                                       'meta': {'seg_index': idx, 'crossing_id': f"bridge_{bridge_counter}", 'seg_length': seg_length}})

        current_pos = end_dist

    # Add virtual Span_End anchor for gap filling
    feature_points.append({'dist': total_len, 'label': 'Span_End', 'ptype': 'span_end', 'meta': {}})

    # ----------------- Integrate manual points (additional feature) -----------------
    # manual_points_json should be a path to a JSON file containing list entries with x,y, optional crs and label
    manual_points = []
    if manual_points_json:
        with open(manual_points_json, 'r') as fh:
            data = json.load(fh)
        # Determine coordinate transformation if manual point has different crs than input gdf
        input_crs = crs
        for entry in data:
            x = entry.get('x')
            y = entry.get('y')
            lbl = entry.get('label', 'Manual_Point')
            entry_crs = entry.get('crs', None)
            if entry_crs is None:
                # assume input shapefile CRS
                px, py = x, y
            else:
                # transform from entry_crs to input_crs
                src = CRS.from_user_input(entry_crs)
                dst = CRS.from_user_input(input_crs)
                if src == dst:
                    px, py = x, y
                else:
                    transformer = Transformer.from_crs(src, dst, always_xy=True)
                    px, py = transformer.transform(x, y)
            # calculate along-line distance of this projected point (closest point distance along line)
            # We'll project the input CRS point back to lon/lat or meters and compute along-line distance by walking coords
            pt = Point(px, py)
            # compute nearest point along main_line by computing cumulative distances along coords and projection of this point to the line
            # Using shapely's project requires same units/crs and works only for projected lines. For geographic, approximate by finding nearest vertex and then geodesic distance
            if is_projected:
                dist_along = main_line.project(pt)
            else:
                # fallback: find nearest coordinate vertex and its cumulative distance
                # This is an approximation but acceptable for manual points in geographic coordinates
                min_d = float('inf')
                min_idx = 0
                for i, (lon, lat) in enumerate(coords):
                    _, _, d = geod.inv(px, py, lon, lat)
                    if d < min_d:
                        min_d = d
                        min_idx = i
                # cumulative distance at that vertex
                # cumul was computed from coords earlier
                dist_along = cumul[min_idx]  # approx
            manual_points.append({'dist': dist_along, 'label': lbl, 'ptype': 'manual', 'meta': entry})
        # add manual points into feature_points list
        feature_points.extend(manual_points)

    # ----------------- Normalize & sort feature points; deduplicate very close ones -----------------
    feature_points_sorted = sorted(feature_points, key=lambda x: x['dist'])
    deduped = []
    for fp in feature_points_sorted:
        if deduped and abs(fp['dist'] - deduped[-1]['dist']) <= eps:
            # merge priority: keep existing (earlier) unless the new one is "First_Point"
            if fp['ptype'] == 'first':
                deduped.insert(0, fp)
            else:
                continue
        else:
            deduped.append(fp)
    feature_points_sorted = deduped

    # ----------------- Construct actual geometries for feature anchors (except Span_End) -----------------
    anchors = []
    for fp in feature_points_sorted:
        if fp['ptype'] == 'span_end':
            continue
        pt_geom = point_at_distance_along_line(main_line, fp['dist'], is_projected)
        anchors.append({'dist': fp['dist'], 'label': fp['label'], 'ptype': fp['ptype'], 'meta': fp['meta'], 'geometry': pt_geom})

    # ----------------- Insert distance points (2.b) -----------------
    # Build a list of anchor distances including the virtual end
    anchor_dists = [fp['dist'] for fp in feature_points_sorted]  # includes Span_End at end
    distance_counters = 0
    dist_points = []
    for i in range(len(anchor_dists) - 1):
        a = anchor_dists[i]
        b = anchor_dists[i + 1]
        gap = b - a
        if gap <= 0:
            continue
        # generate intermediate distance points a + k * distance_interval where < b
        k = 1
        while True:
            pos = a + k * distance_interval
            if pos + 1e-6 >= b:
                break
            distance_counters += 1
            label = f"Distance_Point_{distance_counters}"
            pt = point_at_distance_along_line(main_line, pos, is_projected)
            dist_points.append({'dist': pos, 'label': label, 'ptype': 'distance', 'meta': {}, 'geometry': pt})
            k += 1

    # ----------------- Combine anchors and distance points -----------------
    combined = anchors + dist_points
    combined_sorted = sorted(combined, key=lambda x: x['dist'])

    # ----------------- Cleaning logic (2.c) - sequential pass -----------------
    # We'll walk from start to end; keep a list 'kept'. Always keep the very first point globally.
    kept = []
    if not combined_sorted:
        print("No points generated.")
        return gpd.GeoDataFrame(columns=['label', 'ptype', 'dist_m', 'geometry'], crs=gdf.crs), main_line

    # helper to check if point is a crossing endpoint
    def is_cross_endpoint(pt):
        return pt['ptype'] in ('cross_start', 'cross_end', 'bridge_before', 'bridge_after', 'bridge_single')

    # helper to test same crossing id (if metadata present)
    def crossing_id_of(pt):
        m = pt.get('meta', {})
        return m.get('crossing_id') or m.get('crossing_id')

    # Put the very first point into kept
    kept.append(combined_sorted[0])
    # iterate over subsequent points
    for curr in combined_sorted[1:]:
        # print(combined_sorted)
        last = kept[-1]
        gap = curr['dist'] - last['dist']
        # print(f"curr: {curr['dist']} {curr['label']}, last: {last['dist']} {last['label']}, gap: {gap} ")
        # print(last)
        if gap >= min_buffer:
            # far enough - keep
            kept.append(curr)
            continue

        # Too close: apply deletion priority rules
        # If one of the two is the absolute first point (label 'First_Point'), keep it and drop the other:
        if last.get('label') == 'First_Point':
            # always keep last (the first point). Decide whether to keep curr based on priority: delete crossing endpoints near distance points
            if is_cross_endpoint(curr) and curr['ptype'] in ('cross_start', 'cross_end'):
                # delete crossing endpoint (skip curr)
                # (rule: if crossing start or end is too close to a distance point -> delete crossing start/end)
                # skip adding curr
                continue
            else:
                # drop curr (because we must keep the first and the second is within min_buffer)
                continue

        # If pair is crossing endpoint vs distance point: delete the crossing endpoint
        if is_cross_endpoint(curr) and last['ptype'] == 'distance':
            print("crossings & distance check")
            # curr is crossing endpoint too-close to a distance point -> delete curr
            continue
        if curr['ptype'] == 'distance' and is_cross_endpoint(last):
            print("distance & crossing check")
            # last is crossing endpoint too-close to a distance point -> delete last (but we already kept last)
            # According to "Always keep first point in sequence", we only allowed deletion of last when it's not the absolute first.
            # To implement 'delete last', remove last from kept and compare curr to new last recursively.
            # But be careful to avoid infinite loops; we'll implement by removing last and re-testing against new last.
            # Remove last
            removed = kept.pop()
            # Now, compare curr with new last (if any)
            if not kept:
                # nothing before; keep curr as first
                kept.append(curr)
                continue
            # compute gap with new last and re-evaluate - re-run logic for curr
            new_last = kept[-1]
            new_gap = curr['dist'] - new_last['dist']
            if new_gap >= min_buffer:
                kept.append(curr)
                continue
            else:
                # recursively apply same rules by temporarily making curr the candidate in the next loop iteration:
                # We'll implement a simple approach: if new_last is crossing_end and curr a crossing_start and both belong to different crossings -> delete both
                # But here curr may still conflict; safer approach: skip curr (prefer not to re-enter complex recursion)
                # For simplicity, drop curr (we already removed last which was the crossing endpoint).
                continue

        # If both are crossing endpoints of different crossings: delete both (unless one is absolute first)
        if is_cross_endpoint(last) and is_cross_endpoint(curr):
            print("different crossings check")
            id_last = crossing_id_of(last)
            id_curr = crossing_id_of(curr)
            if id_last != id_curr:
                # delete both: we must remove last and skip curr.
                # But if last is the absolute First_Point keep it.
                if last.get('label') == 'First_Point':
                    # keep last, drop curr
                    continue
                else:
                    # remove last and skip curr
                    kept.pop()
                    continue

        # If both are endpoints of the same crossing and crossing length < small_crossing_thresh: keep only the one farther from previous kept point
        if is_cross_endpoint(last) and is_cross_endpoint(curr):
            print("same crossings check")
            if crossing_id_of(last) and crossing_id_of(curr) and (crossing_id_of(last) == crossing_id_of(curr)):
                # same crossing id
                seg_len = last.get('meta', {}).get('seg_length') or curr.get('meta', {}).get('seg_length') or 0.0
                if seg_len < small_crossing_thresh:
                    # compute distance to previous kept point (the point before last) -- note previous kept exists because last isn't absolute first (handled earlier)
                    prev = kept[-2] if len(kept) >= 2 else None

                    if prev is None:
                        # nothing before previous, keep last and drop curr
                        continue
                    dist_prev_to_last = last['dist'] - prev['dist']
                    dist_prev_to_curr = curr['dist'] - prev['dist']
                    print(f"prev:{prev}")
                    # Keep the one that is farther from previous; we should have kept 'last' already, so if curr is farther, replace last with curr
                    if dist_prev_to_curr > dist_prev_to_last:
                        # replace last by curr
                        kept.pop()
                        kept.append(curr)
                        continue
                    else:
                        # keep last, drop curr
                        continue

        # At this point, none of the special rules apply: default behaviour -> keep the earlier (last) and drop the later (curr)
        # So simply skip curr
        continue

    # 'kept' now contains cleaned points in order
    final_points = kept

    # ----------------- Build output GeoDataFrame -----------------
    out_gdf = gpd.GeoDataFrame(
        {
            'label': [p['label'] for p in final_points],
            'ptype': [p['ptype'] for p in final_points],
            'dist_m': [p['dist'] for p in final_points],
            'geometry': [p['geometry'] for p in final_points],
            'span':s
        },
        crs=gdf.crs
    )

    # Save
    # out_gdf.to_file(output_path)
    print(f"Saved {len(out_gdf)} points to ")

    return out_gdf, main_line

# -------------------- Visualization --------------------

def visualize_results(input_path, points_gdf_or_path, main_line=None):
    lines = gpd.read_file(input_path)
    if isinstance(points_gdf_or_path, str):
        pts = gpd.read_file(points_gdf_or_path)
    else:
        pts = points_gdf_or_path
    fig, ax = plt.subplots(figsize=(10,6))
    lines.plot(ax=ax, color="lightgray", linewidth=2)
    if main_line is not None:
        gpd.GeoSeries([main_line], crs=pts.crs).plot(ax=ax, color="gray", linewidth=1, linestyle="--")
    # markers by ptype
    mapping = {
        'bridge_before': ('s', 80),
        'bridge_after': ('s', 80),
        'bridge_single': ('s', 80),
        'cross_start': ('D', 60),
        'cross_end': ('D', 60),
        'distance': ('o', 30),
        'first': ('*', 100),
        'manual': ('^', 60)
    }
    for ptype, (marker, size) in mapping.items():
        sub = pts[pts['ptype'] == ptype]
        if not sub.empty:
            sub.plot(ax=ax, markersize=size, marker=marker, label=ptype)
    # plot any other
    others = pts[~pts['ptype'].isin(mapping.keys())]
    if not others.empty:
        others.plot(ax=ax, color='black', markersize=30, label='other')
    for idx, row in pts.iterrows():
        try:
            x = row.geometry.x
            y = row.geometry.y
        except Exception:
            continue
        ax.text(x, y + 2, row['label'], fontsize=7)
    plt.legend()
    plt.title("Span and Extracted/Cleaned Points (v4)")
    plt.xlabel("X / Lon")
    plt.ylabel("Y / Lat")
    plt.show()

# -------------------- Sample generator & main --------------------

if __name__ == "__main__":
    version = "5.0"
    # Example manual points JSON (optional). Save a small sample file if you want to test manual points:
    # [
    #   {"x": 2000.0, "y": 0.0, "label": "User_Manual_1"},
    #   {"x": 5200.0, "y": 0.0, "label": "User_Manual_2"}
    # ]
    # save as manual_points.json and pass manual_points_json="manual_points.json"
    sample_path = '../References/Output/Final/OFC_New_Gangev-1_Seg_Span_Seq.shp'
    gdf = gpd.read_file(sample_path)
    span_list = gdf.sort_values('span_name').span_name.unique()
    merged = gpd.GeoDataFrame(columns=['label', 'ptype', 'dist_m', 'geometry', 'span'], crs=gdf.crs)
    for s in span_list:
        out_gdf, main_line = process_shapefile(
            sample_path,
            span_filter=s,
            crossing_offset=20.0,
            feature_endpoint_offset=10.0,
            crossing_types=["road cross", "bridge"],
            crossing_field="crossing_t",
            distance_interval=1800.0,
            min_buffer=150.0,
            small_crossing_thresh=150.0,
            manual_points_json=None  # set to "manual_points.json" to include manual points
        )
        # visualize_results(sample_path, out_gdf, main_line=main_line)
        merged = gpd.GeoDataFrame(pd.concat([merged,out_gdf], ignore_index=True), crs=merged.crs)
        merged.to_file("manholes.shp")