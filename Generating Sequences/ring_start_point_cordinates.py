import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Nalkheda"

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
gps_shape_file = "References/Nalkheda/gps.shp"
segments_shape_file = "References/Nalkheda/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '76.24728479 23.84099693'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R1-C1':'76.20798664 23.98864892',
    'R5-C1':'76.19783541 23.74662251',
}
t_point_ring_spans = {
'T-POINT BHANDAWAD':(76.30897353,23.83452593),
'T-POINT HIRANKHEDI':(76.26376118,23.92651888),
'T-POINT MANASA':(76.19783541,23.74662251),
'T-POINT SEMALKHEDI':(76.14026427,23.88088465),
'T-POINT SIRPOI':(76.20798664,23.98864892),
}
