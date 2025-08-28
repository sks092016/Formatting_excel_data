from qgis.core import QgsProject

# --- SETTINGS ---
layer_name = "OFC_NEW2"  # Name of the layer in QGIS
check_field = "span_name"        # Field whose value you check
update_field = "span_name"    # Field whose value you update

# Mapping: if category == key, replace description with value
replacement_map = {
  'To': 'TO',
}
count = 0 
# --- SCRIPT ---
layer = QgsProject.instance().mapLayersByName(layer_name)[0]
if not layer:
    raise Exception(f"Layer '{layer_name}' not found!")

with edit(layer):
    for feature in layer.getFeatures():
        check_value = feature[check_field]
        for key, value in replacement_map.items():
            if key in check_value:
                new_value = check_value.replace(key, value)
                count += 1 
                layer.changeAttributeValue(feature.id(),layer.fields().indexFromName(update_field),new_value)
            
print(f"✅{count} Replacement completed successfully!")
