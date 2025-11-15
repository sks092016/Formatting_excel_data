import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Sardarpur-2"

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
gps_shape_file = "References/Sardarpur-2/gps.shp"
segments_shape_file = "References/Sardarpur-2/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '74.97507875 22.66384565'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R6': BHQ_CORDINATE,
    'R2-C1':'74.84955910 22.70766059',
    'R4-C1':'75.08219956 22.84345756',
    'R5-C1':'75.04541697 22.90231969',
    'R5-C2':'75.05868402 22.76570134',
    'R6-C1': '75.03965125 22.63605441',
    'R6-C2': '75.05395092 22.64018537',
}
t_point_ring_spans = {
'T-POINT AMODIYA':(74.93921306,22.68545866),
'T-POINT BHATIABARDI':(74.84955910,22.70766059),
'T-POINT DEDLA':(75.05868402,22.76570134),
'T-POINT FULGAVDI':(75.03965125,22.63605441),
'T-POINT POPARNI':(74.94030217,22.66574247),
'T-POINT SAJOD':(75.06693546,22.95151681),
'T-POINT SALWA':(75.04541697,22.90231969),
'T-POINT UNDELI':(75.05395092,22.64018537),
'T-POINT UTAVA':(74.81466487,22.65155177),
'T-POINT AMBA':(74.82204507,22.74749160),
}
