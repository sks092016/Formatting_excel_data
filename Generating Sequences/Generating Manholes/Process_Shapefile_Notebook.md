
# 🧭 Geospatial Line Segment Processor (Step-by-Step Notebook)

This notebook demonstrates how to process shapefile line segments to extract specific coordinates.

### Install Dependencies
```bash
pip install geopandas shapely matplotlib
```

### Import Libraries
```python
import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import linemerge
import re
import matplotlib.pyplot as plt
```
*(Remaining cells follow same logic as the script.)*
