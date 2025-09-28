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
       },
           {
               "name": "R1-C2",
               "start": "between 4 and 5",
               "nodes": ["Mohanpur", "Mawdipura", "Bhutibawdi", "Chakalya"],
               "end": "7"
           }
       ]
   },
}
gp_attr = {
    "style":"rounded=1;whiteSpace=wrap;html=1;strokeWidth=4;strokeColor=#FF9999;shadow=1;align=center;verticalAlign=middle;fontFamily=Georgia;fontSize=8;fontColor=default;fillColor=default;fontStyle=1;spacingBottom=0;spacingLeft=0;spacingTop=0;fillColor=none;",
      'height':20,
      'width':20,
}
zmh_attr = {
    "style":"ellipse;whiteSpace=wrap;html=1;aspect=fixed;rounded=1;shadow=1;strokeColor=#000033;strokeWidth=2;align=center;verticalAlign=middle;fontFamily=Georgia;fontSize=8;fontColor=default;fontStyle=1;fillColor=default;spacingBottom=0;spacingLeft=0;fillColor=none;",
    'height':20,
    'width':20,
}
gp_cr_attr = {
    "style":"rounded=1;whiteSpace=wrap;html=1;strokeWidth=4;strokeColor=#00CC66;shadow=1;align=center;verticalAlign=middle;fontFamily=Georgia;fontSize=8;fontColor=default;fillColor=default;",
    'height':20,
    'width':20,
}
block_attr = {
    "style":"shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;rounded=1;shadow=1;strokeColor=#FF0080;strokeWidth=4;align=center;verticalAlign=middle;fontFamily=Georgia;fontSize=8;fontColor=default;fontStyle=1;fillColor=default;spacingBottom=0;spacingLeft=0;spacingTop=0;spacingBottom=80;",
        'height':20,
        'width':20,
}
label_in_attr = {
    "style":"edgeLabel;resizable=0;html=1;align=right;verticalAlign=bottom;fontFamily=Georgia;fontStyle=1;fontColor=#0000CC;rotation=-90;fontSize=7;fillColor=none;labelBackgroundColor=none;",
    'height':20,
    'width':65,
}
label_out_attr = {
    "style":"edgeLabel;resizable=0;html=1;align=right;verticalAlign=bottom;fontFamily=Georgia;fontStyle=1;fontColor=#4D9900;rotation=90;fontSize=7;fillColor=none;labelBackgroundColor=none;",
    'height':20,
    'width':65,
}
crmh_attr = {
    'style':"ellipse;whiteSpace=wrap;html=1;aspect=fixed;rounded=1;shadow=1;dashed=0;strokeColor=#6600CC;strokeWidth=2;align=center;verticalAlign=middle;spacingLeft=0;spacingTop=0;spacingBottom=40;fontFamily=Georgia;fontSize=8;fontColor=default;fontStyle=1;fillColor=none;",
    'height': 20,
    'width': 20,
}

def styling_object(obj, style_attribute):
    obj.apply_style_string(style_attribute['style'])
    obj.height = style_attribute['height']
    obj.width = style_attribute['width']
    obj.aspect = 'fixed'
    return obj

#positioning Offset
x_offset = 100
y_gp = 150
y_zmh = 50
initial_position = (50,400)
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
block.center_position = (initial_position[0]-30,initial_position[1])
block_zmh = Object(page=page, value='zmh0')
objects["zmh0"] = styling_object(block_zmh, zmh_attr)
block_zmh.center_position = initial_position

# === 2. Main Ring GPs and ZMHs ===
# We'll place them horizontally like a chain

top_nodes = len(ring_data["R1"]["nodes"])//2
bottom_nodes = len(ring_data["R1"]["nodes"]) - top_nodes
reversing_count =1

