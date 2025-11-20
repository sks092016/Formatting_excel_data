import numpy as np
import sys
import os
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

crs = "EPSG:4326"
warnings.filterwarnings("ignore", category=UserWarning)
geod = Geod(ellps="WGS84")

#---------------------- Finding the Sharp Turns----------------------------#
def angle_between(p1, p2, p3):
    """Return angle (in degrees) formed by three points p1-p2-p3."""
    a = np.array(p1)
    b = np.array(p2)
    c = np.array(p3)

    ba = a - b
    bc = c - b

    if np.linalg.norm(ba) == 0 or np.linalg.norm(bc) == 0:
        return None

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1, 1)
    return math.degrees(math.acos(cosine_angle))

def find_sharp_turns(input_shapefile, output_shapefile, output_json, angle_threshold, group_field):
# === Read Data ===
    gdf = gpd.read_file(input_shapefile)
    if group_field not in gdf.columns:
        gdf[group_field] = 0  # fallback group if field missing
    sharp_points = []
    json_records = []
    # === Process by Group ===
    for span, subset in gdf.groupby(group_field):
        # Build a mapping of endpoints
        endpoints = []
        for idx, row in subset.iterrows():
            try:
                if row["scope"].lower() == 'To Be Replace' or row["scope"].lower() == 'Partial OK' :
                    continue
            except: pass
            geom = row.geometry
            if not isinstance(geom, LineString):
                continue
            coords = list(geom.coords)
            start, end = Point(coords[0]), Point(coords[-1])
            endpoints.append((idx, start, end))
        # Compare each segment pair for connection
        for i, (idx1, s1, e1) in enumerate(endpoints):
            for j, (idx2, s2, e2) in enumerate(endpoints):
                if i >= j:
                    continue
                # Check if endpoints are the same (shared node)
                for p1, p2 in [(e1, s2), (s1, e2), (e1, e2), (s1, s2)]:
                    if p1.distance(p2) < 1e-6:  # nearly same point
                        # compute direction vectors
                        line1 = gdf.loc[idx1, "geometry"]
                        line2 = gdf.loc[idx2, "geometry"]
                        coords1 = list(line1.coords)
                        coords2 = list(line2.coords)
                        # get neighbor points for angle computation
                        # pick last two points of line1 and first two points of line2 based on shared point
                        if Point(coords1[-1]).distance(p1) < 1e-6:
                            p_before = coords1[-2]
                        else:
                            p_before = coords1[1]
                        if Point(coords2[0]).distance(p2) < 1e-6:
                            p_after = coords2[1]
                        else:
                            p_after = coords2[-2]
                        mid = (p1.x, p1.y)
                        angle = angle_between(p_before, mid, p_after)
                        if angle is not None and angle < angle_threshold:
                            pt = Point(mid)
                            sharp_points.append({
                                'geometry': pt,
                                'span_name': span,
                                'angle': angle,
                                'line_1': idx1,
                                'line_2': idx2
                            })
                            json_records.append({
                                "x": pt.x,
                                "y": pt.y,
                                "crs": gdf.crs.to_string() if gdf.crs else "Unknown",
                                "label": f"Sharp_{span}_{idx1}_{idx2}",
                                "type": "sharp_edge",
                                "span": span
                            })
    return sharp_points, json_records,gdf

#-----------------------Brown Field Data ------------------------------------#
def to_epsg4326(gdf):
    """Ensure GeoDataFrame is in EPSG:4326 CRS."""
    if gdf.crs is None:
        raise ValueError("Input shapefile must have a valid CRS.")
    if gdf.crs.to_string() != crs:
        return gdf.to_crs(crs)
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

def process_brown_field(input_shp, output_points_shp, output_json_path, scope,crs, brown_field_label, ptype, shape_file_data_field):
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
        print(f"Processing {span}...")
        sub = span_df[span_df[shape_file_data_field].str.lower()==scope]
        if sub.empty:
            print("sub is empty")
            continue
        # Sort by seg_seq
        sub = sub.sort_values(by="seg_seq")
        # Merge consecutive segments with exact endpoint match
        merged_lines = merge_consecutive_segments(list(sub.geometry))
        # Extract start and end points from each merged group
        for merged in merged_lines:
            start, end = get_start_end(merged)
            for (lon, lat) in [start, end]:
                # key = (float(lon), float(lat))
                # if key not in existing_coords:
                #     existing_coords.add(key)
                entry = {
                    "x": lon,
                    "y": lat,
                    "crs": crs,
                    "label": brown_field_label,
                    "type": ptype,
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
            "label": [brown_field_label] * len(new_points),
            "type": [ptype] * len(new_points),
            "span": [e["span"] for e in new_entries]
        }, geometry=new_points, crs=crs)
        out_gdf.to_file(output_points_shp)
        print(f"Saved {len(new_points)} unique endpoint points to {output_points_shp}")
    else:
        print("No new unique endpoints found. Shapefile not updated.")
    return len(new_entries)

