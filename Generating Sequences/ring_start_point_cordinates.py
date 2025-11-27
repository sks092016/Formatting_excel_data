import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Bhitawar"

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
gps_shape_file = "References/Bhitawar/gps.shp"
segments_shape_file = "References/Bhitawar/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '78.11415150 25.79885900'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R6': BHQ_CORDINATE,
    'R1-C1':'78.17587850 25.97837760',
    'R2-C1':'78.18114688 25.76974330',
    'R3-C1':'78.11239330 25.89452000',
    'R3-C2':'78.13425439 25.94310492',
    'R4-C1':'77.99642683 25.86810048',
    'R5-C1':'77.96954191 25.79038837',
}
t_point_ring_spans = {
'T-POINT ADAMPUR':(78.07708297,25.78801559),
'T-POINT BHEGNA':(78.17587850,25.97837760),
'T-POINT CHITOLI':(77.96954191,25.79038837),
'T-POINT KHERVAYA':(78.21412125,25.94693548),
'T-POINT LUHARI':(78.18114688,25.76974330),
'T-POINT RARUA':(78.13425439,25.94310492),
'T-POINT RITHODAN':(77.99642683,25.86810048),
}
