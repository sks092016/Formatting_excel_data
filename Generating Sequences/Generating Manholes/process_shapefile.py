
import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import linemerge
import numpy as np
import re
import matplotlib.pyplot as plt

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(s))]

def point_along_line(line, distance):
    if distance > line.length:
        return line.interpolate(line.length)
    return line.interpolate(distance)

def generate_sample_shapefile(filepath='sample_segments.shp'):
    segments = []
    span_name = "SPAN_A"
    for i in range(1, 8):
        start_x, start_y = (i * 100, 0)
        end_x, end_y = ((i + 1) * 100, 0)
        crossing_t = "Bridge" if i == 3 else ("Road Cross" if i == 5 else "Normal")
        line = LineString([(start_x, start_y), (end_x, end_y)])
        segments.append({
            "span_name": span_name,
            "segment_sequence": f"S{i}",
            "crossing_t": crossing_t,
            "geometry": line
        })
    gdf = gpd.GeoDataFrame(segments, crs="EPSG:32643")
    gdf.to_file(filepath)
    print(f"Sample shapefile created: {filepath}")
    return filepath

def process_shapefile(input_path, output_path='output_points.shp', span_filter='SPAN_A'):
    gdf = gpd.read_file(input_path)
    if gdf.empty:
        raise ValueError("Shapefile is empty or invalid.")

    filtered = gdf[gdf['span_name'] == span_filter].copy()
    if filtered.empty:
        raise ValueError(f"No records found for span_name '{span_filter}'")

    filtered['sort_key'] = filtered['seg_seq'].apply(natural_sort_key)
    filtered = filtered.sort_values(by='sort_key').reset_index(drop=True)

    merged_line = linemerge(filtered.geometry.tolist())
    if merged_line.geom_type == 'LineString':
        main_line = merged_line
    else:
        main_line = linemerge(list(merged_line))

    first_point = point_along_line(main_line, 10)
    total_length = main_line.length
    points = [first_point]
    cumulative_distance = 0

    for _, row in filtered.iterrows():
        seg = row.geometry
        seg_len = seg.length
        next_cum = cumulative_distance + seg_len

        if cumulative_distance <= 1800 <= next_cum:
            points.append(point_along_line(main_line, 1800))
            break

        if row['crossing_t'] in ['Bridge', 'Road Cross']:
            if row['crossing_t'] == 'Bridge' and seg_len > 150:
                points.append(point_along_line(main_line, max(0, cumulative_distance - 50)))
                points.append(point_along_line(main_line, min(total_length, next_cum + 50)))
            else:
                points.append(point_along_line(main_line, next_cum))
            break

        cumulative_distance = next_cum

    if len(points) == 1:
        points.append(point_along_line(main_line, min(1800, total_length)))

    output_gdf = gpd.GeoDataFrame(geometry=[Point(p.x, p.y) for p in points], crs=gdf.crs)
    output_gdf['label'] = ['First_Point'] + [f"Point_{i}" for i in range(2, len(points)+1)]
    output_gdf.to_file(output_path)

    print(f"Output saved to {output_path}")
    return output_gdf

def visualize_results(input_path, output_path):
    lines = gpd.read_file(input_path)
    pts = gpd.read_file(output_path)
    fig, ax = plt.subplots(figsize=(8, 5))
    lines.plot(ax=ax, color='gray', linewidth=2)
    pts.plot(ax=ax, color='red', markersize=50)
    for idx, row in pts.iterrows():
        ax.text(row.geometry.x, row.geometry.y + 10, row['label'], fontsize=9)
    plt.title('Extracted Coordinates')
    plt.show()

if __name__ == "__main__":
    sample_path = '../References/Output/Final/OFC_New_Sujalpur-1_Seg_Span_Seq.shp'
    gdf = gpd.read_file(sample_path)
    span_list = gdf.sort_values('span_name').span_name.unique()
    for s in span_list:
        process_shapefile(sample_path, 'output_points.shp', span_filter=s)
        visualize_results(sample_path, 'output_points.shp')
        break