import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Shahpura"

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
gps_shape_file = "References/Shahpura/gps.shp"
segments_shape_file = "References/Shahpura/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '80.69432377 23.18452404'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R6': BHQ_CORDINATE,
    'R2-C1':'80.80007300 23.20909040',
    'R2-C2':'80.86138437 23.20341692',
    'R2-C3':'80.87171419 23.11176823',
    'R5-C1':'80.64362040 23.28339400',
    'R6-C1':'80.79292165 23.05237797',
}
t_point_ring_spans = {
'T-POINT AMERA':(80.79652550,23.05134240),
'T-POINT ANAKHEDA':(80.83583560,23.08465990),
'T-POINT BICHIYA':(80.56362448,23.09056037),
'T-POINT BILGAON':(80.78694300,23.14094100),
'T-POINT CHAPARA RYT':(80.58545928,23.08014524),
'T-POINT CHHIRPANI':(80.79292165,23.05237797),
'T-POINT DEWARI KHURD':(80.67312130,23.19598630),
'T-POINT GHUSIYA RYT':(80.90378500,23.07576350),
'T-POINT GURAIYA MAL':(80.59908266,23.18713975),
'T-POINT JAMGAON':(80.86138437,23.20341692),
'T-POINT KASAISODA':(80.90404340,23.07691800),
'T-POINT KHAIRBHAGDU MAL':(80.60514030,23.21097136),
'T-POINT KOHANI DEWARI KALA':(80.52568940,23.19748640),
'T-POINT MATAKA RYT':(80.52742300,23.19785970),
'T-POINT RAIYPURA MAL':(80.64362040,23.28339400),
'T-POINT RAKHI MAL':(80.80623010,23.03466900),
'T-POINT SANGRAMPUR MAL':(80.80007300,23.20909040),
'T-POINT SARASWAHI':(80.61355590,23.26732980),
'T-POINT SILAHRI':(80.87171419,23.11176823)
}
