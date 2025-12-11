import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Shajapur"

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
gps_shape_file = "References/Shajapur/gps.shp"
segments_shape_file = "References/Shajapur/OFC_NEW-2.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '76.26797878 23.41551490'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R6': BHQ_CORDINATE,
    'R7': BHQ_CORDINATE,
    'R2-C1':'76.26749650 23.30146720',
    'R4-C1':'76.29744069 23.48364316',
    'R6-C1':'76.35351007 23.29582615',
    'R7-C1':'76.42179000 23.32000000',
}
t_point_ring_spans = {
'T-POINT ALLAUMRODE':(76.31520580,23.38489040),
'T-POINT BARDIYAGUJAR':(76.41341740,23.23424350),
'T-POINT BARDIYASON':(76.24408129,23.25589235),
'T-POINT BHADONI':(76.22693536,23.45045724),
'T-POINT CHOSLAKULMI':(76.26749650,23.30146720),
'T-POINT HIRPURBAJJA':(76.29744069,23.48364316),
'T-POINT PADLI':(76.42360842,23.33737352),
'T-POINT RANTHBHAWAR':(76.35351007,23.29582615),
'T-POINT RICHODA':(76.40250283,23.42202122),
'T-POINT SUNDARSI':(76.44109524,23.27075493),
}
