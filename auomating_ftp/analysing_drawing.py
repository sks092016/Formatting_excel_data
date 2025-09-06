# Install the library first:
# pip install ezdxf

import ezdxf

# Load the DWG file
doc = ezdxf.readfile("input/Koyalibeda(Pakhanjore)/KOYALIBEDA(PAKHANJORE) BLUE RING.dwg")
msp = doc.modelspace()

print("========== STEP 1: Basic Drawing Info ==========")
print("Filename:", doc.filename)
print("DWG/DXF Version:", doc.acad_release)
print("Number of entities in Modelspace:", len(msp))

print("\n========== STEP 2: List Layers ==========")
for layer in doc.layers:
    print(f"Layer: {layer.dxf.name}, Color: {layer.color}, Linetype: {layer.dxf.linetype}")

print("\n========== STEP 3: Extract Text (GP/SC names) ==========")
for entity in msp.query("TEXT MTEXT"):
    if entity.dxftype() == "TEXT":
        print(f"TEXT: '{entity.dxf.text}' at {entity.dxf.insert} on layer {entity.dxf.layer}")
    elif entity.dxftype() == "MTEXT":
        print(f"MTEXT: '{entity.text}' at {entity.dxf.insert} on layer {entity.dxf.layer}")

print("\n========== STEP 4: Extract Lines ==========")
for line in msp.query("LINE"):
    print(f"LINE from {line.dxf.start} to {line.dxf.end} on layer {line.dxf.layer}")

print("\n========== STEP 5: Extract Polylines ==========")
for pline in msp.query("LWPOLYLINE"):
    points = list(pline.get_points())
    print(f"Polyline with {len(points)} vertices on layer {pline.dxf.layer}: {points}")

print("\n========== STEP 6: Extract Blocks ==========")
for block in doc.blocks:
    print(f"Block name: {block.name}, contains {len(block)} entities")
