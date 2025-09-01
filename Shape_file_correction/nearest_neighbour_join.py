from qgis.core import QgsSpatialIndex, QgsFeature, QgsProject, QgsVectorLayer, QgsVectorFileWriter
from qgis.core import QgsProject, QgsFeature
from qgis.core import QgsField
from PyQt5.QtCore import QVariant
import processing
from qgis.core import QgsVectorFileWriter
from qgis.core import QgsProject, QgsVectorFileWriter, QgsFeature, QgsGeometry
import os
from qgis.core import QgsFeatureRequest
# -----------------------------
# USER SETTINGS
# -----------------------------
points_layer_name = "Point_Data"
ring_layer_name = "OFC"
selected_ring_fields = ['ring_code','fromdp', 'todp']
max_distance = 0.01
output_path = "/Users/YourUser/Documents/joined_points_clean.shp"

# -----------------------------
# LOAD LAYERS
# -----------------------------
points_layer = QgsProject.instance().mapLayersByName(points_layer_name)[0]
ring_layer = QgsProject.instance().mapLayersByName(ring_layer_name)[0]

# -----------------------------
# BUILD SPATIAL INDEX
# -----------------------------
index = QgsSpatialIndex(ring_layer.getFeatures())

# -----------------------------
# CREATE OUTPUT MEMORY LAYER
# -----------------------------
out_layer = QgsVectorLayer(f"Point?crs={points_layer.crs().authid()}", "joined_points", "memory")
out_dp = out_layer.dataProvider()

# Add fields
out_dp.addAttributes(points_layer.fields())
out_dp.addAttributes([ring_layer.fields()[ring_layer.fields().indexFromName(f)] for f in selected_ring_fields])
out_layer.updateFields()

# -----------------------------
# PROCESS POINT FEATURES
# -----------------------------
for pt in points_layer.getFeatures():
    if not pt.hasGeometry() or not pt.geometry().isGeosValid():
        continue

    nearest_ids = index.nearestNeighbor(pt.geometry().asPoint(), 1)
    if not nearest_ids:
        continue

    ring_feat = ring_layer.getFeature(nearest_ids[0])
    if not ring_feat.hasGeometry() or not ring_feat.geometry().isGeosValid():
        continue

    if pt.geometry().distance(ring_feat.geometry()) > max_distance:
        continue

    f = QgsFeature()
    f.setGeometry(pt.geometry())
    attrs = pt.attributes() + [ring_feat[f] for f in selected_ring_fields]
    f.setAttributes(attrs)
    out_dp.addFeature(f)

# -----------------------------
# ADD TO PROJECT
# -----------------------------
# QgsProject.instance().addMapLayer(out_layer)

clustered_result = processing.run("native:kmeansclustering", {
    'INPUT':out_layer,
    'CLUSTERS':2000,
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
# -----------------------------
# SAVE USING OLD API
# -----------------------------
QgsVectorFileWriter.writeAsVectorFormat(
    cluster_layer,
    output_path,
    "UTF-8",
    out_layer.crs(),
    "ESRI Shapefile"
)

print(f"✅ Saved {out_layer.featureCount()} features → {output_path}")
