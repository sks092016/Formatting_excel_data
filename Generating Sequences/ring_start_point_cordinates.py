import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Kalapipal"

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
gps_shape_file = "References/Kalapipal/gps.shp"
segments_shape_file = "References/Kalapipal/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '76.82423830 23.33375500'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R1-C1':'76.85945200 23.42156300',
    'R1-C2':'76.88336692 23.47615846',
    'R2-C1':'76.93966830 23.38511830',
    'R3-C1':'76.81834384 23.23243118',
    'R4-C1':'76.88257923 23.22321445',
}
t_point_ring_spans = {
'T-POINT ALNIYA':(76.89719227,23.31832097),
'T-POINT BHARDI':(76.83672953,23.30789342),
'T-POINT BHRAWAL':(76.85945200,23.42156300),
'T-POINT DHABLADHIR':(76.97016870,23.32736770),
'T-POINT HADLAYKHURD':(76.80033785,23.22721576),
'T-POINT LALA KHEDI':(76.88257923,23.22321445),
'T-POINT NIPANYAKHANJAR':(76.88336692,23.47615846),
'T-POINT RONSLA':(76.81834384,23.23243118),
'T-POINT TILAVAD MENA':(76.69590947,23.21515007),
}
