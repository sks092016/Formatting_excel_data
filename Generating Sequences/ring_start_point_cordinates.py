import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Kotma"

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
gps_shape_file = "References/Kotma/gps.shp"
segments_shape_file = "References/Kotma/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '81.97044405 23.21284609'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R1-C1':'82.09898880 23.30942230',
    'R2-C1':'81.96120360 23.22106610',
    'R2-C2':'82.00129920 23.30940980',
}
t_point_ring_spans = {
'T-POINT BENIBAHRA':(82.09898880,23.30942230),
'T-POINT BUDHANPUR':(81.96120360,23.22106610),
'T-POINT KOTHI':(82.05539420,23.34363510),
'T-POINT LAMATOLA':(81.97694770,23.29046757),
'T-POINT VICHARPUR':(82.00129920,23.30940980)
}
