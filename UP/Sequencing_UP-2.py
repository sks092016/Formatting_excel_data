import geopandas as gpd
from shapely.ops import linemerge
from shapely.geometry import Point, MultiLineString
import os

# ------------------ USER CONFIG ------------------

POINT_FILE = "References/input/joints.shp"
LINE_FILE  = "References/input/ofc_rings.shp"
OUTPUT_FILE = "joints_sequenced_FINAL.shp"

POINT_RING_FIELD = "ring_2"
LINE_RING_FIELD  = "ring"

SEQ_FIELD = "seq"

# Projection tolerance (meters)
TOLERANCE = 5.0

# ✅ ORDERED START POINTS PER RING (LON, LAT)
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

# ------------------------------------------------


def merge_lines(geoms):
    merged = linemerge(geoms)
    # if isinstance(merged, MultiLineString):
    #     merged = max(list(merged), key=lambda l: l.length)
    return merged


def main():

    points = gpd.read_file(POINT_FILE)
    lines  = gpd.read_file(LINE_FILE)

    points = points.to_crs(4326)
    lines  = lines.to_crs(4326)

    points[SEQ_FIELD] = None

    for ring in points[POINT_RING_FIELD].dropna().unique():

        print(f"Processing ring: {ring}")

        pt_subset = points[points[POINT_RING_FIELD] == ring]
        ln_subset = lines[lines[LINE_RING_FIELD] == ring]

        if pt_subset.empty or ln_subset.empty:
            print("  Skipped (missing points or line)")
            continue

        merged_line = merge_lines(list(ln_subset.geometry))

        projected = []
        rejected  = []

        for idx, row in pt_subset.iterrows():
            p = row.geometry
            d = merged_line.project(p)
            nearest = merged_line.interpolate(d)
            dist_to_line = p.distance(nearest)

            if dist_to_line <= TOLERANCE:
                projected.append((idx, d, dist_to_line))
            else:
                rejected.append((idx, d, dist_to_line))

        # ✅ SORT BY LINE DISTANCE (CLOCKWISE BASE)
        projected.sort(key=lambda x: x[1])
        if ring == "C06.1":
            print(projected)
        # ✅ ROTATE USING ORDERED START POINTS
        if ring in START_POINTS:
            ordered_starts = START_POINTS[ring]

            for sp in ordered_starts[::-1]:
                sp_point = Point(sp)
                nearest_idx = min(projected, key=lambda x:
                    sp_point.distance(points.loc[x[0]].geometry)
                )[0]

                start_pos = [x[0] for x in projected].index(nearest_idx)
                if ring == "C06.1":
                    print(start_pos)
                projected = projected[start_pos:] + projected[:start_pos]

        # ✅ FINAL SEQUENCE = good points → rejected points at end
        final_order = projected + rejected

        # ✅ ASSIGN SEQUENCE
        seq = 1
        for idx, _, _ in final_order:
            points.at[idx, SEQ_FIELD] = seq
            seq += 1

    points.to_file(OUTPUT_FILE)
    print("\n✅ SEQUENCING COMPLETE")
    print(f"✅ Output written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