#-----------------------Final Manhole Calculations------------------------#

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

def process_shapefile(
    input_path: str,
    span_filter: Optional[str] = None,
    crossing_offset: float = 50.0,           # distance from crossing start/end for *major* crossings like road-cross
    feature_endpoint_offset: float = 10.0,   # small offset used when placing feature endpoints (per 2.a)
    crossing_types: Optional[List[str]] = None,  # list of values (case-insensitive) in the input field to treat as crossings
    crossing_field: str = "crossing_t",      # field in input with crossing type (fallback to 'feature_type')
    distance_interval: float = 1800.0,       # spacing of distance points (2.b)
    min_buffer: float = 150.0,               # minimum allowed distance between any two points (2.c)
    small_crossing_thresh: float = 150.0,    # small crossing length threshold (meters)
    manual_points_json: Optional[str] = None # path to JSON with manual points to add
):
    gdf = gpd.read_file(input_path)
    if gdf.empty:
        raise ValueError("Input shapefile is empty or unreadable.")
    # Filter span_name if requested
    if span_filter is not None:
        if "span_name" not in gdf.columns:
            raise ValueError("Input shapefile lacks 'span_name' field required for filtering.")
        gdf = gdf[gdf["span_name"] == span_filter]
    if gdf.empty:
        print(f"No records found for span_name '{span_filter}'")
        return
    # Sorting segments in their sequence order
    if "seg_seq" not in gdf.columns: #TODO : Chnage the column name for sequnce
        raise ValueError("Input shapefile must have 'seg_seq' field.")
    gdf["sort_key"] = gdf["seg_seq"].apply(natural_sort_key) #TODO : Chnage the column name for sequnce
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
        crossing_types = ["nh road cross","railway cross", "bpcl gas"] #TODO for road crossing
    # Normalize crossing types to lower-case for comparison
    crossing_types = [t.strip().lower() for t in crossing_types]
    # ----------------- Place feature points (2.a) -----------------
    # We'll create a list of dicts representing feature anchors along the merged line:
    feature_points = []
    # include small initial First_Point at feature_endpoint_offset (or 10m earlier behaviour)
    first_pt_dist = min(feature_endpoint_offset, total_len)
    feature_points.append({'dist': first_pt_dist, 'label': 'First_Point', 'ptype': 'first','meta': {'reason': 'StartOffset'}})
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
        ctype_clean = None
        if isinstance(ctype, str):
            ctype_clean = ctype.strip().lower()
        # If this segment matches one of the crossing_types, place points at both ends offset inward by feature_endpoint_offset
        if ctype_clean in crossing_types:
            crossing_counter += 1
            start_offset = max(0.0, start_dist - crossing_offset)
            end_offset = min(total_len, end_dist + crossing_offset)
            label_s = f"Cross_{crossing_counter}_Start"
            label_e = f"Cross_{crossing_counter}_End"
            feature_points.append({'dist': start_offset, 'label': label_s, 'ptype': 'cross_start',
                                   'meta': {'seg_index': idx, 'crossing_id': crossing_counter, 'seg_length': seg_length}})
            feature_points.append({'dist': end_offset, 'label': label_e, 'ptype': 'cross_end',
                                   'meta': {'seg_index': idx, 'crossing_id': crossing_counter, 'seg_length': seg_length}})
        # Additionally handle explicit "bridge" handling (with crossing_offset behavior if segment is a bridge)
        if ctype_clean == "bridge" or ctype_clean == "river bridge":
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
    # ----------------- Integrate manual points (additional feature) -----------------
    manual_points = []
    if manual_points_json:
        with open(manual_points_json, 'r') as fh:
            data = json.load(fh)
        # Determine coordinate transformation if manual point has different crs than input gdf
        input_crs = crs
        for entry in data:
            if entry.get("span").lower() == span_filter.lower():
                x = entry.get('x')
                y = entry.get('y')
                lbl = entry.get('label', 'Manual_Point')
                type = entry.get('type', 'manual')
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
                pt = Point(px, py)
                # compute nearest point along main_line by computing cumulative distances along coords and projection of this point to the line
                if is_projected:
                    dist_along = main_line.project(pt)
                else:
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
                manual_points.append({'dist': dist_along, 'label': lbl, 'ptype': type, 'meta': entry})
        # add manual points into feature_points list
        feature_points.extend(manual_points)
    # Add virtual Span_End anchor for gap filling
    feature_points.append({'dist': total_len, 'label': 'Span_End', 'ptype': 'span_end', 'meta': {}})
    # ----------------- Normalize & sort feature points; deduplicate very close ones -----------------
    feature_points_sorted = sorted(feature_points, key=lambda x: x['dist'])
    deduped = []
    for fp in feature_points_sorted:
        if deduped and abs(fp['dist'] - deduped[-1]['dist']) <= eps:
            # merge priority: keep existing (earlier) unless the new one is "First_Point"
            if fp['ptype'] == 'first' or fp['ptype'] == 'Brown Field':
                # deduped.insert(0, fp)
                deduped.append(fp)
            else:
                continue
        else:
            deduped.append(fp)
    feature_points_sorted = deduped
    #------------------ Removing the first point in case of brown field segments -------------------------
    fp_sorted = []
    for fp in feature_points_sorted:
        if fp_sorted and fp_sorted[-1]['ptype'] == 'Brown Field' and fp['ptype'] == 'first':
            continue
        else:
            fp_sorted.append(fp)
    feature_points_sorted = fp_sorted
    # ----------------- Construct actual geometries for feature anchors (except Span_End) -----------------
    anchors = []
    for fp in feature_points_sorted:
        if fp['ptype'] == 'span_end':
            continue
        if anchors and anchors[-1]['ptype'] == 'Brown Field' and fp['ptype'] == 'first':
            continue
        pt_geom = point_at_distance_along_line(main_line, fp['dist'], is_projected)
        anchors.append({'dist': fp['dist'], 'label': fp['label'], 'ptype': fp['ptype'], 'meta': fp['meta'], 'geometry': pt_geom})
    # ----------------- Insert distance points (2.b) -----------------
    # Build a list of anchor distances including the virtual end
    anchor_dists = [fp['dist'] for fp in feature_points_sorted]  # includes Span_End at end
    distance_counters = 0
    dist_points = []
    print(anchor_dists)
    for i in range(len(anchor_dists) - 1):
        a = anchor_dists[i]
        b = anchor_dists[i + 1]
        gap = b - a
        point_type_a = next((r['ptype'] for r in anchors if r['dist'] == a), None)
        point_type_b = next((r['ptype'] for r in anchors if r['dist'] == b), None)
        if point_type_a == 'Brown Field' and point_type_b == 'Brown Field':
            continue
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
    temp_gdf = gpd.GeoDataFrame(
        {
            'label': [p['label'] for p in combined_sorted],
            'ptype': [p['ptype'] for p in combined_sorted],
            'dist_m': [p['dist'] for p in combined_sorted],
            'geometry': [p['geometry'] for p in combined_sorted],
            'span': span_filter
        },
        crs=gdf.crs
    )
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
        if curr.get('label') == 'Brown Field Conn':
            kept.append(curr)
            continue
        try:
            last = kept[-1]
        except IndexError:
            print(span_filter)
            print(kept)
            continue
        gap = curr['dist'] - last['dist']
        if gap >= min_buffer:
            # far enough - keep
            kept.append(curr)
            continue
        # Too close: apply deletion priority rules
        # If one of the two is the absolute first point (label 'First_Point'), keep it and drop the other:
        if last.get('label') == 'Brown Field Conn':
            continue
        if last.get('label') == 'First_Point':
            continue
        # If pair is crossing endpoint vs distance point: delete the crossing endpoint
        if is_cross_endpoint(curr) and last['ptype'] == 'distance':
            # curr is crossing endpoint too-close to a distance point -> delete curr
            continue
        if curr['ptype'] == 'distance' and is_cross_endpoint(last):
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
            'span':span_filter
        },
        crs=gdf.crs
    )
    # Save
    # out_gdf.to_file(output_path)
    print(f"Saved {len(out_gdf)} manholes for span {span_filter}")
    return out_gdf, main_line, temp_gdf