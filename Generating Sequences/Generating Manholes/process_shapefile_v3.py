
#!/usr/bin/env python3
"""
process_shapefile_v3.py

Finalized script to:
 - merge ordered LineString segments preserving sequence
 - extract feature points (Bridge, Road Cross) with specified rules
 - include the initial 10 m point from start
 - insert distance-based points every 1800 meters between consecutive feature points (and to span end)
 - handle projected and geographic CRS (geodesic measurements for EPSG:4326)
 - output a point shapefile with clear labels:
     Distance_Point_1, Distance_Point_2, ...
     Bridge_Point_1, Bridge_Point_2, ...
     RoadCross_Point_1, RoadCross_Point_2, ...
     First_Point
"""

import geopandas as gpd
from shapely.geometry import Point, LineString
from pyproj import Geod
import re
import math
import matplotlib.pyplot as plt
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore", category=UserWarning)

# -------------------- Utility --------------------

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split("([0-9]+)", str(s))]

def ordered_merge(lines):
    """Merge LineStrings in the given order, preserving direction."""
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
    """
    Given list of coords [(x,y), ...], return segment lengths list and cumulative distances at each vertex.
    If projected: use Euclidean distances (assumed meters).
    If geographic: use geodesic distances in meters (lon/lat).
    """
    seg_lens = []
    cumul = [0.0]
    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]):
        if is_projected:
            d = math.hypot(x2 - x1, y2 - y1)
        else:
            # coords are (lon, lat)
            _, _, d = geod.inv(x1, y1, x2, y2)
        seg_lens.append(d)
        cumul.append(cumul[-1] + d)
    return seg_lens, cumul  # seg_lens len = n-1, cumul len = n

def total_length_from_cumulatives(cumul):
    return cumul[-1] if cumul else 0.0

def point_at_distance_along_line(line, distance_m, is_projected):
    """
    Return a shapely Point located distance_m meters along 'line' (LineString).
    If projected -> use shapely.interpolate (distance in same units, meters expected).
    If geographic -> use geodesic interpolation (pyproj.Geod) over line coords.
    """
    if is_projected:
        # shapely expects distance in same units as CRS (meters for projected)
        return line.interpolate(min(distance_m, line.length))
    else:
        # geodesic interpolate walking coords
        coords = list(line.coords)
        cum = 0.0
        for (lon1, lat1), (lon2, lat2) in zip(coords[:-1], coords[1:]):
            az12, az21, seglen = geod.inv(lon1, lat1, lon2, lat2)
            if cum + seglen >= distance_m:
                remaining = distance_m - cum
                lon, lat, _ = geod.fwd(lon1, lat1, az12, remaining)
                return Point(lon, lat)
            cum += seglen
        # if distance beyond end return last point
        x, y = coords[-1]
        return Point(x, y)

# -------------------- Main processing --------------------

