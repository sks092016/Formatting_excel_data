import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Nalcha-2"

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
gps_shape_file = "References/Nalcha-2/gps.shp"
segments_shape_file = "References/Nalcha-2/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '75.40689047 22.41711255'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R1-C1':'75.40748687 22.45489178',
    'R1-C2':'75.46188940 22.54905006',
    'R2-C1':'75.39060694 22.38875472',
    'R4-C1':'75.52768683 22.53039567',
    'R5-C1':'75.48532425 22.46187597',
}
t_point_ring_spans = {
'T-POINT  KARAMTALAI TO BHILTALWADA':(75.31219244,22.43258909),
'T-POINT BANJARIPURA TO IMALIPURA':(75.48532425,22.46187597),
'T-POINT BHADKAY TO UMARPURA':(75.41228256,22.41670988),
'T-POINT BILLOD TO KUNVARSI':(75.52768683,22.53039567),
'T-POINT IMALIPURA TO CHOTA JAMANAYA':(75.56039200,22.47842000),
'T-POINT IMALIPURA TO PALASMAL':(75.54500689,22.40030316),
'T-POINT JIRAPURA TO SHIKHARPURA':(75.40748687,22.45489178),
'T-POINT MALIPURA TO TITIPURA':(75.39239537,22.36346011),
'T-POINT MEWAS JAMNIYA TO JAMANDA':(75.51660162,22.40995074),
'T-POINT MOGRABAW TO AAMKHO':(),
'T-POINT PANALA TO SULI BARDI':(),
'T-POINT RATWA TO UJJAINI':(),
'T-POINT SARAY  TO BHADKAY':(),
}