for g in ring_data["R1"]["nodes"]:
    offset_multiplier = ring_data["R1"]["nodes"].index(g)+1
    gp_id = g.lower()
    zmh_id = f"zmh{offset_multiplier}"

    gp = Object(page=page, value=g.capitalize(), id=gp_id)
    objects[gp_id] = styling_object(gp, gp_attr)

    zmh = Object(page=page, value=f"zmh-{offset_multiplier}", id=zmh_id)
    objects[zmh_id] = styling_object(zmh, zmh_attr)

    in_label = Object(page=page, value='MC(IN):R1(1-6) GPAC:R1(1-6)', id=f'{zmh_id}-in')
    objects[f'{zmh_id}-in'] = styling_object(in_label, label_in_attr)

    out_label = Object(page=page, value="MC(OUT):R1(1-6) GPAC:R1(7-12)", id=f'{zmh_id}-out')
    objects[f'{zmh_id}-out'] = styling_object(out_label, label_out_attr)

    gpac = Edge(page=page, source=zmh, target=gp)
    gpac.strokeColor = '#F88024'

    if offset_multiplier <= top_nodes:
        gp.center_position = (    initial_position[0]+offset_multiplier* x_offset, initial_position[1]-y_gp)
        gp.apply_style_string(f"{gp_attr['style']};spacingBottom=40;")
        zmh.center_position = (initial_position[0]+offset_multiplier* x_offset, initial_position[1]-y_zmh)
        zmh.apply_style_string(f"{zmh_attr['style']};spacingTop=40;")
        in_label.center_position = (zmh.center_position[0]-10, (zmh.center_position[1]+gp.center_position[1])/2)
        out_label.center_position = (zmh.center_position[0]+10, (zmh.center_position[1]+gp.center_position[1])/2)
    else:
       gp.center_position = (initial_position[0]+(offset_multiplier-reversing_count)* x_offset, initial_position[1]+y_gp)
       gp.apply_style_string(f"{gp_attr['style']};spacingTop=40;")
       zmh.center_position = (initial_position[0]+(offset_multiplier-reversing_count)* x_offset, initial_position[1]+y_zmh)
       zmh.apply_style_string(f"{zmh_attr['style']};spacingBottom=40;")
       in_label.center_position = (zmh.center_position[0]+10, (zmh.center_position[1]+gp.center_position[1])/2)
       out_label.center_position = (zmh.center_position[0]-10, (zmh.center_position[1]+gp.center_position[1])/2)
       reversing_count += 2

for n in range(0, len(ring_data["R1"]["nodes"])+1):
    if n < len(ring_data["R1"]["nodes"]):
        mc = Edge(page=page, source=objects[f'zmh{n}'], target=objects[f'zmh{n+1}'], label="MC")
        mc.text_format.fontSize = 8
        mc.text_format.fontFamily = "georgia"
        mc.text_format.fontColor = "#FF0000"
        mc.text_format.fontColor = 1
        mc.strokeColor = '#249DF8'
    else:
        mc = Edge(page=page, source=objects[f'zmh{n}'], target=objects[f'zmh0'], label="MC")
        mc.text_format.fontSize = 8
        mc.text_format.fontFamily = "georgia"
        mc.text_format.fontColor = "#FF0000"
        mc.text_format.fontColor = 1
        mc.strokeColor = '#249DF8'

#---checking associated -- child ring
def find_crmh_position(ring, objects, location):
    if 'between' in ring[location]:
        text = ring[location]
        match = re.search(r'between (\d+) and (\d+)', text)
        node1, node2 = int(match.group(1)), int(match.group(2))
        main_ring = ring["name"].split("-")[0]
        start_node_position = objects[f"zmh{node1}"].center_position
        print(f"Starting node {node1} is at {start_node_position}")
        end_node_position = objects[f"zmh{node2}"].center_position
        print(f"Starting node {node2} is at {end_node_position}")
        if start_node_position[1] == end_node_position[1]:
            if start_node_position[0] < end_node_position[0]:
                x_off =  end_node_position[0] - start_node_position[0]
                crmh_position = (start_node_position[0] + x_off/2, start_node_position[1])
            else:
                x_off = start_node_position[0] - end_node_position[0]
                crmh_position = (end_node_position[0] + x_off/2, start_node_position[1])
        if start_node_position[0] == end_node_position[0]:
            y_off =  end_node_position[1] - start_node_position[1]
            crmh_position = (end_node_position[0], start_node_position[1]+y_off/2)
        return crmh_position, node1
    else:
        crmh_position = objects[f"zmh{ring[location]}"].center_position
        return crmh_position, ring[location]


