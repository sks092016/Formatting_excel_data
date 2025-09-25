#%%
import re
from re import split

import drawpyo
from drawpyo.diagram import Object, Edge
import os
from N2G import drawio_diagram
from numpy.ma.core import shape
ring_data = {
    "block_name":"Tirla",
    "R1" :{
       "nodes": ["Gyanpura","Himmatgarh","Sitapat","Advi","Musapura","Mafipura","Ganganagar","Tirla"],
       "no_of_child_ring":1,
       "child_ring" :[{
        "name":"R1-C1",
        "start":"between 3 and 4",
       "nodes": ["Salkanpur","Kothda","Ambapura","Chhota_Umeriya","Khandan_Bujurg"],
        "end":"between 4 and 5"
       }]
   },
}
gp_attr = {
    "style":"rounded=1;whiteSpace=wrap;html=1;strokeWidth=4;strokeColor=#FF9999;shadow=1;align=center;verticalAlign=middle;fontFamily=Georgia;fontSize=12;fontColor=default;fillColor=default;fontStyle=1;spacingBottom=0;spacingLeft=0;spacingTop=0;",
      'height':50,
      'width':50,
}
zmh_attr = {
    "style":"ellipse;whiteSpace=wrap;html=1;aspect=fixed;rounded=1;shadow=1;strokeColor=#000033;strokeWidth=4;align=center;verticalAlign=middle;fontFamily=Georgia;fontSize=12;fontColor=default;fontStyle=1;fillColor=default;spacingBottom=0;spacingLeft=0;",
    'height':50,
    'width':50,
}
gp_cr_attr = {
    "style":"rounded=1;whiteSpace=wrap;html=1;strokeWidth=4;strokeColor=#00CC66;shadow=1;align=center;verticalAlign=middle;fontFamily=Georgia;fontSize=12;fontColor=default;fillColor=default;",
    'height':50,
    'width':50,
}
block_attr = {
    "style":"shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;rounded=1;shadow=1;strokeColor=#FF0080;strokeWidth=4;align=center;verticalAlign=middle;fontFamily=Georgia;fontSize=12;fontColor=default;fontStyle=1;fillColor=default;spacingBottom=0;spacingLeft=0;spacingTop=0;spacingBottom=80;",
        'height':60,
        'width':70,
}
label_in_attr = {
    "style":"edgeLabel;resizable=0;html=1;;align=right;verticalAlign=bottom;fontFamily=Georgia;fontStyle=1;fontColor=#0000CC;rotation=-90;",
    'height':30,
    'width':125,
}
label_out_attr = {
    "style":"edgeLabel;resizable=0;html=1;;align=right;verticalAlign=bottom;fontFamily=Georgia;fontStyle=1;fontColor=#4D9900;rotation=90;",
    'height':30,
    'width':125,
}
crmh_attr = {
    'style':"ellipse;whiteSpace=wrap;html=1;aspect=fixed;rounded=1;shadow=1;dashed=0;strokeColor=#6600CC;strokeWidth=4;align=center;verticalAlign=middle;spacingLeft=0;spacingTop=0;spacingBottom=80;fontFamily=Georgia;fontSize=12;fontColor=default;fontStyle=1;fillColor=default;",
    'height': 50,
    'width': 50,
}

def styling_object(obj, style_attribute):
    obj.apply_style_string(style_attribute['style'])
    obj.height = style_attribute['height']
    obj.width = style_attribute['width']
    obj.aspect = 'fixed'
    return obj

#positioning Offset
x_offset = 150
y_gp = 300
y_zmh = 100
# === CREATE DRAWIO FILE ===
f = drawpyo.File()
f.file_path = "/Users/subhashsoni/Formatting_excel_data/Generating_FTP/"
# f.file_path = "C:\\Users\SubhashSoni\PycharmProjects\Formatting_excel_data\Generating_FTP"
f.file_name = "ring_with_child.drawio"
page = drawpyo.Page(file=f)
objects = {}
edges = []
#
diagram = drawio_diagram()
diagram.add_diagram("Page-1")
# === 1. Block Node ===
block = Object(page=page, value=ring_data["block_name"].capitalize())
objects["block"] = styling_object(block, block_attr)
block.center_position = (-x_offset, 0)
block_zmh = Object(page=page, value='zmh_0')
objects["zmh_0"] = styling_object(block_zmh, zmh_attr)
block_zmh.center_position = (0,0)

# === 2. Main Ring GPs and ZMHs ===
# We'll place them horizontally like a chain

top_nodes = len(ring_data["R1"]["nodes"])//2
bottom_nodes = len(ring_data["R1"]["nodes"]) - top_nodes
reversing_count =1

