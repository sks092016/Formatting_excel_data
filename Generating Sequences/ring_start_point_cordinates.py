import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Athner"

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
gps_shape_file = ("References/Athner/gps.shp")
segments_shape_file = "References/Athner/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '77.92717814 21.62109233'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    "R3-C1": "77.91191389 21.50487777",
    "R3-C2": "77.82978931 21.54587488"
}
t_point_ring_spans = {
"T-POINT AMBADA": (77.74941463,21.52845884),
"T-POINT ANDERBAWADI": (77.77765408,21.41780904),
"T-POINT BELKUND": (77.77765408,21.41780904),
"T-POINT DEHGHUD": (77.83019154,21.66058921),
"T-POINT GARGUD RYT": (77.8446446,21.4624054),
"T-POINT HIDALI": (77.93555099,21.51839058),
"T-POINT KAWALA RYT": (77.83828086,21.45995175),
"T-POINT KELBEHARA": (77.8213334,21.418207),
"T-POINT PANBEHARA": (77.91191389,21.50487777),
"T-POINT PUSALI": (77.98454,21.63048),
"T-POINT WADALI": (77.82978931,21.54587488),
"T-POINT YENKHEDA": (77.96809670,21.63209550)
}
