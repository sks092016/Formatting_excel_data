import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Sheopur"

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
gps_shape_file = "References/Sheopur/gps.shp"
segments_shape_file = "References/Sheopur/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '76.69734097 25.67959218'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R6': BHQ_CORDINATE,
    'R1-C1':'76.74145213 25.86886490',
    'R2-C1':'76.59096199 25.68653540',
    'R3-C1':'76.70839717 25.45489178',
    'R4-C1':'76.64378871 25.54627835',
    'R5-C1':'76.56967660 25.51675730',
    'R5-C2':'76.63460897 25.47492237',
    'R6-C1':'76.61715857 25.81007923',
}
t_point_ring_spans = {
'T-POINT AJAPURA':(76.66595387,25.58694865),
'T-POINT ASIDA':(76.59096199,25.68653540),
'T-POINT BAGBAJ':(76.72838180,25.67464405),
'T-POINT BAGDUA':(76.61715857,25.81007923),
'T-POINT BAHARAWADA':(76.74145213,25.86886490),
'T-POINT BASOD':(76.56967660,25.51675730),
'T-POINT HIRAPUR':(76.77396434,25.83201467),
'T-POINT INDRAPURA':(76.63460897,25.47492237),
'T-POINT PANDOLA':(76.64378871,25.54627835),
'T-POINT RADEP':(76.70839717,25.45489178),
'T-POINT TALAWADHA':(76.71245200,25.52750444),
'T-POINT UDOTPURA':(76.58084450,25.44926930),
}
