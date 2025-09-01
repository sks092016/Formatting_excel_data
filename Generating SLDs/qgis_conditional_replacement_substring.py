from qgis.core import QgsProject, edit

# --- SETTINGS ---
layer_name = "OFC_NEW"  # Name of the layer in QGIS
check_field = "span_name"
update_field = "span_name"
"""{'extra_in_spans': {'NAKHLAULI', 'NARSINGH GARH', 'JAHMHOURA', 'ATER BLOCK', 'KACHIPURA', 'GODHUPURA'}, 
 'unused_gps': {'NARSING GARH', 'GOHDUPURA', 'JAMHOURA', 'BADAPURA', 'KACHHPURA'}}"""

replacement_map = {
'BADPURA TO NARIPURA':'BADAPURA TO NARIPURA',
'GADHA TO BADPURA':'GADHA TO BADAPURA'
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