def process_shapefile(input_path, output_path="output_points.shp", span_filter=None, distance_interval=1800):
    """
    Main function:
      - input_path: path to segments shapefile
      - output_path: path to write points shapefile
      - span_filter: optional span_name value to filter features
      - distance_interval: meters between distance-based points (default 1800)
    """
    gdf = gpd.read_file(input_path)
    if gdf.empty:
        raise ValueError("Input shapefile is empty or unreadable.")

    # Filter by span_name if requested
    if span_filter is not None:
        if "span_name" not in gdf.columns:
            raise ValueError("Input shapefile lacks 'span_name' field required for filtering.")
        gdf = gdf[gdf["span_name"] == span_filter]
    if gdf.empty:
        raise ValueError(f"No records found for span_name '{span_filter}'")

    # Natural sort by segment_sequence (alphanumeric)
    if "seg_seq" not in gdf.columns:
        raise ValueError("Input shapefile must have 'segment_sequence' field.")
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
    # compute segment lengths and cumulative distances for the merged line
    seg_lens, cumul = segment_lengths_and_cumulatives(coords, is_projected)
    total_len = total_length_from_cumulatives(cumul)

    print(f"CRS: {crs.to_string()} | Projected: {is_projected} | Total length (m): {total_len:.3f}")

    # ---- Collect feature points ----
    feature_points = []  # tuples (dist_along_line_m, label, reason)
    # Always include the 10 m first point as the initial reference
    first_pt_dist = min(10.0, total_len)
    feature_points.append((first_pt_dist, "First_Point", "StartOffset_10m"))

    # counters for label numbering
    counters = defaultdict(int)
    # We'll also store a mapping for duplicates avoidance
    eps = 1e-3  # 1 mm tolerance for dedup

    # Iterate through original ordered segments to find their dist ranges on the merged line.
    # To map each segment's start along-line distance, we walk using lengths of segments in order.
    seg_index = 0
    current_pos = 0.0
    for idx, row in gdf.iterrows():
        seg_geom = row.geometry
        # Find start and end distance of this segment along the merged_line.
        # We compute length of segment using projected or geodesic methods to ensure consistency.
        # For geodesic, compute using geod over the segment coords
        seg_coords = list(seg_geom.coords)
        # compute length of this segment
        seg_length = 0.0
        if is_projected:
            for (x1,y1),(x2,y2) in zip(seg_coords[:-1], seg_coords[1:]):
                seg_length += math.hypot(x2-x1, y2-y1)
        else:
            for (lon1,lat1),(lon2,lat2) in zip(seg_coords[:-1], seg_coords[1:]):
                _,_,d = geod.inv(lon1, lat1, lon2, lat2)
                seg_length += d

        start_dist = current_pos
        end_dist = current_pos + seg_length

        ctype = None
        # check fields for bridge/road cross - user used 'crossing_t' earlier; fallback to feature_type if available
        if "crossing_t" in gdf.columns:
            ctype = row.get("crossing_t", None)
        elif "feature_type" in gdf.columns:
            ctype = row.get("feature_type", None)
        else:
            ctype = row.get("crossing_t", None)  # might be None

        if ctype is not None and isinstance(ctype, str):
            ctype_clean = ctype.strip().lower()
        else:
            ctype_clean = None

        # Handle Road Cross
        if ctype_clean in ("road cross", "road_cross", "roadcross", "roadcrossing", "roadcrossing"):
            counters["RoadCross"] += 1
            dist_here = max(0.0, start_dist)  # start of segment
            label = f"RoadCross_Point_{counters['RoadCross']}"
            feature_points.append((dist_here, label, "RoadCross_start"))

        # Handle Bridge
        if ctype_clean in ("bridge",):
            # Bridge rules
            if seg_length > 150.0:
                # two points: 50m before start and 50m after end (clipped to [0, total_len])
                before_d = max(0.0, start_dist - 50.0)
                after_d = min(total_len, end_dist + 50.0)
                counters["Bridge"] += 1
                label_b = f"Bridge_Point_{counters['Bridge']}_Before"
                counters["Bridge"] += 1
                label_a = f"Bridge_Point_{counters['Bridge']}_After"
                feature_points.append((before_d, label_b, "Bridge_before"))
                feature_points.append((after_d, label_a, "Bridge_after"))
            else:
                # single point: choose start or end whichever is farther from previous feature
                start_candidate = start_dist
                end_candidate = end_dist
                # previous feature = last added feature point distance
                prev_dist = feature_points[-1][0] if feature_points else 0.0
                # distances along line (absolute differences) - since along-line metric
                dstart = abs(start_candidate - prev_dist)
                dend = abs(end_candidate - prev_dist)
                chosen = start_candidate if dstart > dend else end_candidate
                counters["Bridge"] += 1
                label = f"Bridge_Point_{counters['Bridge']}"
                feature_points.append((chosen, label, "Bridge_single"))

        current_pos = end_dist
        seg_index += 1

    # Add virtual end-of-span as a boundary for gap filling (so we fill after last feature up to end if required)
    feature_points.append((total_len, "Span_End", "End"))

    # ---- Normalize & sort feature points; deduplicate if very close ----
    # Sort by distance along line
    feature_points_sorted = sorted(feature_points, key=lambda x: x[0])

    # Deduplicate by proximity along-line (eps meters)
    deduped = []
    for dist, label, reason in feature_points_sorted:
        if deduped and abs(dist - deduped[-1][0]) <= eps:
            # Already have nearly same point; skip or choose nicer label priority (keep existing)
            continue
        deduped.append((dist, label, reason))

    feature_points_sorted = deduped

    # ---- Generate distance-based points between consecutive feature points ----
    output_points = []  # tuples (Point, label, reason, dist_along)
    # First, convert each feature into an actual Point geometry (except Span_End we'll not output but use for gap checks)
    for dist, label, reason in feature_points_sorted:
        if label == "Span_End":
            continue
        pt = point_at_distance_along_line(main_line, dist, is_projected)
        output_points.append((pt, label, reason, dist))

    # Now insert distance-based points between consecutive feature anchors (including start and end)
    # Build a list of distances including both anchors and the virtual end
    anchor_dists = [d for d, l, r in feature_points_sorted]
    # We'll iterate pairs (anchor_dists[i], anchor_dists[i+1])
    distance_counters = 0
    for i in range(len(anchor_dists) - 1):
        a = anchor_dists[i]
        b = anchor_dists[i+1]
        gap = b - a
        if gap <= 0:
            continue
        # number of intermediate distance points to add = floor(gap / distance_interval)
        # but we must not include a point exactly at 'b' (feature anchor). So generate k such that a + k*interval < b
        k = 1
        while True:
            pos = a + k * distance_interval
            if pos + 1e-6 >= b:  # reached or exceeded next anchor
                break
            # create point at pos
            distance_counters += 1
            label = f"Distance_Point_{distance_counters}"
            pt = point_at_distance_along_line(main_line, pos, is_projected)
            output_points.append((pt, label, "DistanceInterval", pos))
            k += 1

    # ---- Deduplicate output_points by along-line proximity and create final GeoDataFrame ----
    # Merge output_points with feature points, ensure sorted along-line
    combined = []
    for pt, label, reason, dist in output_points:
        combined.append((dist, pt, label, reason))
    # Sort by distance
    combined_sorted = sorted(combined, key=lambda x: x[0])

    # Deduplicate if two points are very close along line (within eps)
    final = []
    last_dist = -9999
    for dist, pt, label, reason in combined_sorted:
        if final and abs(dist - last_dist) <= eps:
            # skip duplicates (keep the earlier one)
            continue
        final.append((dist, pt, label, reason))
        last_dist = dist

    # Build GeoDataFrame to write
    out_gdf = gpd.GeoDataFrame({
        "label": [item[2] for item in final],
        "reason": [item[3] for item in final],
        "dist_m": [item[0] for item in final],
        "geometry": [item[1] for item in final]
    }, crs=gdf.crs)

    out_gdf.to_file(output_path)
    print(f"Saved {len(out_gdf)} points to {output_path}")

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
    # plot main_line if provided
    if main_line is not None:
        gpd.GeoSeries([main_line], crs=pts.crs).plot(ax=ax, color="gray", linewidth=1, linestyle="--")
    # differentiate labels by prefix
    for prefix, marker, z in [("Bridge", "s", 60), ("RoadCross", "D", 50), ("Distance_Point", "o", 30), ("First_Point","*",80)]:
        subset = pts[pts["label"].str.contains(prefix)]
        if not subset.empty:
            subset.plot(ax=ax, markersize=z, marker=marker, label=prefix)
    # generic plot for any other
    others = pts[~pts["label"].str.contains("Bridge|RoadCross|Distance_Point|First_Point")]
    if not others.empty:
        others.plot(ax=ax, color="black", markersize=20)
    for idx, row in pts.iterrows():
        ax.text(row.geometry.x, row.geometry.y + 2, row["label"], fontsize=7)
    plt.legend()
    plt.title("Span and Extracted Points")
    plt.xlabel("X / Lon")
    plt.ylabel("Y / Lat")
    plt.show()

