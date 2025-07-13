import difflib

import pandas as pd
import geopandas as gpd
from math import radians, sin, cos, sqrt, atan2
import tkinter as tk
from tkinter import filedialog
import time
from IPython.display import display
from tabulate import tabulate
from pathlib import Path
import shutil
import requests

folder_path = 'D:\\bharat_net_data\\'
gdf_reference = gpd.read_file("References/tarana_shape_file.shp")
print(tabulate(gdf_reference.head(),headers = 'keys', tablefmt = 'psql'))

# dir_path = Path(folder_path + 'Ujjain' +"-"+ 'Tarana')
# a = "x"
# b = "y"
# v = 1.0
# # If it exists, delete it
# if dir_path.exists() and dir_path.is_dir():
#     shutil.rmtree(dir_path)  # Deletes the entire folder and its contents
#
# # Now create it fresh
# dir_path.mkdir(parents=True, exist_ok=False)
# print(dir_path)
# with pd.ExcelWriter(str(dir_path)+f"\\{a}-{b}-{v}.xlsx", engine='openpyxl', mode='w') as writer:
#     gdf_reference.to_excel(writer, sheet_name='Details Sheet', index=False)

# print(gdf_reference['road_autho'].unique())

# import requests
#
# def get_village_name(lat, lon):
#     url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
#     headers = {
#         'User-Agent': 'village-lookup-script'
#     }
#     response = requests.get(url, headers=headers)
#     data = response.json()
#
#     # Try extracting village or locality name
#     address = data.get('address', {})
#     village = address.get('village') or address.get('hamlet') or address.get('town') or address.get('city')
#     return address
#
# # Example usage
# print(get_village_name(23.340705, 76.037812))
#
# import requests
#
# def get_village_google(lat, lon, api_key):
#     place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=30&key={api_key}"
#     response = requests.get(place_url)
#     data = response.json()
#     name = []
#     return data['results'][0]['name']
#
# print(get_village_google(23.39504, 76.01335, ""))

# value = 'cul'
# value2 = difflib.SequenceMatcher(None, value.lower(), "culvert").ratio() > 0.5
# print(value2)

def finding_road_name(row):
    api_key = 'AIzaSyBpsTQbW0ax0c18wGhC46wLkIPNvOH1sb4'
    lat, lon = row.split(' ')[1],row.split(' ')[0]
    place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=20&type=establishment&key={api_key}"
    response = requests.get(place_url)
    data = response.json()

    return data

d = finding_road_name('77.42462327900006 24.991348586000072')
print(d)