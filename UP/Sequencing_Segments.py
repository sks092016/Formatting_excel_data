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
from shapely.geometry import Point

# ---------------- CONFIG ----------------
JOINTS_FILE = "Refernces/Output/sequenced_output.shp"
SEGMENTS_FILE = "References/Input/ofc_rings.shp"
OUTPUT_FILE = "References/output/sequenced_segments.shp"

RING_FIELD = "rings"
JOINT_SEQ_FIELD = "seq"
SEG_SEQ_FIELD = "seg_seq"

START_POINTS = {
    "R01": Point(81.83946815,27.35295317),
    "R02": Point(81.78724340,27.30803201),
}

END_POINTS = {
    "R01": Point(81.83946815,27.35295317),
    "R02": Point(81.81194938,27.32479538),
}
# ---------------------------------------


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

    for ring in sorted(segs[RING_FIELD].unique()):
        print(f"\nProcessing ring {ring}")

        ring_segs = segs[segs[RING_FIELD] == ring]
        ring_joints = joints[joints[RING_FIELD] == ring]
        other_joints = joints[joints[RING_FIELD] != ring]

        if ring_segs.empty:
            continue

        # ---- start_seq FIX (IMPORTANT) ----
        sp = START_POINTS[ring]
        nearest_other = nearest_joint(other_joints, sp)
        start_seq = nearest_other[JOINT_SEQ_FIELD]

        # Identify start/end joints of same ring
        start_joint = nearest_joint(ring_joints, sp)
        end_joint = nearest_joint(ring_joints, END_POINTS[ring])

        normal = []
        start_seg = []
        end_seg = []
        spur_same = []
        spur_other_pre = []
        spur_other_post = []

        for idx, seg in ring_segs.iterrows():
            cj = connected_joints(seg, joints)

            if len(cj) == 2:
                max_seq = cj[JOINT_SEQ_FIELD].max()
                normal.append((idx, max_seq))
                continue

            if len(cj) == 1:
                j = cj.iloc[0]
                j_seq = j[JOINT_SEQ_FIELD]
                j_ring = j[RING_FIELD]

                if j.geometry.equals(start_joint.geometry):
                    start_seg.append((idx, j_seq))
                elif j.geometry.equals(end_joint.geometry):
                    end_seg.append((idx, j_seq))
                else:
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

        ordered = (
            spur_other_pre +
            start_seg +
            normal +
            spur_same +
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
