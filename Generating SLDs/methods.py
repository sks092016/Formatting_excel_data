from shapely.ops import transform
import pyproj
import json
import sys
import os
import re
import zipfile
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point, LineString
from collections import defaultdict
from pyproj import Geod
from collections import defaultdict

def line_length_meter(line):
    geod = Geod(ellps="WGS84")
    length_m = geod.line_length(
        [p[0] for p in line.coords],  # longitudes
        [p[1] for p in line.coords]  # latitudes
    )
    return length_m

def reverse_geom(geom):
    return LineString(list(geom.coords)[::-1])

def merge_consecutive(group):
    """
    Merge only consecutive LineStrings with the same row_authority.
    If an authority repeats later (non-contiguous), it will be a new record.
    """
    merged = []
    current_geom = None
    current_auth = None
    first_seq = None
    st_ch = 0
    end_ch = 0
    current_length = 0
    ring = ''

    for idx, row in enumerate(group.itertuples()):
        if current_auth == row.road_autho:
            new_geom = row.geometry
            try:
                if current_geom.coords[-1] == new_geom.coords[0]:
                    # Case 1: Already aligned (end-to-start)
                    pass
                elif current_geom.coords[-1] == new_geom.coords[-1]:
                    # Case 2: Reverse new so end matches start
                    new_geom = LineString(list(new_geom.coords)[::-1])
                elif current_geom.coords[0] == new_geom.coords[-1]:
                    # Case 3: Reverse current so start matches end
                    current_geom = LineString(list(current_geom.coords)[::-1])
                    new_geom = LineString(list(new_geom.coords)[::-1])
                elif current_geom.coords[0] == new_geom.coords[0]:
                    # Case 4: Reverse both so they align
                    current_geom = LineString(list(current_geom.coords)[::-1])
                else:
                    # No match → skip or handle separately
                    continue
                coords = list(current_geom.coords) + list(new_geom.coords)[1:]
                current_geom = LineString(coords)
            except Exception as e:
                # print(row.OBJECTID)
                print(row.geometry)
                print(e)
                continue
        else:
            # Save previous block before switching
            if current_geom is not None:
                current_length = line_length_meter(current_geom)
                end_ch += current_length
                next_geom = group.iloc[current_idx + 1].geometry
                if current_geom.coords[-1] == next_geom.coords[0]:
                    pass  # Already correct
                elif current_geom.coords[0] == next_geom.coords[0]:
                    current_geom = reverse_geom(current_geom)
                elif current_geom.coords[0] == next_geom.coords[-1]:
                    current_geom = reverse_geom(current_geom)
                merged.append((row.span_name, current_auth, row.span_id,ring,first_seq,current_length,st_ch,end_ch,current_geom))
            # Start a new merge block
            current_geom = row.geometry
            current_auth = row.road_autho
            first_seq = row.Sequqnce
            ring = row.ring_no
            current_idx = idx
            if first_seq == 1:
                st_ch = 0.0
            else:
                st_ch = end_ch
            current_length = 0
    # Save last block
    if current_geom is not None:
        current_length = line_length_meter(current_geom)
        end_ch += current_length
        merged.append(
            (row.span_name, current_auth, row.span_id, ring ,first_seq, current_length, st_ch, end_ch, current_geom))
    return merged

def process_shapefile(input_path, output_path):
    """Read, merge, and save shapefile with proper consecutive grouping."""
    gdf = gpd.read_file(input_path)

    results = []
    # Group by span & span_seq to preserve order
    for span, group in gdf.groupby(["span_name"], sort=False):
        group_sorted = group.sort_values(by="Sequqnce", key=lambda col: col.astype(float))  # ensure order
        merged = merge_consecutive(group_sorted)
        results.extend(merged)

    # Convert to GeoDataFrame
    out_gdf = gpd.GeoDataFrame(
        results,
        columns=["span_name","road_autho","span_seq","ring","first_segment",'length','st_ch','end_ch',"geometry"],
        geometry="geometry",
        crs=gdf.crs
    )

    out_gdf.to_file(output_path)
    print(f"✅ Output written to {output_path}")
    return out_gdf

