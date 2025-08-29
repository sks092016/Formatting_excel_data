import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Sanwer"

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
gps_shape_file = "References/Dahi/gps.shp"
segments_shape_file = "References/Dahi/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '74.58572600 22.11462600'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R2_C1':'74.54288400 22.20237600',
    'R3_C1':'74.67893057 22.15975566',
}
# Non Spur T-POINT SPANS points or Segments which are part of closed Ring
t_point_ring_spans = {
    't-point kalami' : (74.59103323,22.21041797),
    't-point arada': (74.54113617,22.20222182),
    't-point gp gajgota': (74.57202477,22.16247279),
    't-point khatami' : (74.58726823,22.16869047),
    't-point chakalya' : (74.58291270,22.12216864),
    't-point rebarda' : (74.67893057,22.15975566),
    't-point katarkheda' : (74.55619883,22.07870419),
    't-point kavda' : (74.52270094,22.11045993),
    't-point babli khurd':(74.60463113,22.13881607)
}
