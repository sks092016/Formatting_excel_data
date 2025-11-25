import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Badodiya"

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
gps_shape_file = "References/Badodiya/gps.shp"
segments_shape_file = "References/Badodiya/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '76.34992628 23.59480803'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R3-C1':'76.34295010 23.68303173',
    'R3-C2':'76.26676600 23.64429558',
    'R4-C1':'76.47267219 23.43142332',
    'R4-C2':'76.51000904 23.45340654',
    'R5-C1':'76.50785450 23.56636480',
    'R5-C2':'76.51306035 23.50192713',
}
t_point_ring_spans = {
'T-POINT AYYAPUR':(76.51306035,23.50192713),
'T-POINT BADIGAV':(76.51000904,23.45340654),
'T-POINT BHDENDI':(76.24473255,23.64001068),
'T-POINT BIJANA':(76.27358480,23.54402658),
'T-POINT CHOMA':(76.26676600,23.64429558),
'T-POINT GULANA':(76.47267219,23.43142332),
'T-POINT KHEDAVAD':(76.52688831,23.55301998),
'T-POINT KITHORE':(76.50785450,23.56636480),
'T-POINT KUMHARIYAKHAS':(76.35177992,23.56660263),
'T-POINT MALYAHEDI':(76.34279813,23.68298808),
'T-POINT MALYHEDI':(76.33900511,23.69133241),
'T-POINT MANGLIYA':(76.33567825,23.65841316),
'T-POINT NOLAYA':(76.55633159,23.53896215),
}
