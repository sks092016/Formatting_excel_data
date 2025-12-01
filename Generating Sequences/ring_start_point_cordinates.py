import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Harda"

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
gps_shape_file = "References/Harda/gps.shp"
segments_shape_file = "References/Harda/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '77.09832908 22.34092864'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R1-C1':'77.10955797 22.27614710',
    'R2-C1':'77.03364630 22.30789170',
    'R2-C2':'76.90892250 22.34817520',
    'R3-C1':'77.05054271 22.45004490',
    'R3-C2':'77.13022582 22.42464246',
    'R4-C1': '76.91974954 22.41492265',
}
t_point_ring_spans = {
'T-POINT BHUNNAS':(77.13022582,22.42464246),
'T-POINT HANIFABAD':(76.85962387,22.35112770),
'T-POINT KACHBEDI':(76.90892250,22.34817520),
'T-POINT KADOLA UWARI':(77.03364630,22.30789170),
'T-POINT KAMTADA':(76.99490345,22.25321955),
'T-POINT KANARDA':(77.10955797,22.27614710),
'T-POINT KHEDINEEMA':(77.04821819,22.47673494),
'T-POINT NAYAPURA':(76.88525973,22.44958333),
'T-POINT NEEMGAON':(77.02487645,22.33969645),
'T-POINT RATATALAI':(76.91974954,22.41492265),
'T-POINT RIJGAON':(77.05054271,22.45004490),
'T-POINT SALYAKHEDI':(76.83325743,22.43756884),
}
