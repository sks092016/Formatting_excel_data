from qgis.core import (
    QgsProject, QgsPrintLayout, QgsLayoutItemMap,
    QgsLayoutItemLegend, QgsLayoutItemLabel, QgsLayoutExporter,
    QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes, QgsLayerTree, QgsLegendStyle, QgsTextFormat, QgsRectangle
)
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtCore import Qt
import os

# --- Settings ---
layer_name = "row_clubbed_file"   # Name of the layer in QGIS
output_folder = r" /Users/subhashsoni/Documents/Bharatnet_OFC_planning/SLDs"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# --- Helper: adjust extent to map frame aspect ratio ---
def adjusted_extent(layer_extent, map_width, map_height, buffer=0.1):
    """
    Scale geographic extent to match the aspect ratio of the map frame.
    Adds buffer (fraction of width/height).
    """
    xmin, xmax = layer_extent.xMinimum(), layer_extent.xMaximum()
    ymin, ymax = layer_extent.yMinimum(), layer_extent.yMaximum()

    width = xmax - xmin
    height = ymax - ymin

    # Add buffer
    xmin -= width * buffer
    xmax += width * buffer
    ymin -= height * buffer
    ymax += height * buffer
    width = xmax - xmin
    height = ymax - ymin

    # Aspect ratios
    data_aspect = width / height if height != 0 else 1
    frame_aspect = map_width / map_height if map_height != 0 else 1

    # Adjust to match frame aspect
    if data_aspect > frame_aspect:  # data wider than frame
        new_height = width / frame_aspect
        diff = (new_height - height) / 2
        ymin -= diff
        ymax += diff
    else:  # data taller than frame
        new_width = height * frame_aspect
        diff = (new_width - width) / 2
        xmin -= diff
        xmax += diff

    return QgsRectangle(xmin, ymin, xmax, ymax)

# --- Load layer ---
layer_list = QgsProject.instance().mapLayersByName(layer_name)
if not layer_list:
    raise Exception(f"❌ Layer '{layer_name}' not found")
layer = layer_list[0]
if not layer.isValid():
    raise Exception(f"❌ Layer '{layer_name}' is not valid")

# Get unique span values
span_field_index = layer.fields().lookupField("span_name")
unique_spans = layer.uniqueValues(span_field_index)

project = QgsProject.instance()
manager = project.layoutManager()

for span in unique_spans:
    # Filter layer to one span
    expr = f""""span_name" = '{span}'"""
    layer.setSubsetString(expr)

    # --- Create Layout ---
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(f"Layout_{span}")

    # --- Page size ---
    page = layout.pageCollection().pages()[0].pageSize()
    page_width = page.width()
    page_height = page.height()

    # Margins (mm)
    margin = 15
    map_width = page_width - 2 * margin
    map_height = page_height - 2 * margin
    x = (page_width - map_width) / 2
    y = (page_height - map_height) / 2

    # --- Map Item ---
    map_item = QgsLayoutItemMap(layout)
    map_item.setRect(x, y, map_width, map_height)

    # Adjust extent to frame aspect ratio with buffer
    extent = adjusted_extent(layer.extent(), map_width, map_height, buffer=0.1)
    map_item.setExtent(extent)

    # Add border/frame
    map_item.setFrameEnabled(True)
    layout.addLayoutItem(map_item)

    # --- Title ---
    title = QgsLayoutItemLabel(layout)
    title.setText(f"Span: {span}")

    font = QFont("Cambria", 18, QFont.Bold)
    font.setUnderline(True)

    fmt = QgsTextFormat()
    fmt.setFont(font)
    fmt.setSize(18)
    title.setTextFormat(fmt)

    # Full width box for centering
    title.setFixedSize(QgsLayoutSize(page_width, 15, QgsUnitTypes.LayoutMillimeters))
    title.attemptMove(QgsLayoutPoint(0, 5, QgsUnitTypes.LayoutMillimeters))
    title.setHAlign(Qt.AlignHCenter)

    layout.addLayoutItem(title)

    # --- Legend ---
    legend = QgsLayoutItemLegend(layout)
    legend.setTitle("Row Authority")

    root = QgsLayerTree()
    root.addLayer(layer)  # only current layer
    legend.model().setRootGroup(root)

    # Font for legend
    legend_font = QFont("Cambria", 8)
    legend.setStyleFont(QgsLegendStyle.Title, legend_font)
    legend.setStyleFont(QgsLegendStyle.Subgroup, legend_font)
    legend.setStyleFont(QgsLegendStyle.SymbolLabel, legend_font)

    legend.adjustBoxSize()
    # Bottom-left placement
    legend.attemptMove(QgsLayoutPoint(10, page_height - 70, QgsUnitTypes.LayoutMillimeters))

    layout.addLayoutItem(legend)

    # --- Export PDF ---
    exporter = QgsLayoutExporter(layout)
    pdf_path = os.path.join(output_folder, f"{span}.pdf")
    result = exporter.exportToPdf(pdf_path, QgsLayoutExporter.PdfExportSettings())

    if result == QgsLayoutExporter.Success:
        print(f"✅ Exported {pdf_path}")
    else:
        print(f"❌ Failed to export {pdf_path}")

# Reset filter
layer.setSubsetString("")
