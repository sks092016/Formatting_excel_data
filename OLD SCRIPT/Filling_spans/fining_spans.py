
# import pandas as pd
# import geopandas as gpd
# from shapely.geometry import LineString, Point
# import networkx as nx
#
# # ---------- INPUT FILES ----------
# csv_file = "Data.csv"           # CSV with From, To, Ring, SPAN
# nodes_file = "Morena/gps.shp"         # Shapefile with NAME + geometry (points)
# edges_file = "Morena/OFC_NEW.shp"         # Shapefile with geometry only (lines)
# output_file = "output_spans.shp" # Final output shapefile
#
# # ---------- LOAD DATA ----------
# spans = pd.read_csv(csv_file)
# nodes = gpd.read_file(nodes_file)     # expects column 'NAME'
# edges = gpd.read_file(edges_file)     # expects column 'geometry'
#
# # Ensure CRS is consistent
# edges = edges.set_crs(nodes.crs, allow_override=True)
#
# # Map NAME -> point geometry
# node_dict = dict(zip(nodes["GP_Name"], nodes.geometry))
#
# # ---------- BUILD GRAPH ----------
# G = nx.Graph()
#
# for idx, edge in edges.iterrows():
#     line: LineString = edge.geometry
#     coords = list(line.coords)
#     start = Point(coords[0])
#     end = Point(coords[-1])
#
#     # add edge with geometry
#     G.add_edge(start.wkt, end.wkt, geometry=line, idx=idx)
#
# # Helper to snap a node point to graph
# def snap_point_to_graph(point):
#     # match by exact WKT (since points are consistent from node shapefile)
#     return point.wkt
#
# # ---------- PATH MATCHING ----------
# output_rows = []
#
# for _, row in spans.iterrows():
#     from_node = row["From"]
#     to_node = row["To"]
#     span_name = row["Span"]
#
#     start_point = node_dict[from_node]
#     end_point = node_dict[to_node]
#
#     try:
#         path_nodes = nx.shortest_path(G, source=snap_point_to_graph(start_point),
#                                          target=snap_point_to_graph(end_point))
#     except nx.NetworkXNoPath:
#         print(f"⚠️ No path found from {from_node} to {to_node}")
#         continue
#
#     # Walk along edges in path_nodes
#     for u, v in zip(path_nodes[:-1], path_nodes[1:]):
#         data = G.get_edge_data(u, v)
#         line = data["geometry"]
#
#         # ensure direction matches u -> v
#         coords = list(line.coords)
#         if Point(coords[0]).wkt != u:
#             line = LineString(coords[::-1])  # reverse if needed
#
#         output_rows.append({
#             "FROM": from_node,
#             "TO": to_node,
#             "SPAN_NAME": span_name,
#             "geometry": line
#         })
#
# # ---------- CREATE OUTPUT SHAPEFILE ----------
# output_gdf = gpd.GeoDataFrame(output_rows, crs=nodes.crs)
# output_gdf.to_file(output_file)
#
# print(f"✅ Output shapefile saved: {output_file}")


import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point
import networkx as nx

# ---------- INPUT FILES ----------
csv_file = "Data.csv"  # CSV with From, To, Ring, SPAN
nodes_file = "Morena/gps.shp"  # Shapefile with NAME + geometry (points)
edges_file = "Morena/OFC_NEW.shp"  # Shapefile with geometry only (lines)
output_file = "output_spans.shp"  # Final output shapefile

# ---------- LOAD DATA ----------
spans = pd.read_csv(csv_file)
nodes = gpd.read_file(nodes_file)     # expects column 'NAME'
edges = gpd.read_file(edges_file)     # expects column 'geometry'

# Ensure CRS is consistent
edges = edges.set_crs(nodes.crs, allow_override=True)

# Map NAME -> point geometry
node_dict = dict(zip(nodes["GP_Name"], nodes.geometry))

# ---------- BUILD GRAPH ----------
G = nx.Graph()

for idx, edge in edges.iterrows():
    line: LineString = edge.geometry
    coords = list(line.coords)
    start = Point(coords[0])
    end = Point(coords[-1])

    # store both geometry + attributes
    G.add_edge(start.wkt, end.wkt, idx=idx, data=edge)

# Helper to snap node to graph
def snap_point_to_graph(point):
    return point.wkt

# ---------- PATH MATCHING ----------
output_rows = []

for _, row in spans.iterrows():
    from_node = row["From"]
    to_node = row["To"]
    span_name = row["Span"]

    start_point = node_dict[from_node]
    end_point = node_dict[to_node]

    try:
        path_nodes = nx.shortest_path(G, source=snap_point_to_graph(start_point),
                                         target=snap_point_to_graph(end_point))
    except nx.NetworkXNoPath:
        print(f"⚠️ No path found from {from_node} to {to_node}")
        continue

    # Walk along path
    for u, v in zip(path_nodes[:-1], path_nodes[1:]):
        edge_data = G.get_edge_data(u, v)
        original = edge_data["data"]  # full row from edges

        line = original.geometry
        coords = list(line.coords)

        # Ensure geometry direction matches
        if Point(coords[0]).wkt != u:
            line = LineString(coords[::-1])

        # Copy all attributes from original edge row
        updated = original.copy()

        # Update only the required fields
        updated["from_gp_na"] = from_node
        updated["to_gp_name"] = to_node
        updated["span_name"] = span_name
        updated["geometry"] = line

        output_rows.append(updated)

# ---------- CREATE OUTPUT SHAPEFILE ----------
output_gdf = gpd.GeoDataFrame(output_rows, crs=nodes.crs)
output_gdf.to_file(output_file)

print(f"✅ Output shapefile saved: {output_file}")
