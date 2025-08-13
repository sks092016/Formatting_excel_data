import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Shivpuri"

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
gps_shape_file = "References/Shivpuri/gps_ne.shp"
segments_shape_file = "References/Shivpuri/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '77.67055920 25.42077520'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R1_C1': '77.55322940 25.50657657',
    'R1_C2': '77.61703856 25.44491937',
    'R2_C1': '77.71024625 25.71810877',
    'R3_C1': '77.79196527 25.41852214',
    'R3_C2': '77.63061351 25.35748617',
}
# Non Spur T-POINT SPANS points or Segments which are part of closed Ring
t_point_ring_spans = {
    't point khutela' : (77.86256758,25.39348160),
    't point banskhedi': (77.63061352,25.35748617),
    't point kunwarpur': (77.59249590,25.55992045),
    't point bhangad' : (77.75619105,25.76292149),
    't point gurawal': (77.76812083,25.83406604),
    't point kankar' : (77.74048104,25.54426135),
    't point sakalpur': (77.76453239,25.55204034)
}
