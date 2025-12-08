import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Sasner"

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
gps_shape_file = "References/Sasner/gps.shp"
segments_shape_file = "References/Sasner/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '76.10074928 23.93502267'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R1-C1':'76.07266620 24.01151270',
    'R2-C1':'76.15141254 24.08838491',
    'R2-C2':'76.17111130 24.18687002',
}
t_point_ring_spans = {
'T-POINT BADIYA':(76.13180910,23.99700260),
'T-POINT DEVLI':(76.18682480,24.18719820),
'T-POINT DHERIYA SOYAT':(76.15138060,24.12298890),
'T-POINT DHERIYA SUSNER':(75.99595730,23.97664570),
'T-POINT DONGARGAV':(76.15270910,24.27830360),
'T-POINT KARKADIYA SOYAT':(76.16945873,24.18322171),
'T-POINT KHEJDAKHEDI':(76.15294130,24.08361230),
'T-POINT KHERANA':(76.13706860,24.01289250),
'T-POINT KHERIYA SOYAT':(76.18749407,24.16828610),
'T-POINT LALAKHEDI':(76.17593485,24.05599198),
'T-POINT LODHAKHEDI':(76.06059680,24.04578830),
'T-POINT NANORA':(76.06059680,24.04578830),
'T-POINT PIPLYA NANKAR':(76.07074189,23.93765214),
'T-POINT SHYAMPURA':(76.07266620,24.01151270),
}
