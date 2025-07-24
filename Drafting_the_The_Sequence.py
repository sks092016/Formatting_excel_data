import geopandas as gpd
from shapely.geometry import LineString
from tabulate import tabulate
version = "1.0"
import pandas as pd

gdf = gpd.read_file('References/Formats/OFC_NEW.shp')

gdf_new = gdf.iloc[0:0].copy()
gdf_new["Sequence"] = None

def get_start_end_coords(line):
    coords = list(line.coords)
    return coords[0], coords[-1]

new_df = gpd.GeoDataFrame(gdf, geometry='geometry')
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
        if not found:
            print("Warning: A disconnected segment remains. Stopping sequence generation.")
            break


    sequence_series = temp_df.index.to_series().apply(
        lambda x: sorted_indices.index(x) + 1 if x in sorted_indices else None)


    temp_df['Sequence'] = sequence_series


    temp_df = temp_df.drop(columns=['start', 'end'])

    assert gdf_new.crs == temp_df.crs, "CRS mismatch!"
    gdf_new = pd.concat([gdf_new, temp_df])

gdf_new.to_file(f'References/Output/OFC_NEW_{version}.shp')

print("Sequence assigned and saved with original index preserved.")