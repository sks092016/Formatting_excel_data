import difflib
import pandas as pd
import geopandas as gpd
from collections import Counter
import re
from ring_start_point_cordinates import *
from methods import *


gps = gpd.read_file(gps_shape_file)
segments = gpd.read_file(segments_shape_file)
#_____________________________
gp_names = gps.name.tolist()
gp_name_lat_lon = list(zip(gps.name, zip(gps.geometry.x, gps.geometry.y)))
#_____________________________
gp_name_counts = Counter(gp_names)
gp_geometry_counts = Counter(gp_name_lat_lon)
#_____________________________
gp_repetions = checking_repetions(gp_name_counts)
gp_geo_repetions = checking_repetions(gp_geometry_counts)

if gp_repetions:
#does their geometry repeats
    if gp_geo_repetions:
        logging.info(f"These GPs are repeating {gp_repetions}")
        logging.info(f"The Geometry of these GPs are {gp_geo_repetions}")
    else:
        logging.info(f"These GPs are repeating {gp_repetions} but their geometry is different")
        logging.info("Their Geometry is: ")
        df = pd.DataFrame(list(gp_geometry_counts.keys()), columns=["gp_name", "coords"])
        duplicates = df[df.duplicated("gp_name", keep=False)]
        logging.info(duplicates)

spans = segments.span_name.tolist()
consistancy =  check_gp_consistency(spans, gp_names)
logging.info(consistancy)