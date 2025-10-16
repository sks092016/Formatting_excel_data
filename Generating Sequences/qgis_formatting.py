from qgis.core import (
    QgsProject,
    QgsExpression,
    QgsVectorLayerSimpleLabeling,
    QgsTextFormat,
    QgsCategorizedSymbolRenderer,
    QgsRendererCategory,
    QgsSymbol,
    QgsPalLayerSettings,
    QgsUnitTypes,
    edit
)
from qgis.PyQt.QtGui import QFont, QColor

# 1️⃣ Access layers
gps_layer = QgsProject.instance().mapLayersByName("gps")[0]
ofc_layer = QgsProject.instance().mapLayersByName("OFC_NEW")[0]

# ==============================
# STEP 1: LABEL SETTINGS FOR GPS
# ==============================
field_name = "name"

# Create and configure font
font = QFont("Georgia")
font.setBold(True)

# Create text format
text_format = QgsTextFormat()
text_format.setFont(font)
text_format.setSizeUnit(QgsUnitTypes.RenderMillimeters)
text_format.setSize(6)  # label size in millimeters
text_format.setColor(QColor("black"))

# Expression for UPPERCASE labels
expression = QgsExpression(f"upper({field_name})")

# Create labeling settings
label_settings = QgsPalLayerSettings()
label_settings.fieldName = expression.expression()

# ✅ Correct enum usage for modern QGIS
label_settings.placement = QgsPalLayerSettings.Placement.OverPoint

label_settings.setFormat(text_format)
label_settings.enabled = True

# Apply labeling
labeling = QgsVectorLayerSimpleLabeling(label_settings)
gps_layer.setLabeling(labeling)
gps_layer.setLabelsEnabled(True)
gps_layer.triggerRepaint()

print("✅ Labels created for GPS layer with uppercase GP_Name field.")

# ======================================
# STEP 2: CATEGORICAL SYMBOL FOR OFC_NEW
# ======================================
renderer_field = "ring_no"

# Get unique values for ring_no
unique_values = ofc_layer.uniqueValues(ofc_layer.fields().indexFromName(renderer_field))

categories = []
for value in unique_values:
    symbol = QgsSymbol.defaultSymbol(ofc_layer.geometryType())
    symbol.setWidth(0.86)
    category = QgsRendererCategory(value, symbol, str(value))
    categories.append(category)

renderer = QgsCategorizedSymbolRenderer(renderer_field, categories)
ofc_layer.setRenderer(renderer)
ofc_layer.triggerRepaint()

print("✅ Categorical symbology applied based on 'ring_no'.")

# ===============================================
# STEP 3: CLEAN & FORMAT span_name FIELD IN ofc_layer
# ===============================================
span_field = "span_name"

with edit(ofc_layer):
    for f in ofc_layer.getFeatures():
        span_value = f[span_field]
        if span_value:
            new_val = span_value.lower().strip()

            # Normalize t-point typos
            replacements = {
                "t point": "t-point",
                "t- point": "t-point",
                "t - point": "t-point",
            }
            for wrong, correct in replacements.items():
                new_val = new_val.replace(wrong, correct)

            if new_val != span_value:
                f[span_field] = new_val
                ofc_layer.updateFeature(f)

print("✅ span_name field normalized to lowercase and 't-point' typos fixed.")

# ====================================================
# STEP 4: COPY UNIQUE SPANS STARTING WITH "t-point"
# ====================================================
unique_spans = set()
for f in ofc_layer.getFeatures():
    span_value = f[span_field]
    if span_value and span_value.startswith("t-point"):
        unique_spans.add(span_value)

print("✅ Unique spans starting with 't-point':")
for s in sorted(unique_spans):
    print(s)
