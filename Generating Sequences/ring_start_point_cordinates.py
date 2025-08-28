import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Dhar"

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
gps_shape_file = "References/Dhar/gps.shp"
segments_shape_file = "References/Dhar/OFC_NEW2.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '75.30438601 22.59855429'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R1-C1':'75.30568220 22.73751285',
    'R2-C1':'75.35276000 22.70454800',
    'R3-C1':'75.43461100 22.69689500',
}
# Non Spur T-POINT SPANS points or Segments which are part of closed Ring
t_point_ring_spans = {
    't-point bijur' : (75.47460360, 22.72640403),
    't-point khachroda': (75.41120283, 22.84025193),
    't- point teesgaon': (75.30568220, 22.73751285),
    't-point sunar khedi' : (75.34477199, 22.65515596),
}
