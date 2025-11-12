from qgis.core import (
    QgsProject, QgsPrintLayout, QgsLayoutItemMap,
    QgsLayoutItemLegend, QgsLayoutItemLabel, QgsLayoutExporter,
    QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes, QgsLayerTree, QgsLegendStyle, QgsTextFormat, QgsRectangle
)
from qgis.core import (
    QgsLayoutItemTextTable, QgsLayoutTableColumn, QgsLayoutTable,QgsLayoutItemPicture,
    QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes, QgsLayoutFrame, QgsLayoutMeasurement, QgsLayoutItemScaleBar, Qgis,QgsLayoutItemPage
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from qgis.PyQt.QtGui import QFont, QColor
from qgis.PyQt.QtCore import Qt
import os
import json
from pathlib import Path

district_name = 'Ujjain'
block_name = 'Mahidpur'

# --- Settings ---
# file_path =f"/Users/subhashsoni/Formatting_excel_data/Generating SLDs/input/{block_name}/ring_details_{block_name}.json"
file_path = f"C:\\Users\SubhashSoni\PycharmProjects\Formatting_excel_data\Generating SLDs\input\{block_name}\\ring_details_{block_name}.json"
with open(file_path, "r", encoding="utf-8") as f:
    ring_dict = json.load(f)

layer_name = f"RoW Authorities-{block_name}"  # Name of the layer in QGIS
# output_folder = f"/Users/subhashsoni/Documents/Bharatnet_OFC_planning/SLDs/{block_name}"
output_folder = f"D:\\bharat_net_data\slds\\{block_name}"
end_point_layer = f"output_points_rings-{block_name}"


block_dir = Path(output_folder)
block_dir.mkdir(exist_ok=True)

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

vertices_layer = QgsProject.instance().mapLayersByName(end_point_layer)[0]

# Get unique span values
ring_field_index = layer.fields().lookupField("ring")
unique_rings = layer.uniqueValues(ring_field_index)

project = QgsProject.instance()
manager = project.layoutManager()

for ring in unique_rings:
    # Filter layer to one span
    expr = f""""ring" = '{ring}'"""
    layer.setSubsetString(expr)
    expr_for_end_points = f""""ring" = '{ring}'"""
    vertices_layer.setSubsetString(expr_for_end_points)

    # --- Create Layout ---
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(f"Layout_{ring}")

    # --- Page size ---
    layout_page = layout.pageCollection().pages()[0]
    layout_page.setPageSize(QgsLayoutSize(594, 420, QgsUnitTypes.LayoutMillimeters))
    page = layout_page.pageSize()
    page_width = page.width()
    page_height = page.height()

    # Margins (mm)
    margin = 5
    map_width = 510 - 2 * margin
    map_height = 415 - 2 * margin
    x = (page_width - map_width) / 2
    y = (page_height - map_height) / 2

    # --- Map Item ---
    map_item = QgsLayoutItemMap(layout)
    map_item.setRect(x, y, map_width, map_height)
    extent = adjusted_extent(layer.extent(), map_width, map_height, buffer=0.1)
    map_item.setExtent(extent)
    map_item.setFrameEnabled(True)
    map_item.attemptResize(QgsLayoutSize(510, 415, QgsUnitTypes.LayoutMillimeters))
    map_item.attemptMove(QgsLayoutPoint(80,2,QgsUnitTypes.LayoutMillimeters))
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.8, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(map_item)

    # --- Title ---
    title = QgsLayoutItemLabel(layout)
    title.setText(f"{block_name}--{ring}")
    font = QFont("Cambria", 25, QFont.Bold)
    fmt = QgsTextFormat()
    fmt.setFont(font)
    fmt.setSize(25)
    title.setTextFormat(fmt)
    title.attemptMove(QgsLayoutPoint(95, 15, QgsUnitTypes.LayoutMillimeters))
    # title.setHAlign(Qt.AlignHCenter)
    layout.addLayoutItem(title)

    # --- TABLE 1 (6x2) ---
    table = QgsLayoutItemTextTable(layout)
    layout.addMultiFrame(table)
    cols = [QgsLayoutTableColumn(), QgsLayoutTableColumn()]
    cols[0].setHeading("State")
    cols[1].setHeading("Madhya Pradesh")
    cols[0].setWidth(20)  # in mm
    cols[1].setWidth(50)
    table.setColumns(cols)
    rows = [
        ["District", district_name],
        ["Block", block_name],
        ["Ring", ring],
        ["No of Spans", str(ring_dict[ring]["meta"]["total_spans"])],
        ["Length", str(round(ring_dict[ring]["meta"]["total_length"]))],
    ]
    table.setContents(rows)
    table.setWrapBehavior(True)
    header_font = QFont("Cambria", 15)
    header_font.setBold(True)
    table.setHeaderFont(header_font)
    table.setHeaderFontColor(QColor('Red'))
    content_font = QFont("Cambria", 15)
    table.setContentFont(content_font)
    frame = QgsLayoutFrame(layout, table)
    frame.setFixedSize(QgsLayoutSize(70, 100, QgsUnitTypes.LayoutMillimeters))
    frame.attemptResize(QgsLayoutSize(70, 100, QgsUnitTypes.LayoutMillimeters))
    frame.attemptMove(QgsLayoutPoint(3, 2, QgsUnitTypes.LayoutMillimeters))
    table.addFrame(frame)
    table.update()  
    layout.refresh()
    # table 2
    table_row = QgsLayoutItemTextTable(layout)
    layout.addMultiFrame(table_row)
    cols = [QgsLayoutTableColumn(), QgsLayoutTableColumn()]
    cols[0].setHeading("Authority")
    cols[1].setHeading("Length(m)")
    cols[0].setWidth(35)  # in mm
    cols[1].setWidth(35)
    table_row.setColumns(cols)
    for key  in ring_dict[ring]["meta"]["row_autho"].keys():
        table_row.addRow([str(key), str(round(ring_dict[ring]["meta"]["row_autho"][key]))])
    table_row.setWrapBehavior(True)
    header_font = QFont("Cambria", 15)
    header_font.setBold(True)
    table_row.setHeaderFont(header_font)
    table_row.setHeaderFontColor(QColor('Red'))
    content_font = QFont("Cambria", 15)
    table_row.setContentFont(content_font)
    frame = QgsLayoutFrame(layout, table_row)
    frame.setFixedSize(QgsLayoutSize(70, 100, QgsUnitTypes.LayoutMillimeters))
    frame.attemptResize(QgsLayoutSize(70, 100, QgsUnitTypes.LayoutMillimeters))
    frame.attemptMove(QgsLayoutPoint(3,120, QgsUnitTypes.LayoutMillimeters))
    table_row.addFrame(frame)
    table_row.update()
    layout.refresh()
    #___________________________________
    legend = QgsLayoutItemLegend(layout)
    legend.setTitle("Legends")
    root = QgsLayerTree()
    root_layer = root.addLayer(layer) # Only current layer
    legend.model().setRootGroup(root)
    title_font = QFont("Cambria", 15)
    title_font.setBold(True)
    label_font = QFont("Cambria", 15)
    legend.setStyleFont(QgsLegendStyle.Title, title_font)
    legend.setStyleFont(QgsLegendStyle.Subgroup, label_font)
    legend.setStyleFont(QgsLegendStyle.SymbolLabel, label_font)
    legend.setSymbolWidth(15)  # mm
    legend.setSymbolHeight(5)  # mm
    legend.setFrameEnabled(True)  # Draw border
    legend.setFrameStrokeWidth(QgsLayoutMeasurement(0.8, QgsUnitTypes.LayoutMillimeters))  # Thin border
    legend.setFrameStrokeColor(QColor(50, 50, 50))  # Dark gray
    legend.setBackgroundColor(QColor(255, 255, 255, 220))  # Semi-transparent white
    legend.setBoxSpace(5.0)  # Padding inside legend box
    legend.setColumnSpace(5.0)  # Space between columns
    frame.attemptResize(QgsLayoutSize(70, 100, QgsUnitTypes.LayoutMillimeters))
    # legend.adjustBoxSize()
    legend.attemptMove(QgsLayoutPoint(3, 180, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(legend)
    layout.refresh()
    # --- Scale Bar ---
    scalebar = QgsLayoutItemScaleBar(layout)
    scalebar.setStyle('Double Box')
    scalebar.setLinkedMap(map_item)
    scalebar.setUnits(QgsUnitTypes.DistanceMeters)
    scalebar.setNumberOfSegments(1)
    scalebar.setNumberOfSegmentsLeft(0)
    scalebar.setUnitsPerSegment(1000)
    scalebar.setUnitLabel('m')
    scalebar.setFont(QFont("Cambria", 15))
    scalebar.setHeight(15)
    scalebar.attemptMove(QgsLayoutPoint(3, 390, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(scalebar)

    # --- North Arrow (as SVG Picture) ---
    picture = QgsLayoutItemPicture(layout)
    picture.setPicturePath("C:\\Users\SubhashSoni\PycharmProjects\Formatting_excel_data\Generating SLDs\\North\\north_simple.svg")
    # picture.setPicturePath("/Users/subhashsoni/Formatting_excel_data/Generating SLDs/North/north_simple.svg")
    picture.setFixedSize(QgsLayoutSize(20, 20, QgsUnitTypes.LayoutMillimeters))
    picture.attemptMove(QgsLayoutPoint(page_width-30, page_height-30, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(picture)

    # --- Export PDF ---
    ring_folder = f"{output_folder}/'Rings_SLD'"
    ring_dir = Path(ring_folder)
    ring_dir.mkdir(exist_ok=True)
    
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.forceVectorOutput = False  # Avoid converting text to outlines
    pdf_settings.exportMetadata = True
    pdf_settings.rasterizeWholeImage = False  # Don't rasterize
    pdf_settings.simplifyGeometries = False  # Keep geometry intact
    pdf_settings.textRenderFormat = Qgis.TextRenderFormat.AlwaysText
    pdf_settings.dpi = 60

    exporter = QgsLayoutExporter(layout)
    pdf_path = os.path.join(ring_folder, f"{ring}-{block_name}.pdf")
    result = exporter.exportToPdf(pdf_path, pdf_settings)
    if result == QgsLayoutExporter.Success:
        print(f"✅ Exported {pdf_path}")
    else:
        print(f"❌ Failed to export {pdf_path}")
# Reset filter
layer.setSubsetString("")
vertices_layer.setSubsetString("")

