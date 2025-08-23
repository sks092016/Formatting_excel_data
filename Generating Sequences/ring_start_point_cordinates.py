import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Sohagpur"

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
gps_shape_file = "References/Sohagpur/gps.shp"
segments_shape_file = "References/Sohagpur/OFC_NEW2.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '81.35733800 23.30678800'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R1-C1':'81.41100818 23.35151756',
    'R3-C1':'81.35959961 23.24604788'
}
# Non Spur T-POINT SPANS points or Segments which are part of closed Ring
t_point_ring_spans = {
    't-point nargi' : (81.43876489, 23.23129172),
    't-point bandhwabada': (81.33876473, 23.18831281),
    't-point maiki': (81.42901691, 23.36109677),
    't-point kitoli' : (81.45626627,23.35902508),
    't-point senduri chuniya': (81.31223499,23.25853792),
    't-point pachagaon':(23.24604788,81.35959961)
}
