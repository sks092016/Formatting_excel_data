import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Karera"

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
gps_shape_file = "References/Karera/gps.shp"
segments_shape_file = "References/Karera/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '78.14690021 25.45493864'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R1-C1':'78.25271966 25.46115220',
    'R1-C2':'78.27277173 25.41356901',
    'R2-C1':'77.95813590 25.46997067',
    'R2-C2':'78.13159597 25.39416491',
    'R3-C1':'78.23490540 25.57068023',
    'R3-C2':'78.28021886 25.53164412',
    'R4-C1': '78.13956776 25.61074377',
    'R4-C2': '78.15259369 25.59005605',
}
t_point_ring_spans = {
'T-POINT BANSGAD':(78.08662627,25.54890499),
'T-POINT BHAINSA':(78.19064885,25.70315075),
'T-POINT CHOKA':(78.21269816,25.47305896),
'T-POINT DAWARBHAT':(78.23490540,25.57068023),
'T-POINT FATEHPUR':(78.15259369,25.59005605),
'T-POINT JUJHAI':(78.13159597,25.39416491),
'T-POINT KALIPAHADI':(78.25271966,25.46115220),
'T-POINT KHADICHA':(78.13956776,25.61074377),
'T-POINT KHAIRAGHAT':(78.12296633,25.46413918),
'T-POINT KHIRIAPUNAWALI':(78.27277173,25.41356901),
'T-POINT KHUDAWALI':(78.28021886,25.53164412),
'T-POINT KUCHALON':(78.25883800,25.38027310),
'T-POINT MAMONIKALA':(77.99878113,25.38279438),
'T-POINT NARAHI':(78.06170488,25.44857609),
'T-POINT RAJGAD':(77.95813590,25.46997067),
'T-POINT RAMNAGAR':(78.12059848,25.49223333),
'T-POINT TODAKARERA':(78.17917045,25.46044133),
'T-POINT UKAYALA':(77.94686830,25.49647000),
}
