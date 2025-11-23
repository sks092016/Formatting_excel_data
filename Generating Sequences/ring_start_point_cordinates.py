import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Neemuch"

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
gps_shape_file = "References/Neemuch/gps.shp"
segments_shape_file = "References/Neemuch/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '74.86450370 24.46730560'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R1-C1':'74.81378274 24.49133623',
    'R1-C2':'74.87854117 24.48335118',
    'R2-C1':'74.87770374 24.31460132',
    'R3-C1':'74.98572116 24.44235594',
    'R4-C1':'74.93271743 24.37387269',
}
t_point_ring_spans = {
'T-POINT BAMORI':(74.87770374,24.31460132),
'T-POINT BHATKHEDA':(74.93271743,24.37387269),
'T-POINT BISALWASSONGARA':(74.98572116,24.44235594),
'T-POINT DHANIRAKALAN':(74.81378274,24.49133623),
'T-POINT HARWAR':(74.92378449,24.33765014),
'T-POINT KANAVATI':(74.87854117,24.48335118),
}
