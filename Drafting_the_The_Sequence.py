import geopandas as gpd
from shapely.geometry import LineString
from shapely.geometry import Point
from tabulate import tabulate
import pandas as pd
version = "2.0"


gdf = gpd.read_file('References/Formats/OFC_NEW.shp')
gdf_new_sp = gdf.iloc[0:0].copy() #copies only the structure of the shape file without data
gdf_new_sp["seg_seq"] = None

def get_start_end_coords(line):
    coords = list(line.coords)
    return coords[0], coords[-1]

def merged_line_geometry(lines):
    df = pd.DataFrame({'geometry': lines})
    # Collect coordinates while avoiding duplicate midpoints
    merged_coords = []
    for line in df['geometry']:
        coords = list(line.coords)
        if not merged_coords:
            merged_coords.extend(coords)
        else:
            # Avoid duplicating the connecting point
            merged_coords.extend(coords[1:])
    # Create one merged LineString
    merged_line = LineString(merged_coords)
    return merged_line


gdf_span = gpd.GeoDataFrame(columns=['span_name', 'ring', 'start_cord','end_cord','span_seq','geometry' ], geometry='geometry')

span = gdf.sort_values('span_name').span_name.unique()
for s in span:
    temp_df = gdf[gdf.span_name == s].sort_values('Sequqnce')
    temp_df['start'] = temp_df.geometry.apply(lambda geom: get_start_end_coords(geom)[0])
    temp_df['end'] = temp_df.geometry.apply(lambda geom: get_start_end_coords(geom)[1])
    sorted_indices = []
    remaining = temp_df.copy()
    current_idx = remaining.index[0]
    current = remaining.loc[current_idx]
    sorted_indices.append(current_idx)
    remaining = remaining.drop(current_idx)
    while not remaining.empty:
        found = False
        for idx, row in remaining.iterrows():
            if row['start'] == current['end']:
                sorted_indices.append(idx)
                current = row
                remaining = remaining.drop(idx)
                found = True
                break
            elif row['start'] == current['start']:
                r = current
                print(f'{current.index[0]} is reversed')
                print(current)
            elif row['end'] == current['end']:
                r = row
                print(f'{row.index[0]} is reversed')
                print(row)
        if not found:
            print("Warning: A disconnected segment remains. Stopping sequence generation.")
            break
    sequence_series = temp_df.index.to_series().apply(
        lambda x: sorted_indices.index(x) + 1 if x in sorted_indices else None)
    # filling up the segment sequence
    temp_df['seg_seq'] = sequence_series
    temp_df = temp_df.drop(columns=['start', 'end'])
    complete_span_line = merged_line_geometry(temp_df.geometry)

    # creating the dataframe for the span sequence
    new_data = gpd.GeoDataFrame([{
        'span_name': s,
        'ring': str(temp_df.loc[temp_df.index[0], 'ring_no']),
        'start_cord':get_start_end_coords(complete_span_line)[0],
        'end_cord':get_start_end_coords(complete_span_line)[-1],
        'span_seq':'',
        'geometry': complete_span_line # Replace with your coordinates
    }], geometry='geometry')

    gdf_span = pd.concat([gdf_span, new_data], ignore_index=True)
    assert gdf_new_sp.crs == temp_df.crs, "CRS mismatch!"
    gdf_new_sp = pd.concat([gdf_new_sp, temp_df])

gdf_new_sp.to_file(f'References/Output/OFC_NEW_{version}.shp')
gdf_span.to_file(f'References/Output/OFC_NEW_SPAN{version}.shp')
print("Sequence assigned and saved with original index preserved.")