# -------------------- Sample generator & main --------------------

def generate_sample_shapefile(filepath="sample_segments_v3.shp"):
    """Create a test shapefile with a few segments; this sample uses projected coords (meters)."""
    spans = []
    # Make a long span 10 segments each 1000 m to test multiple 1800 intervals and a bridge
    x = 0.0
    for i in range(10):
        start = (x, 0.0)
        x += 1000.0
        end = (x, 0.0)
        ctype = "Normal"
        if i == 2:
            ctype = "Bridge"   # a bridge ~1000 m long in this example (>>150)
        if i == 6:
            ctype = "Road Cross"
        spans.append({
            "span_name": "SPAN_TEST",
            "segment_sequence": f"S{i+1}",
            "crossing_t": ctype,
            "geometry": LineString([start, end])
        })
    gdf = gpd.GeoDataFrame(spans, crs="EPSG:32643")
    gdf.to_file(filepath)
    print("Sample shapefile saved to", filepath)
    return filepath

if __name__ == "__main__":
    # Example run: generate sample, process, visualize
    sample_path = '../References/Output/Final/OFC_New_Gangev-1_Seg_Span_Seq.shp'
    gdf = gpd.read_file(sample_path)
    span_list = gdf.sort_values('span_name').span_name.unique()
    for s in span_list:
        out_gdf, main_line = process_shapefile(sample_path, output_path="output_points_v3.shp", span_filter=s, distance_interval=1800)
        visualize_results(sample_path, out_gdf, main_line=main_line)
        break
