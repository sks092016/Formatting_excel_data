layer = iface.activeLayer()

if layer is None or layer.geometryType() != QgsWkbTypes.LineGeometry:
    print("Select a line layer first.")
else:
    print("Processing...")

    endpoint_index = {}  # key = (x,y), value = list of feature IDs

    for f in layer.getFeatures():
        geom = f.geometry()
        if geom.isEmpty():
            continue
        
        # Handle multipart & single part
        for part in geom.asMultiPolyline() if geom.isMultipart() else [geom.asPolyline()]:
            if len(part) < 2:
                continue
            
            start_pt = part[0]
            end_pt = part[-1]
            
            for pt in (start_pt, end_pt):
                key = (round(pt.x(), 5), round(pt.y(), 5))  # rounded for matching
                endpoint_index.setdefault(key, []).append(f.id())

    # Find dangling endpoints → only one line endpoint exists at that coordinate
    dangling_feature_ids = set()
    for pt, lst in endpoint_index.items():
        if len(lst) == 1:
            dangling_feature_ids.add(lst[0])

    # Select features on map
    layer.selectByIds(list(dangling_feature_ids))

    print(f"Selected {len(dangling_feature_ids)} line(s) with dangling endpoints.")
