from qgis.core import (
    QgsProject, QgsPrintLayout, QgsLayoutItemMap,
    QgsLayoutItemLegend, QgsLayoutItemLabel, QgsLayoutExporter,
    QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes
)
from qgis.PyQt.QtGui import QFont
import os

# --- Settings ---
layer_name = "row_clubbed_file"# Name of the layer as shown in QGIS Layers panel
output_folder = "D:\\bharat_net_data\\slds\\"

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Get the layer from the QGIS project
layer = QgsProject.instance().mapLayersByName(layer_name)[0]
if not layer or not layer.isValid():
    raise Exception(f"❌ Layer '{layer_name}' not found or invalid")

# Iterate over unique spans
unique_spans = layer.uniqueValues(layer.fields().lookupField("span_name"))

project = QgsProject.instance()
manager = project.layoutManager()

for span in unique_spans:
    # Filter to one span
    expr = f""""span_name" = '{span}'"""
    layer.setSubsetString(expr)

    # --- Create new layout ---
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(f"Layout_{span}")

    # --- Map Item ---
    map_item = QgsLayoutItemMap(layout)
    map_item.setRect(20, 20, 200, 100)
    map_item.setExtent(layer.extent())   # zoom to current filtered span
    layout.addLayoutItem(map_item)

    # --- Title ---
    title = QgsLayoutItemLabel(layout)
    title.setText(f"Span: {span}")
    title.setFont(QFont("Arial", 16))
    title.adjustSizeToText()
    layout.addLayoutItem(title)

    # --- Legend ---
    legend = QgsLayoutItemLegend(layout)
    legend.setTitle("Row Authority")

    root = QgsLayerTree()
    root.addLayer(layer)   # Only show current layer in legend
    legend.model().setRootGroup(root)

    layout.addLayoutItem(legend)

    # --- Export to PDF ---
    exporter = QgsLayoutExporter(layout)
    pdf_path = os.path.join(output_folder, f"{span}.pdf")
    exporter.exportToPdf(pdf_path, QgsLayoutExporter.PdfExportSettings())

    print(f"✅ Exported {pdf_path}")

# Reset filter
layer.setSubsetString("")