def process_span_data(input_gdf, output_shapefile, output_json):
    # Ensure CRS is WGS84
    if input_gdf.crs is None or input_gdf.crs.to_epsg() != 4326:
        input_gdf = input_gdf.to_crs(epsg=4326)

    output_rows = []
    span_details = {}

    # Process each span_name separately
    for span, group in input_gdf.groupby("span_name", sort=False):
        group = group.sort_values(by="st_ch")

        # Add to JSON aggregation
        span_details[span] = group.groupby("road_autho")["length"].sum().to_dict()
        span_details[span]['Ring'] = group['ring'].unique().tolist()[0]
        span_details[span]['Span_id'] = group['span_seq'].unique().tolist()[0]
        # Extract start & end points with chainages
        start_point_name = span.split(" TO ")[0].strip()
        end_point_name = span.split(" TO ")[-1].strip()

        for idx, row in group.iterrows():
            coords = list(row.geometry.coords)

            # First row start point
            if row["st_ch"] == group["st_ch"].min():
                output_rows.append({
                    "span_name": span,
                    "Point Name": start_point_name,
                    "ring": span_details[span]["Ring"],
                    "Chainage": row["st_ch"],
                    "geometry": Point(coords[0])
                })

            # Intermediate points (start of segment except first)
            if row["st_ch"] != group["st_ch"].min():
                output_rows.append({
                    "span_name": span,
                    "Point Name": "",
                    "ring": span_details[span]["Ring"],
                    "Chainage": row["st_ch"],
                    "geometry": Point(coords[0])
                })

            # Last segment end point
            if row["end_ch"] == group["end_ch"].max():
                output_rows.append({
                    "span_name": span,
                    "Point Name": end_point_name,
                    "ring": span_details[span]["Ring"],
                    "Chainage": row["end_ch"],
                    "geometry": Point(coords[-1])
                })

    # Create output GeoDataFrame
    output_gdf = gpd.GeoDataFrame(output_rows, crs="EPSG:4326")

    # Save shapefile
    output_gdf.to_file(output_shapefile)

    # Save JSON
    with open(output_json, "w") as f:
        json.dump(span_details, f, indent=4)

    return output_gdf, span_details

def line_length_meter(line):
    geod = Geod(ellps="WGS84")
    length_m = geod.line_length(
        [p[0] for p in line.coords],  # longitudes
        [p[1] for p in line.coords]  # latitudes
    )
    return length_m

def numeric_span_seq(v):
    """Return first numeric group found in span_seq for sorting; fallback 0"""
    if v is None:
        return 0
    m = re.findall(r'\d+', str(v))
    return int(m[0]) if m else 0

def node_key_from_coord(coord):
    """coord may be tuple (x,y) or shapely Point-like; return rounded tuple"""
    return (round(float(coord[0]), 6), round(float(coord[1]), 6))

