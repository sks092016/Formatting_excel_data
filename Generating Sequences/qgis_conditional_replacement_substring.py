from qgis.core import QgsProject, edit

# --- SETTINGS ---
layer_name = "OFC_NEW"  # Name of the layer in QGIS
check_field = "span_name"
update_field = "span_name"

# t-point corrections
'''
't point':'t-point',
't- point':'t-point',
't -point':'t-point',
't - point':'t-point',
'''

replacement_map = {
 'RASHILPUR':'RASILPUR',
 'CHURHAELA':'CHURHELA',
 'RAITHOURAKALANN':'RAITHOURAKALAN'
}
count = 0 

# --- SCRIPT ---
layer = QgsProject.instance().mapLayersByName(layer_name)[0]
if not layer:
    raise Exception(f"Layer '{layer_name}' not found!")

with edit(layer):
    for feature in layer.getFeatures():
        check_value = feature[check_field]
        if not check_value:
            continue
        for key, value in replacement_map.items():
            if key in check_value:  # case-sensitive; use lower() if needed
                new_value = check_value.replace(key, value)
                count += 1
                layer.changeAttributeValue(
                    feature.id(),
                    layer.fields().indexFromName(update_field),
                    new_value
                )
            
print(f"✅ {count} replacements completed successfully!")
