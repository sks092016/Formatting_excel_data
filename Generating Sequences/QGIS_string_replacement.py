from qgis.core import QgsProject, edit

# Get layer by name from QGIS layer panel
layer_name = "mahidpur_gps"
layer = QgsProject.instance().mapLayersByName(layer_name)[0]

# Define what to replace
old_str = "Baijanth"
new_str = "Baijnath"

count = 0
# Start editing the layer
with edit(layer):
    for feature in layer.getFeatures():
        update_fields = {}

        for idx, field in enumerate(layer.fields()):
            value = feature.attribute(idx)

            # Check it's a string and contains the text to replace
            if isinstance(value, str) and old_str in value:
                new_value = value.replace(old_str, new_str).strip()
                update_fields[idx] = new_value
                count = count + 1
        # Apply updates if there are any
        if update_fields:
            layer.changeAttributeValues(feature.id(), update_fields)
print(f"{count} many replacement made")