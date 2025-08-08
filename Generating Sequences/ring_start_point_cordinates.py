import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Mahidpur"

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
gps_shape_file = "References/Mahidpur/mahidpur_gps.shp"
segments_shape_file = "References/Mahidpur/Mahidpur.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '75.65702968 23.483690632'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R6': BHQ_CORDINATE,
    'R1-C1': '75.557222348 23.5868662240001',
    'R2-C1': '75.6380252 23.3759445',
    'R3-C1': '75.7661533 23.5988835',
    'R4-C1': '75.650789032 23.661996653',
    'R5-C1': '75.73959413 23.484297516',
    'R6-C1': '75.564025717 23.456512864'
}
# Non Spur T-POINT SPANS points or Segments which are part of closed Ring
t_point_ring_spans = {
    't point jawasiyapanth' : (75.73959413, 23.484297516)
}
