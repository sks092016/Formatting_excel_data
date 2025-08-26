from qgis.core import QgsProject, QgsFeature
import processing

# -------------------------
# USER SETTINGS
# -------------------------
points_layer_name = "Point_Data"          # Layer with your points
ring_layer_name = "OFC"              # Layer with ring info (from_gp, to_gp)
dtp_line_layer_name = "OFC"     # Layer for Extract within distance
gps_layer_name = "gps"         # GPS points for nearest neighbor
name_field = "name"                   # Field to normalize
snap_tolerance = 0.00005              # Tolerance for snapping
extract_distance = 0.0001             # Distance for extraction and clustering
k_clusters_factor = 5                  # Divide total features by this for K clusters

# -------------------------
# LOAD LAYERS
# -------------------------
points_layer = QgsProject.instance().mapLayersByName(points_layer_name)[0]
ring_layer = QgsProject.instance().mapLayersByName(ring_layer_name)[0]
dtp_line_layer = QgsProject.instance().mapLayersByName(dtp_line_layer_name)[0]
gps_layer = QgsProject.instance().mapLayersByName(gps_layer_name)[0]

# -------------------------
# 1. NAME FIELD NORMALIZATION
# -------------------------
points_layer.startEditing()
for feat in points_layer.getFeatures():
    feat[name_field] = feat[name_field].strip().upper()
    points_layer.updateFeature(feat)
points_layer.commitChanges()

# -------------------------
# 2. JOIN ATTRIBUTES BY NEAREST (from_gp, to_gp)
# -------------------------
joined_result = processing.run("qgis:joinbynearest", {
    'INPUT': points_layer,
    'INPUT_2': ring_layer,
    'FIELDS_TO_COPY': ['from_gp', 'to_gp', 'ring_code'],
    'NEIGHBORS': 1,
    'PREFIX': '',
    'OUTPUT': 'memory:'
})['OUTPUT']

# -------------------------
# 3. DELETE DUPLICATE GEOMETRIES
# -------------------------
cleaned_result = processing.run("qgis:deleteduplicategeometries", {
    'INPUT': joined_result,
    'OUTPUT': 'memory:'
})['OUTPUT']

# -------------------------
# 4. EXTRACT POINTS WITHIN DISTANCE OF DTP LINE
# -------------------------
extracted_result = processing.run("qgis:extractwithindistance", {
    'INPUT': cleaned_result,
    'DISTANCE':extract_distance,
    'OUTPUT': 'memory:'
})['OUTPUT']

# -------------------------
# 5. CLUSTERING POINTS (K-means)
# -------------------------
total_features = extracted_result.featureCount()
k_clusters = max(1, total_features // k_clusters_factor)  # Avoid 0 clusters

clustered_result = processing.run("qgis:kmeansclustering", {
    'INPUT': extracted_result,
    'NUMBER_OF_CLUSTERS': k_clusters,
    'FIELDS_TO_USE': [],
    'OUTPUT': 'memory:'
})['OUTPUT']

# -------------------------
# 6. NEAREST NEIGHBOR ANALYSIS (points to GPS)
# -------------------------
nearest_result = processing.run("qgis:joinbynearest", {
    'INPUT': clustered_result,
    'INPUT_2': gps_layer,
    'FIELDS_TO_COPY': [],  # If you want GPS fields, list them here
    'NEIGHBORS': 1,
    'PREFIX': '',
    'OUTPUT': 'memory:'
})['OUTPUT']

# -------------------------
# 7. SNAP POINTS BASED ON ENTITY TYPE
# -------------------------
snapped_result = processing.run("qgis:snappointstolayer", {
    'INPUT': nearest_result,
    'REFERENCE_LAYER': nearest_result,
    'TOLERANCE': snap_tolerance,
    'BEHAVIOR': 1,  # 0=closest vertex, 1=closest point
    'OUTPUT': 'memory:'
})['OUTPUT']

# -------------------------
# ADD FINAL LAYER TO QGIS
# -------------------------
QgsProject.instance().addMapLayer(snapped_result)

print("Workflow completed. Final snapped layer added to QGIS.")
