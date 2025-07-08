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

folder_path = 'D:\\bharat_net_data\\'
gdf_reference = gpd.read_file("References/tarana_shape_file.shp")
print(tabulate(gdf_reference.head(),headers = 'keys', tablefmt = 'psql'))

dir_path = Path(folder_path + 'Ujjain' +"-"+ 'Tarana')
a = "x"
b = "y"
v = 1.0
# If it exists, delete it
if dir_path.exists() and dir_path.is_dir():
    shutil.rmtree(dir_path)  # Deletes the entire folder and its contents

# Now create it fresh
dir_path.mkdir(parents=True, exist_ok=False)
print(dir_path)
with pd.ExcelWriter(str(dir_path)+f"\\{a}-{b}-{v}.xlsx", engine='openpyxl', mode='w') as writer:
    gdf_reference.to_excel(writer, sheet_name='Details Sheet', index=False)