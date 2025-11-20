import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Khairlangi"

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
gps_shape_file = "References/Khairlangi/gps.shp"
segments_shape_file = "References/Khairlangi/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '79.97841400 21.60450500'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R2-C1':'79.87753850 21.67153040',
    'R3-C1':'79.89638690 21.57544260',
    'R4-C1':'80.06850970 21.61945733',
}
t_point_ring_spans = {
'T-POINT BHIJYADAND':(79.90573337,21.68571704),
'T-POINT KATORI':(79.89636580,21.57545930),
'T-POINT MIRAGPUR':(79.83742077,21.63592722),
'T-POINT MOHADI':(80.06850970,21.61945733),
'T-POINT SALEBADI':(79.87753850,21.67153040),
'T-POINT KUMAHALI':(79.88502599,21.56655470),
'T-POINT CHHATERA':(79.81278780,21.57607810),
}
