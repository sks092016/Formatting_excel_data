from qgis.core import QgsProject
blockName ='Gandhwani'
layer_name = f'OFC_New_{blockName}-1_Seg_Span_Seq'
from_gp_column = 'from_gp_na'
to_gp_column = 'to_gp_name'
layer = QgsProject.instance().mapLayersByName(layer_name)[0]
layer.startEditing()

# Make sure fields exist
count = 0
for f in layer.getFeatures():
    span = f["span_name"]
    if span and "TO" in span.upper():
        parts = [p.strip() for p in span.upper().split("TO")]
        if len(parts) == 2:
            count += 1
            f[from_gp_column] = parts[0]
            f[to_gp_column] = parts[1]
            layer.updateFeature(f)
        else:
            print(f'{f["OBJECTID"]} not updated')
layer.commitChanges()
print(f"✅ Updated from_gp and to_gp columns, total {count} records updated")
