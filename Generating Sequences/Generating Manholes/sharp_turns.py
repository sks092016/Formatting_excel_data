import geopandas as gpd
# from markdown_it.common.html_blocks import block_names
from shapely.geometry import Point, LineString
import numpy as np
import math
import json

block_name = "Gangev"
# === Parameters ===
input_shapefile = f'input/OFC_New_{block_name}-1_Seg_Span_Seq.shp'   # your input line shapefile
output_shapefile = f"temp/sharp_turn_points_{block_name}.shp"   # output point shapefile
output_json = f"temp/sharp_turn_points_{block_name}.json"       # output JSON file
angle_threshold = 110  # degrees
group_field = "span_name"   # field that groups related segments (change to match your data)

# === Helper function to compute angle between 3 points ===
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

# === Save Outputs ===
if sharp_points:
    out_gdf = gpd.GeoDataFrame(sharp_points, crs=gdf.crs)
    out_gdf.to_file(output_shapefile)
    print(f"✅ Sharp turn points saved to: {output_shapefile}")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(json_records, f, indent=4)
    print(f"✅ JSON file saved to: {output_json}")
else:
    print("No sharp turns found under the given threshold.")