for g in ring_data["R1"]["nodes"]:
    offset_multiplier = ring_data["R1"]["nodes"].index(g)+1
    gp_id = g.lower()
    zmh_id = f"zmh_{offset_multiplier}"

    gp = Object(page=page, value=g.capitalize(), id=gp_id)
    objects[gp_id] = styling_object(gp, gp_attr)

    zmh = Object(page=page, value=f"zmh-{offset_multiplier}", id=zmh_id)
    objects[zmh_id] = styling_object(zmh, zmh_attr)

    in_label = Object(page=page, value='MC(IN):R1(1-6)<==>GPAC1:R1(1-6)', id=f'{zmh_id}-in')
    objects[f'{zmh_id}-in'] = styling_object(in_label, label_in_attr)

    out_label = Object(page=page, value="MC(OUT):R1(1-6)<==>GPAC1:R1(7-12)", id=f'{zmh_id}-out')
    objects[f'{zmh_id}-out'] = styling_object(out_label, label_out_attr)

    mc = Edge(page=page, source=zmh, target=gp)

    if offset_multiplier <= top_nodes:
        gp.center_position = (offset_multiplier* x_offset, -y_gp)
        gp.apply_style_string(f"{gp_attr['style']};spacingBottom=80;")
        zmh.center_position = (offset_multiplier* x_offset, -y_zmh)
        in_label.center_position = (zmh.center_position[0]-35, (zmh.center_position[1]+gp.center_position[1])/2)
        out_label.center_position = (zmh.center_position[0]+25, (zmh.center_position[1]+gp.center_position[1])/2)
    else:
       gp.center_position = ((offset_multiplier-reversing_count)* x_offset, y_gp)
       gp.apply_style_string(f"{gp_attr['style']};spacingTop=80;")
       zmh.center_position = ((offset_multiplier-reversing_count)* x_offset, y_zmh)
       in_label.center_position = (zmh.center_position[0]+25, (zmh.center_position[1]+gp.center_position[1])/2)
       out_label.center_position = (zmh.center_position[0]-35, (zmh.center_position[1]+gp.center_position[1])/2)
       reversing_count += 2

for n in range(0, len(ring_data["R1"]["nodes"])+1):
    if n < len(ring_data["R1"]["nodes"]):
        mc = Edge(page=page, source=objects[f'zmh_{n}'], target=objects[f'zmh_{n+1}'], label="Main Cable")
    else:
        mc = Edge(page=page, source=objects[f'zmh_{n}'], target=objects[f'zmh_0'], label="Main Cable", src_label="Main Cable", trgt_label="Main Cable")

#---checking associated -- child ring
def find_start_position(ring, ring_data, objects):
    if 'between' in ring['start']:
        text = ring['start']
        match = re.search(r'between (\d+) and (\d+)', text)
        node1, node2 = int(match.group(1)), int(match.group(2))
        main_ring = ring["name"].split("-")[0]
        start_node_position = objects[f"zmh_{node1}"].center_position
        crmh_start = (start_node_position[0]+x_offset, start_node_position[1])
        return crmh_start
if ring_data["R1"]["no_of_child_ring"] > 0:
    for ring in ring_data["R1"]["child_ring"]:
        crmh_start_position = find_start_position(ring, ring_data, objects)
        crmh = Object(page=page, value='crmh_start', id="crmh_start")
        crmh.center_position =  crmh_start_position
        objects["crmh_start"] = styling_object(crmh, crmh_attr)

#
# # Connect Block → first GP
# edges.append(("block", "gp1", "Start"))
#
# # Connect GPs in a ring
# for i in range(1, MAIN_RING_NODES):
#     edges.append((f"gp{i}", f"gp{i+1}", f"G{i}-G{i+1}"))
# edges.append((f"gp{MAIN_RING_NODES}", "block", "Return"))
#
# # === 3. Child Ring ===
# # Child ring starts at a CRMH between ZMH2 and ZMH3, ends at another CRMH between ZMH5 and ZMH6
# crmh_start = Object(page=page, value="CRMH-Start")
# crmh_start.position = (2.5 * x_offset, y_zmh - 70)
# crmh_start.apply_style_string("shape=diamond;fillColor=#ff6666;strokeColor=#660000;")
# objects["crmh_start"] = crmh_start
#
# crmh_end = Object(page=page, value="CRMH-End")
# crmh_end.position = (5.5 * x_offset, y_zmh - 70)
# crmh_end.apply_style_string("shape=diamond;fillColor=#ff6666;strokeColor=#660000;")
# objects["crmh_end"] = crmh_end
#
# # Child ring nodes (cGPs)
# y_child = -100
# for j in range(1, CHILD_RING_NODES + 1):
#     cgp_id = f"cgp{j}"
#     cgp = Object(page=page, value=f"C-GP-{j}")
#     cgp.position = (2.5 * x_offset + j * 70, y_child)
#     cgp.apply_style_string("shape=ellipse;fillColor=#66ff99;strokeColor=#006633;")
#     objects[cgp_id] = cgp
#
# # Edges for child ring
# edges.append(("crmh_start", "cgp1", "C-Start"))
# for j in range(1, CHILD_RING_NODES):
#     edges.append((f"cgp{j}", f"cgp{j+1}", f"C{j}-C{j+1}"))
# edges.append((f"cgp{CHILD_RING_NODES}", "crmh_end", "C-End"))
#
# # === 4. Draw all edges ===
# # for src, tgt, lbl in edges:
# #     if src in objects and tgt in objects:
# #         line = Edge(page=page,
# #                     points=[(objects[src], 0.5, 0.5),
# #                             (objects[tgt], 0.5, 0.5)],
# #                     stroke_color="#000000",
# #                     stroke_width=2)
# #         line.content = lbl
#
# # === WRITE FILE ===

f.write()
print("Diagram saved to ring_with_child.drawio")