if ring_data["R1"]["no_of_child_ring"] > 0:
    for ring in ring_data["R1"]["child_ring"]:
        crmh_st= Object(page=page, value='crmh_start', id=f"{ring['name']}_start")
        objects[f"{ring['name']}_start"] = styling_object(crmh_st, crmh_attr)
        crmh_st.center_position, n1 = find_crmh_position(ring, objects, 'start')

        crmh_ed = Object(page=page, value='crmh_end', id=f"{ring['name']}_end")
        objects[f"{ring['name']}_end"] = styling_object(crmh_ed, crmh_attr)
        crmh_ed.center_position, n2 = find_crmh_position(ring, objects, 'end')

        if int(n1) < top_nodes:
            initial_cr_position = (objects[f"zmh{top_nodes}"].center_position[0]+150, 
                                                    objects[f"zmh{top_nodes}"].center_position[1]-150)
        else:
            initial_cr_position = (objects[f"zmh{top_nodes+1}"].center_position[0] + 150,
                                                    objects[f"zmh{top_nodes+1}"].center_position[1] + 150)
        top_nodes_cr =  len(ring["nodes"])//2
        reversing_count = 1
        for g in ring["nodes"]:
            offset_multiplier = ring["nodes"].index(g) + 1
            gp_id = g.lower()
            zmh_id = f"zmh{offset_multiplier}-{ring['name']}"

            gpcr = Object(page=page, value=g.capitalize(), id=gp_id)
            objects[gp_id] = styling_object(gpcr, gp_attr)

            zmhcr = Object(page=page, value=f"zmh-{offset_multiplier}", id=zmh_id)
            objects[zmh_id] = styling_object(zmhcr, zmh_attr)

            in_label = Object(page=page, value='MC(IN):R1(1-6) GPAC:R1(1-6)', id=f'{zmh_id}-in')
            objects[f'{zmh_id}-in'] = styling_object(in_label, label_in_attr)

            out_label = Object(page=page, value="MC(OUT):R1(1-6) GPAC:R1(7-12)", id=f'{zmh_id}-out')
            objects[f'{zmh_id}-out'] = styling_object(out_label, label_out_attr)

            gpac = Edge(page=page, source=zmhcr, target=gpcr)
            gpac.strokeColor = '#F88024'

            if offset_multiplier <= top_nodes_cr:
                gpcr.center_position = (initial_cr_position[0] + offset_multiplier * x_offset, initial_cr_position[1] - y_gp)
                gpcr.apply_style_string(f"{gp_attr['style']};spacingBottom=40;")
                zmhcr.center_position = (initial_cr_position[0] + offset_multiplier * x_offset, initial_cr_position[1] - y_zmh)
                zmhcr.apply_style_string(f"{zmh_attr['style']};spacingTop=40;")
                in_label.center_position = (zmhcr.center_position[0] - 10,
                                            (zmhcr.center_position[1] + gpcr.center_position[1]) / 2)
                out_label.center_position = (zmhcr.center_position[0] + 10,
                                             (zmhcr.center_position[1] + gpcr.center_position[1]) / 2)
            else:
                gpcr.center_position = (initial_cr_position[0] + (offset_multiplier - reversing_count) * x_offset,
                                      initial_cr_position[1] + y_gp)
                gpcr.apply_style_string(f"{gp_attr['style']};spacingTop=40;")
                zmhcr.center_position = (initial_cr_position[0] + (offset_multiplier - reversing_count) * x_offset,
                                       initial_cr_position[1] + y_zmh)
                zmhcr.apply_style_string(f"{zmh_attr['style']};spacingBottom=40;")
                in_label.center_position = (zmhcr.center_position[0] + 10,
                                            (zmhcr.center_position[1] + gpcr.center_position[1]) / 2)
                out_label.center_position = (zmhcr.center_position[0] - 10,
                                             (zmhcr.center_position[1] + gpcr.center_position[1]) / 2)
                reversing_count += 2
        edge = Edge(page=page, source=objects[f"{ring['name']}_start"], target=objects[f'zmh1-{ring["name"]}'],label="MC(In)R3(13-18)-CRMC(In)R1(1-6)")
        edge.text_format.fontSize = 8
        edge.text_format.fontFamily = "georgia"
        edge.text_format.fontColor = '#DD0303'
        edge.strokeColor = '#59AC77'
        edge.strokeWidth = 2
        for n in range(1, len(ring["nodes"]) +1):
            if n < len(ring["nodes"]):
                mc = Edge(page=page, source=objects[f'zmh{n}-{ring["name"]}'], target=objects[f'zmh{n + 1}-{ring["name"]}'], label="CRMC")
                mc.text_format.fontSize = 8
                mc.text_format.fontFamily = "georgia"
                mc.text_format.fontColor = "#249DF8"
                mc.strokeColor = '#249DF8'
            else:
                mc = Edge(page=page, source=objects[f'zmh{n}-{ring["name"]}'], target=objects[f"{ring['name']}_end"], label="CRMC(Out)R1(1-6)-MC(Out)R1(13-18)")
                mc.text_format.fontSize = 8
                mc.text_format.fontFamily = "georgia"
                mc.text_format.fontColor = '#DD0303'
                mc.strokeColor = '#59AC77'
                mc.strokeWidth = 2

f.write()
print("Diagram saved to ring_with_child.drawio")