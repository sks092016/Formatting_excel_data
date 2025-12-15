#!/usr/bin/env python3
"""
Standalone segment sequencing based on sequenced joints.

REQUIRES:
    pip install geopandas shapely

INPUT:
    joints.shp  -> must contain fields: ring, seq
    segments.shp -> must contain field: ring

OUTPUT:
    segments_sequenced.shp with field seg_seq
"""

import geopandas as gpd
from shapely.geometry import Point, LineString

# ---------------- CONFIG ----------------
JOINTS_FILE = "References/Output/sequenced_output.shp"
SEGMENTS_FILE = "References/Input/OFC_CS.shp"
OUTPUT_FILE = "References/Output/sequenced_segments-2.shp"

RING_FIELD = "rings"
JOINT_SEQ_FIELD = "seq"
SEG_SEQ_FIELD = "seg_seq"

RING_DATA = {
    "R01" : {
        "start_joint" : Point(81.83946815,27.35295317),
        "end_joint" : Point(81.83501082,27.34005387),
        "start_segment" : [(81.83946815,27.35295317), (81.84352657,27.34670577)],
        "end_segment" : [(81.83501082,27.34005387), (81.83946815,27.35295317)]
    },
    "R02" : {
        "start_joint" : Point(81.77920978,27.31722888),
        "end_joint" : Point(81.81169878,27.32997800),
        "start_segment" : [(81.78727344,27.30803231), (81.77920978,27.31722888)],
        "end_segment" : [(81.81169878,27.32997800), (81.81194938,27.32479538)]
    }
}

# ---------------------------------------
def is_linestring_from_endpoints(
    line: LineString,
    endpoint_candidates,
    tolerance=0.00001
):
    """
    Checks whether a LineString's endpoints match (approximately)
    any two points in endpoint_candidates, irrespective of order.

    Parameters
    ----------
    line : shapely.geometry.LineString
    endpoint_candidates : list of (x, y)
        Approximate endpoints to test against
    tolerance : float
        Distance tolerance for matching

    Returns
    -------
    bool
        True if line endpoints match any two candidate points
    """

    if not isinstance(line, LineString):
        return False

    line_start = Point(line.coords[0])
    line_end   = Point(line.coords[-1])

    matched = []

    for pt in endpoint_candidates:
        p = Point(pt)

        if line_start.distance(p) <= tolerance:
            matched.append("start")
        elif line_end.distance(p) <= tolerance:
            matched.append("end")

    # We need both ends to match (order independent)
    return "start" in matched and "end" in matched

def nearest_joint(joints, pt):
    return joints.loc[
        joints.geometry.distance(pt).idxmin()
    ]


def connected_joints(segment, joints):
    touched = joints[joints.geometry.touches(segment.geometry)]
    if touched.empty:
        touched = joints[joints.geometry.distance(segment.geometry) < 0.001]
    return touched


def main():
    joints = gpd.read_file(JOINTS_FILE)
    segs = gpd.read_file(SEGMENTS_FILE)

    segs[SEG_SEQ_FIELD] = None
    global_seq = 1
    #sorted(segs[RING_FIELD].unique())
    rings = ['R01', 'R02']
    for ring in rings:
        print(f"\nProcessing ring {ring}")

        ring_segs = segs[segs[RING_FIELD] == ring]
        ring_joints = joints[joints[RING_FIELD] == ring]
        other_joints = joints[joints[RING_FIELD] != ring]

        if ring_segs.empty:
            continue

        # ---- start_seq FIX (IMPORTANT) ----
        sp = RING_DATA[ring]["start_joint"]
        nearest_other = nearest_joint(other_joints, sp)
        start_seq = int(nearest_other[JOINT_SEQ_FIELD])

        # Identify start/end joints of same ring
        start_joint = nearest_joint(ring_joints, sp)
        end_joint = nearest_joint(ring_joints, RING_DATA[ring]["end_joint"])

        normal = []
        start_seg = []
        end_seg = []
        spur_same = []
        spur_other_pre = []
        spur_other_post = []

        for idx, seg in ring_segs.iterrows():
            cj = connected_joints(seg, joints)

            if is_linestring_from_endpoints(seg, RING_DATA[ring]["start_segment"]):
                start_seg.append((idx, None))
                continue

            if is_linestring_from_endpoints(seg, RING_DATA[ring]["end_segment"]):
                start_seg.append((idx, None))
                continue

            if len(cj) == 2:
                max_seq = cj[JOINT_SEQ_FIELD].astype(int).max()
                normal.append((idx, max_seq))
                continue

            if len(cj) == 1:
                j = cj.iloc[0]
                j_seq = int(j[JOINT_SEQ_FIELD])
                j_ring = j[RING_FIELD]
                if j_ring == ring:
                    spur_same.append((idx, j_seq))
                else:
                    if j_seq < start_seq:
                        spur_other_pre.append((idx, j_seq))
                    else:
                        spur_other_post.append((idx, j_seq))

        # ---- Sorting ----
        normal.sort(key=lambda x: x[1])
        spur_same.sort(key=lambda x: x[1])
        spur_other_pre.sort(key=lambda x: x[1])
        spur_other_post.sort(key=lambda x: x[1])
        for elem in spur_same:
            inserted = False
            for i, (_, idx) in enumerate(normal):
                if idx == elem[1]:
                    normal.insert(i + 1, elem)
                    inserted = True
                    break
            if not inserted:
                normal.append(elem)
        ordered = (
            spur_other_pre +
            start_seg +
            normal +
            end_seg +
            spur_other_post
        )

        for idx, _ in ordered:
            segs.at[idx, SEG_SEQ_FIELD] = global_seq
            global_seq += 1


    segs.to_file(OUTPUT_FILE)
    print("\nSaved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
