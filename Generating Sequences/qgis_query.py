layer = iface.activeLayer()   # Make sure your layer is selected
if not layer.isEditable():
    layer.startEditing()

for feature in layer.getFeatures():
    if feature["span_name"] == "BANDHWABADA TO DUDHI":
        fid = feature.id()
        # from_gp = feature["from_gp_na"]
        # to_gp = feature["to_gp_name"]
        #
        # # swap
        # new_from = to_gp
        new_from = "T-POINT PACHGAON"
        # new_to = from_gp
        new_to = "DUDHI"
        #
        # # build new span name
        new_span = f"{new_from} TO {new_to}"


        layer.changeAttributeValue(fid, layer.fields().indexFromName("from_gp_na"), new_from)
        layer.changeAttributeValue(fid, layer.fields().indexFromName("to_gp_name"), new_to)
        layer.changeAttributeValue(fid, layer.fields().indexFromName("span_name"), new_span)

layer.commitChanges()
print("Update complete ✅")
