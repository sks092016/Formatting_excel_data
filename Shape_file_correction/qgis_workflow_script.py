from qgis.core import QgsProject, QgsFeature
from qgis.core import QgsField
from PyQt5.QtCore import QVariant
import processing
from qgis.core import QgsVectorFileWriter
from qgis.core import QgsProject, QgsVectorFileWriter, QgsFeature, QgsGeometry
import os
from qgis.core import QgsFeatureRequest

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
    'MAX_DISTANCE':100,
    'OUTPUT':'TEMPORARY_OUTPUT'})["OUTPUT"]



# cluster_layer.startEditing()
# field_name1 = "from_gp_distance"
# field_name2 = "to_gp_distance"
# cluster_layer.dataProvider().addAttributes([QgsField(field_name1, QVariant.String)])
# cluster_layer.updateFields()
# cluster_layer.dataProvider().addAttributes([QgsField(field_name2, QVariant.String)])
# cluster_layer.updateFields()
# cluster_layer.commitChanges()

# cluster_field = "CLUSTER_ID"  # field in points
# gp_field = "GP Name"  # join key to map fromdp/todp
# # -------------------------
# # BUILD LOOKUP FOR FROMDP / TODP
# # -------------------------
# dp_dict = {}
# for dp in gps_layer.getFeatures():
#     key = f"{str(dp[gp_field])}".upper()
#     dp_dict[key] = dp.geometry()
# # -------------------------
# # PROCESS EACH CLUSTER
# # -------------------------
# unique_clusters = cluster_layer.uniqueValues(cluster_layer.fields().indexFromName(cluster_field))
# for cluster_id in unique_clusters:
#     cluster_feats = [f for f in cluster_layer.getFeatures() if f[cluster_field] == cluster_id]
#     if not cluster_feats:
#         continue

#     from_gp_name = str(cluster_feats[0]["fromdp"]).upper()
#     to_gp_name = str(cluster_feats[0]["todp"]).upper()

#     from_gp_geom = dp_dict.get(from_gp_name)
#     to_gp_geom = dp_dict.get(to_gp_name)

#     if from_gp_geom is None or to_gp_geom is None:
#         print(f"Skipping cluster {cluster_id}, missing GP geom")
#         continue

#     cluster_layer.startEditing()
#     for f in cluster_feats:
#         if not f.hasGeometry() or not f.geometry().isGeosValid():
#             continue
#         try:
#             f["from_gp_distance"] = float(f.geometry().distance(from_gp_geom))
#             f["to_gp_distance"] = float(f.geometry().distance(to_gp_geom))
#             cluster_layer.updateFeature(f)
#         except Exception as e:
#             print(f"Error for feature {f.id()}: {e}")
#             continue
#     cluster_layer.commitChanges()

