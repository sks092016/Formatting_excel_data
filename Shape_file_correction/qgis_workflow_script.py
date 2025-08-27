from qgis.core import QgsProject, QgsFeature
import processing
from qgis.core import QgsField
from PyQt5.QtCore import QVariant
import processing
from qgis.core import QgsVectorFileWriter
from qgis.core import QgsProject, QgsVectorFileWriter, QgsFeature, QgsGeometry
import os
# -------------------------
# USER SETTINGS
# -------------------------
points_layer_name = "Point_Data"          # Layer with your points
ring_layer_name = "OFC"              # Layer with ring info (from_gp, to_gp)
dtp_line_layer_name = "OFC"     # Layer for Extract within distance
gps_layer_name = "GP"         # GPS points for nearest neighbor
name_field = "name"                   # Field to normalize
snap_tolerance = 0.00005              # Tolerance for snapping
extract_distance = 0.00009             # Distance for extraction and clustering
k_clusters_factor = 5                  # Divide total features by this for K clusters
# -------------------------
# LOAD LAYERS
# -------------------------
points_layer = QgsProject.instance().mapLayersByName(points_layer_name)[0]
ring_layer = QgsProject.instance().mapLayersByName(ring_layer_name)[0]
dtp_line_layer = QgsProject.instance().mapLayersByName(dtp_line_layer_name)[0]
gps_layer = QgsProject.instance().mapLayersByName(gps_layer_name)[0]
# -------------------------
# 2. JOIN ATTRIBUTES BY NEAREST (from_gp, to_gp)
# -------------------------
joined_result = processing.run("native:joinbynearest", {
    'INPUT':points_layer,
    'INPUT_2':ring_layer,
    'FIELDS_TO_COPY':['ring_code','fromdp','todp'],
    'DISCARD_NONMATCHING':False,
    'PREFIX':'',
    'NEIGHBORS':1,
    'MAX_DISTANCE':None,
    'OUTPUT':'TEMPORARY_OUTPUT'})["OUTPUT"]
# -------------------------
# 3. DELETE DUPLICATE GEOMETRIES
# -------------------------
cleaned_result = processing.run("native:deleteduplicategeometries", {
    'INPUT':joined_result,
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
# -------------------------
# 4. EXTRACT POINTS WITHIN DISTANCE OF DTP LINE
# -------------------------
extracted_result = processing.run("qgis:extractwithindistance", {
    'INPUT': cleaned_result,
    'REFERENCE':dtp_line_layer,
    'DISTANCE':extract_distance,
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
# -------------------------
# 5. CLUSTERING POINTS (K-means)
# -------------------------
clustered_result = processing.run("native:kmeansclustering", {
    'INPUT':extracted_result,
    'CLUSTERS':1000,
    'FIELD_NAME':'CLUSTER_ID',
    'SIZE_FIELD_NAME':'CLUSTER_SIZE',
    'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']

cluster_layer = QgsProject.instance().addMapLayer(clustered_result)
cluster_layer.startEditing()
field_name = "span_name"
if field_name not in [f.name() for f in cluster_layer.fields()]:
    cluster_layer.dataProvider().addAttributes([QgsField(field_name, QVariant.String)])
    cluster_layer.updateFields()
for f in cluster_layer.getFeatures():
    f[field_name] = f"{f['fromdp'].upper()} TO {f['todp'].upper()}"
    cluster_layer.updateFeature(f)
cluster_layer.commitChanges()

# -------------------------
# USER INPUTS
# -------------------------
# cluster_layer, gps_layer
cluster_layer.startEditing()
field_name1 = "from_gp_distance"
field_name2 = "to_gp_distance"
cluster_layer.dataProvider().addAttributes([QgsField(field_name1, QVariant.String)])
cluster_layer.updateFields()
cluster_layer.dataProvider().addAttributes([QgsField(field_name2, QVariant.String)])
cluster_layer.updateFields()

cluster_layer.commitChanges()


cluster_field = "CLUSTER_ID"  # field in points
gp_field = "GP Name"  # join key to map fromdp/todp

# -------------------------
# BUILD LOOKUP FOR FROMDP / TODP
# -------------------------
dp_dict = {}
for dp in gps_layer.getFeatures():
    key = f"{str(dp[gp_field])}".upper()
    dp_dict[key] = dp.geometry()
# -------------------------
# PROCESS EACH CLUSTER
# -------------------------
unique_clusters = cluster_layer.uniqueValues(cluster_layer.fields().indexFromName(cluster_field))
for cluster_id in unique_clusters:
    cluster_feats = [f for f in cluster_layer.getFeatures() if f[cluster_field] == cluster_id]
    if not cluster_feats:
        continue
    # For now assume all points in cluster map to same gp_name (adjust if per-point mapping)
    from_gp_name = cluster_feats[0]["fromdp"]
    to_gp_name = cluster_feats[0]["todp"]
    from_gp_geom = dp_dict.get(from_gp_name, None)
    if from_gp_geom is None:
        print(f"Did not find geometry for {from_gp_name}")
    to_gp_geom = dp_dict.get(to_gp_name, None)
    if to_gp_geom is None:
        print(f"Did not find geometry for {to_gp_name}")
    # Calculate distances
    cluster_layer.startEditing()
    for f in cluster_feats:
        try:
            f["from_gp_distance"] = f.geometry().distance(from_gp_geom) or 0
            f["to_gp_distance"] = f.geometry().distance(to_gp_geom) or 0
        except Exception as e:
            continue
        cluster_layer.updateFeature(f)
    cluster_layer.commitChanges()

# Destination path for saving
output_path = "/Users/subhashsoni/Formatting_excel_data/Shape_file_correction/input_point_shape_file/Clusters"

# Save the scratch layer as Shapefile
QgsVectorFileWriter.writeAsVectorFormat(
    cluster_layer,
    output_path,
    "UTF-8",                         # encoding
    cluster_layer.crs(),             # keep same CRS
    "ESRI Shapefile"                 # format
)
print("Field calculated and saved.")
print("Workflow completed. Final snapped layer added to QGIS.")
