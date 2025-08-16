from qgis.core import QgsProject

# --- SETTINGS ---
layer_name = "OFC_NEW"  # Name of the layer in QGIS
check_field = "span_name"        # Field whose value you check
update_field = "span_name"    # Field whose value you update

# Mapping: if category == key, replace description with value
replacement_map = {
    'MAHRSHPUR':'MAHESHPUR',
    "TETH" : "THEH",
    "SATAWADAKHURD" : "SATANWADAKHURD"
    
}
count = 0 
# --- SCRIPT ---
layer = QgsProject.instance().mapLayersByName(layer_name)[0]
if not layer:
    raise Exception(f"Layer '{layer_name}' not found!")

with edit(layer):
    for feature in layer.getFeatures():
        check_value = feature[check_field]
        if check_value in replacement_map:
            new_value = replacement_map[check_value]
            layer.changeAttributeValue(feature.id(),
                                       layer.fields().indexFromName(update_field),
                                       new_value)
            count += 1 

print(f"✅{count} Replacement completed successfully!")
