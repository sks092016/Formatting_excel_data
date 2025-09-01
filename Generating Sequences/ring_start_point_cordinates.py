import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Ater"

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
gps_shape_file = "References/Ater/gps.shp"
segments_shape_file = "References/Ater/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '78.64511197 26.74803793'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R1-C1':'78.61915761 26.59728580',
    'R3-C1':'78.72296229 26.58720297',
    'R4-C1':'78.82831742 26.67424983',
}
# Non Spur T-POINT SPANS points or Segments which are part of closed Ring
t_point_ring_spans = {
    't-point sora' : (78.63246879,26.66857775),
    't-point kanera':(78.56041825,26.72443601),
    't-point pawai': (78.64268375,26.63690462),
    't-point kadoura': (78.64111947,26.70137509),
    't-point jawasa':(78.73998289,26.62514675),
    't-point ghinochi':(78.66017348,26.73775721),
    't-point jouri kotwal':(78.70206957,26.71580772),
    't-point naripura': (78.86502726,26.66113963),
    't-point sakraya': (78.82831742,26.67424983),
    't-point goarkhurd':(78.61915761, 26.59728580),
    't-point ater': (78.66017348,26.73775721),
    't-point chouki':(78.72296229,26.58720297),
    't-point mudia khera':(78.76715200, 26.58879365),
    't-point dulhagan':(78.78377558,26.66745089),
    't-point rama':(78.81041939,26.72280601),
    't-point kosad':(78.80448961,26.73169951),
    't-point khipona':(78.68977252,26.75359663)

}