def build_connected_components(gdf):
    """
    Build connected components using segment endpoints (rounded).
    Returns list of lists of index labels (same index as gdf)
    """
    parent = {}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    def union(a,b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    nodes = set()
    seg_list = []
    for idx, row in gdf.iterrows():
        coords = list(row.geometry.coords)
        s = node_key_from_coord(coords[0])
        e = node_key_from_coord(coords[-1])
        nodes.add(s); nodes.add(e)
        seg_list.append((idx, s, e))
    for n in nodes:
        parent[n] = n
    for _idx, s, e in seg_list:
        union(s, e)
    comps = defaultdict(list)
    for idx, s, e in seg_list:
        root = find(s)
        comps[root].append(idx)
    return list(comps.values())

def orient_segment_geometry(seg_geom: LineString, desired_prev_point, prefer_start=True):
    coords = list(seg_geom.coords)
    start_key = node_key_from_coord(coords[0])
    end_key = node_key_from_coord(coords[-1])
    # If already matches desired, keep as is
    if prefer_start and start_key == desired_prev_point:
        return seg_geom
    if (not prefer_start) and end_key == desired_prev_point:
        return seg_geom
    # Otherwise reverse if that will match
    if prefer_start and end_key == desired_prev_point:
        return LineString(list(reversed(coords)))
    if (not prefer_start) and start_key == desired_prev_point:
        return LineString(list(reversed(coords)))
    # No match - return original (can't orient)
    return seg_geom

def process(input_path, output_path, output_crs="EPSG:4326", work_utm="EPSG:32643"):
    gdf = gpd.read_file(input_path)
    # Basic required columns check (not strict)
    for col in ["span_seq", "ring", "first_segm"]:
        if col not in gdf.columns:
            print(f"Warning: expected column '{col}' not found in input. Script will still try to proceed.")
    # Project to UTM for length calculations
    # gdf_proj = gdf.to_crs(work_utm)
    gdf_proj = gdf
    out_features = []
    # Iterate per ring
    for ring_val, ring_gdf in gdf_proj.groupby("ring", sort=False):
        comps = build_connected_components(ring_gdf)
        for comp in comps:
            sub = ring_gdf.loc[comp].copy()
            # Sort by numeric span_seq and first_segm
            sub["__span_n"] = sub["span_seq"].apply(numeric_span_seq)
            # coerce first_segm to numeric for sort (if present)
            try:
                sub["__first_segm_n"] = sub["first_segm"].astype(float)
            except:
                sub["__first_segm_n"] = sub["first_segm"].apply(lambda v: float(v) if v is not None else 0.0)
            sub = sub.sort_values(["__span_n", "__first_segm_n"], ascending=[True, True])
            # Now order by this sort and ensure geometry orientation follows the sorted order:
            ordered_indices = list(sub.index)
            # We'll walk through ordered segments and if necessary reverse geometry so the start of
            # the next segment matches the end of the previous (or vice-versa) following span order.
            cumulative = 0.0
            prev_end_key = None
            for i, idx in enumerate(ordered_indices):
                row = sub.loc[idx]
                geom = row.geometry
                coords = list(geom.coords)
                start_key = node_key_from_coord(coords[0])
                end_key = node_key_from_coord(coords[-1])
                if row.ring == "R4-C1":
                    print(start_key)
                    print(end_key)
                # Orientation logic (unchanged)
                if i == 0:
                    if len(ordered_indices) > 1:
                        next_row = sub.loc[ordered_indices[i + 1]]
                        next_coords = list(next_row.geometry.coords)
                        next_start_key = node_key_from_coord(next_coords[0])
                        if end_key == next_start_key:
                            oriented = geom
                        elif start_key == next_start_key:
                            oriented = LineString(list(reversed(coords)))
                        else:
                            oriented = geom
                    else:
                        oriented = geom
                else:
                    if start_key == prev_end_key:
                        oriented = geom
                    elif end_key == prev_end_key:
                        oriented = LineString(list(reversed(coords)))
                    else:
                        oriented = geom
                # Update end tracking
                oriented_coords = list(oriented.coords)
                start_key = node_key_from_coord(oriented_coords[0])
                end_key = node_key_from_coord(oriented_coords[-1])
                prev_end_key = end_key
                last_end_point = oriented_coords[-1]  # Store final endpoint
                # seg_length = oriented.length
                seg_length = line_length_meter(oriented)
                ch_value = float(cumulative)
                # ✅ NEW: derive name if first_segm = 1
                span = row.get("span_name", "")
                fs = row.get("first_segm", 0)
                if str(fs) == "1" or fs == 1:
                    name_val = span.split(" TO ")[0]
                else:
                    name_val = ""
                # Start point output
                start_pt = Point(oriented_coords[0])
                out_features.append({
                    "span_name": row.get("span_name"),
                    "road_autho": row.get("road_autho"),
                    "span_seq": row.get("span_seq"),
                    "ring": row.get("ring"),
                    "first_segm": row.get("first_segm"),
                    "name": name_val,  # ✅ added output
                    "Ch": ch_value,
                    "geometry": start_pt
                })
                cumulative += seg_length
            # ✅ After the loop — add final end-point chainage for this component
            print(row.get("span_name"))
            if last_end_point is not None:
                out_features.append({
                    "span_name": row.get("span_name"),
                    "road_autho": row.get("road_autho"),
                    "span_seq": row.get("span_seq"),
                    "ring": row.get("ring"),
                    "first_segm": row.get("first_segm"),
                    "name":  row.get("span_name").split(" TO ")[1], # ✅ still carry
                    "Ch": float(cumulative),
                    "geometry": Point(last_end_point)
                })
    # Build GeoDataFrame in projected CRS and convert to requested output CRS
    if len(out_features) == 0:
        print("No output features created. Please check input data.")
        return
    out_gdf = gpd.GeoDataFrame(out_features, geometry="geometry", crs=output_crs)
    # out_gdf = out_gdf.to_crs(output_crs)
    # Ensure output folder exists
    out_folder = Path(output_path).parent
    out_folder.mkdir(parents=True, exist_ok=True)
    # Write shapefile
    out_gdf.to_file(output_path)
    print("Saved output shapefile:", output_path)