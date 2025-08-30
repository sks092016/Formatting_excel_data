import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Sabalgarh"

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
gps_shape_file = "References/Sambalgarh/gps.shp"
segments_shape_file = "References/Sambalgarh/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '77.40593800 26.25149000'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R1_C1':'77.42896000 26.29559000',
    'R2_C1':'77.39167080 26.27434756',
    'R3_C1':'77.30012200 26.17664200',
}
# Non Spur T-POINT SPANS points or Segments which are part of closed Ring
t_point_ring_spans = {
    't-point rampur' : (77.42896000,26.29559000),
    't-point babdipura': (77.26184323,26.19710885),
    't-point kemara khurd': (77.22735290,26.18223045),
    't-point jatoli' : (77.31399500, 26.22862500),
    't-point ram pahadi' : (77.35245600, 26.22324700),
    't-point babdi' : (77.32587500, 26.25287400),
    't-point rangarh' : (77.34854700, 26.29314900),
    't-point battokhar' : (77.35884000, 26.30251900),
    't-point kheron':(77.41052813, 26.32095948),
    't-point rupa ki tor':(77.42167401, 26.30955256),
    't-point ratanpura':(77.49690513, 26.36843577),
    't-point hirapur':(77.49690513, 26.36843577),
    't-point piprghan':(77.39167080,26.27434756),
    't-point rampur gird':(77.43552900,26.28607400)
}
