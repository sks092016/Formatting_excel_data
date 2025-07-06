import pandas as pd
import geopandas as gpd
from math import radians, sin, cos, sqrt, atan2
import tkinter as tk
from tkinter import filedialog
import time
from IPython.display import display
from tabulate import tabulate

gdf_reference = gpd.read_file("References/tarana_shape_file.shp")
print(tabulate(gdf_reference.head(),headers = 'keys', tablefmt = 'psql'))

