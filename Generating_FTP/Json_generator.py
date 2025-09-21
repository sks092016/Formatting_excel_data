import json

def midpoint(pos1, pos2):
    return {"x": (pos1["x"]+pos2["x"])/2, "y": (pos1["y"]+pos2["y"])/2}

def generate_with_crmh(n_main, spacing=100, child_rings=None, node_names=None):
    """
    n_main: number of main GPs
    child_rings: list of dicts [
       {"start": ("zmh", idx) or ("between", idx1, idx2),
        "end": ("zmh", idx) or ("between", idx1, idx2),
        "n_child": int}
    ]
    """
    nodes, edges, zmh_positions = [], [], {}

    # --- Block node ---
    nodes.append({"data": {"id": "block", "label": node_names["main_ring"][0], "type": "block"}, "position": {"x": -spacing, "y": 0}})
    nodes.append({"data": {"id": "zmh_block", "label": "ZMH-BLOCK", "type": "zmh"}, "position": {"x": 0, "y": 0}})

    # --- Main Ring (simple rectangle arrangement) ---
    top_count = (n_main + 1)//2
    bottom_count = n_main - top_count

    for i in range(top_count):
        gp_id, zmh_id = f"{node_names['main_ring'][i + 1]}", f"zmh_{i+1}"
        x = (i+1)*spacing
        nodes.append({"data": {"id": gp_id, "label": f"{gp_id.upper()}", "type": "gp"}, "position": {"x": x, "y": spacing}})
        zmh_pos = {"x": x, "y": spacing//2}
        nodes.append({"data": {"id": zmh_id, "label": f"ZMH-{i+1}", "type": "zmh"}, "position": zmh_pos})
        zmh_positions[i+1] = zmh_pos

    for i in range(bottom_count):
        idx = top_count + i
        gp_id, zmh_id = f"{node_names['main_ring'][idx]}", f"zmh_{idx}"
        x = (i+1)*spacing
        nodes.append({"data": {"id": gp_id, "label": f"{gp_id.upper()}", "type": "gp"}, "position": {"x": x, "y": -spacing}})
        zmh_pos = {"x": x, "y": -spacing//2}
        nodes.append({"data": {"id": zmh_id, "label": f"ZMH-{idx}", "type": "zmh"}, "position": zmh_pos})
        zmh_positions[idx] = zmh_pos

    # # --- Main ring edges ---
    # for i in range(1, n_main):
    #     edges.append({"data": {"id": f"e_gp{i}_gp{i+1}", "source": f"gp{i}", "target": f"gp{i+1}"}})
    # edges.append({"data": {"id": f"e_gp{n_main}_block", "source": f"gp{n_main}", "target": "block"}})
    # edges.insert(0, {"data": {"id": "e_block_gp1", "source": "block", "target": "gp1"}})
    #
    # for i in range(1, n_main+1):
    #     edges.append({"data": {"id": f"e_gp{i}_zmh{i}", "source": f"gp{i}", "target": f"zmh_gp{i}"}})
    #
    # # --- Child rings with CRMHs ---
    # if child_rings:
    #     cr_idx = 1
    #     for cr in child_rings:
    #         n_child = cr["n_child"]
    #
    #         # --- Place CRMH start ---
    #         if cr["start"][0] == "zmh":
    #             zmh_id = cr["start"][1]
    #             pos = zmh_positions[zmh_id]
    #         else:  # ("between", idx1, idx2)
    #             pos = midpoint(zmh_positions[cr["start"][1]], zmh_positions[cr["start"][2]])
    #         start_id = f"crmh{cr_idx}_start"
    #         nodes.append({"data": {"id": start_id, "label": f"CRMH-{cr_idx}S", "type": "crmh"}, "position": pos})
    #
    #         # --- Place CRMH end ---
    #         if cr["end"][0] == "zmh":
    #             zmh_id = cr["end"][1]
    #             pos = zmh_positions[zmh_id]
    #         else:
    #             pos = midpoint(zmh_positions[cr["end"][1]], zmh_positions[cr["end"][2]])
    #         end_id = f"crmh{cr_idx}_end"
    #         nodes.append({"data": {"id": end_id, "label": f"CRMH-{cr_idx}E", "type": "crmh"}, "position": pos})
    #
    #         # --- Place child nodes in a small oval between start and end ---
    #         for i in range(n_child):
    #             cid, zid = f"cgp{cr_idx}_{i+1}", f"zmh_cgp{cr_idx}_{i+1}"
    #             cx = (i+1)*spacing + cr_idx*spacing
    #             cy = (spacing if i%2==0 else -spacing)
    #             nodes.append({"data": {"id": cid, "label": f"CR{cr_idx}-GP-{i+1}", "type": "c_gp"},
    #                           "position": {"x": cx, "y": cy}})
    #             nodes.append({"data": {"id": zid, "label": f"CR{cr_idx}-ZMH-{i+1}", "type": "zmh"},
    #                           "position": {"x": cx, "y": cy//2}})
    #
    #         # --- Connect child ring edges ---
    #         edges.append({"data": {"id": f"e_cr{cr_idx}_start", "source": start_id, "target": f"cgp{cr_idx}_1"}})
    #         for i in range(1, n_child):
    #             edges.append({"data": {"id": f"e_cr{cr_idx}_{i}_{i+1}", "source": f"cgp{cr_idx}_{i}", "target": f"cgp{cr_idx}_{i+1}"}})
    #         edges.append({"data": {"id": f"e_cr{cr_idx}_end", "source": f"cgp{cr_idx}_{n_child}", "target": end_id}})
    #         cr_idx += 1
    return {"nodes": nodes} #{"nodes": nodes, "edges": edges}



nodes_names = {
"main_ring":["Tirla_Block","Gyanpura","Himmatgarh","Sitapat","Padlaya","Dilavra","Advi","Musapura","Mafipura","Ganganagar","Tirla"],
"child_rings":["Bagadiya","Salkanpur","Kothda","Chhota_Umeriya","Khandan_Bujurg"]
}
# Example with CRMHs
layout = generate_with_crmh(
    len(nodes_names["main_ring"]),
    spacing=120,
    child_rings=[
        {"start": ("between", 2, 3), "end": ("zmh", 5), "n_child": 5},  # start between ZMH2-3, end at ZMH5
        {"start": ("zmh", 1), "end": ("between", 6, 7), "n_child": 4}   # start at ZMH1, end between ZMH6-7
    ],
    node_names=nodes_names
)

with open("crmh_layout.json", "w") as f:
    json.dump(layout, f, indent=2)
