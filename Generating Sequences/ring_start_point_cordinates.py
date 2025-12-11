import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Karhal"

now = datetime.now()
formatted = now.strftime("%d-%m-%y_%H-%M-%S")

# Define log file
log_file = log_dir / f"segment_span_sequence_{blockName}-{formatted}.log"

# Configure logging
logging.basicConfig(
    filename=log_file,
    filemode='a',  # Append mode
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Optional: also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
#### Checking the CRS of the shape file

# input file names
gps_shape_file = "References/Karhal/gps.shp"
segments_shape_file = "References/Karhal/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '77.06058091 25.49686555'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R2-C1':'77.06015600 25.61104490',
    'R3-C1':'76.77987160 25.49833810',
}
t_point_ring_spans = {
'T-POINT BANDHALI':(76.76944158,25.52903186),
'T-POINT BARDHAKHURD':(76.77987160,25.49833810),
'T-POINT DHONDPUR':(76.74173167,25.57522201),
'T-POINT GADLA':(76.99422956,25.70686005),
'T-POINT JAKHDA':(77.06015600,25.61104490),
'T-POINT JHIRINYA':(76.86753720,25.37628000),
'T-POINT KARIYADEH':(77.01794976,25.32525169),
'T-POINT LEHRONI':(77.10595355,25.52091551),
'T-POINT PAHELA':(76.88295910,25.42306891),
'T-POINT PIPRANI':(76.99422956,25.70686005),
'T-POINT SESAIPURA':(77.17382826,25.54035444),
}
