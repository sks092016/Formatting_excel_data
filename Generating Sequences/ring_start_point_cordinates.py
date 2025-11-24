import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Dabra"

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
gps_shape_file = "References/Dabra/gps.shp"
segments_shape_file = "References/Dabra/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '78.33176240 25.88569860'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R2-C1':'78.44659280 26.05667590',
    'R3-C1':'78.28074915 25.99036729',
    'R3-C2':'78.34723653 26.03645987',
    'R4-C1':'78.24909173 25.89715821',
}
t_point_ring_spans = {
'T-POINT BIJAKPUR':(78.27605533,25.82013164),
'T-POINT JANAKPUR':(78.42298810,26.03554120),
'T-POINT KIROL':(78.55211430,26.05305950),
'T-POINT LAKHNOTI':(78.44659280,26.05667590),
'T-POINT MAHARAJPUR':(78.24909173,25.89715821),
'T-POINT TEKANPUR':(78.28074915,25.99036729),
'T-POINT LADERA':(78.34717654,26.03648567),
'T-POINT DABRA BLOCK':(78.30759524,25.84339944),
}
