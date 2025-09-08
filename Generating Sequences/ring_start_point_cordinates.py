import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Balaghat"

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
gps_shape_file = "References/Balaghat/gps.shp"
segments_shape_file = "References/Balaghat/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '80.19993800 21.80523700'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R1-C1':'80.25283162 21.78241961',
    'R2-C1':'80.23990620 21.84237850'
}
# Non Spur T-POINT SPANS points or Segments which are part of closed Ring
t_point_ring_spans = {
't-point hirapur':(80.23990620,21.84237850),
't-point khursodi':(80.19631269,21.75354787)
}
#--------BARWANI------------
# t_point_ring_spans = {
#  't-point  pakhalya':(74.89034000,21.90976400),
#  't-point hirkray':(74.89627354, 21.89715437),
#  't-point pakhalya':(74.89185993,21.90485223),
#  't-point panchpula uttar':(74.97021025,21.87474700)
# }

#-------MALHARGARH-2---------
# t_point_ring_spans = {
# 't-point admalya':(75.18708986,24.30950621),
# 't-point garnai':(75.27970416,24.27244578),
# 't-point hingoriya chota':(75.21341251,24.28393738),
# 't-point mundri': (75.10718700,24.13633900),
# 't-point piplia jodha':(75.24576032,24.22260185),
# 't-point ranayra':(75.18032061,24.21439208),
# 't-point semli':(74.91941979,24.18216178),
# 't-point sindhpan':  (75.11957849,24.16134956),
# }

#------ATER--------
# t_point_ring_spans = {
#     't-point sora' : (78.63246879,26.66857775),
#     't-point kanera':(78.56041825,26.72443601),
#     't-point pawai': (78.64268375,26.63690462),
#     't-point kadoura': (78.64111947,26.70137509),
#     't-point jawasa':(78.73998289,26.62514675),
#     't-point ghinochi':(78.66017348,26.73775721),
#     't-point jouri kotwal':(78.70206957,26.71580772),
#     't-point naripura': (78.86502726,26.66113963),
#     't-point sakraya': (78.82831742,26.67424983),
#     't-point goarkhurd':(78.61915761, 26.59728580),
#     't-point ater': (78.66017348,26.73775721),
#     't-point chouki':(78.72296229,26.58720297),
#     't-point mudia khera':(78.76715200, 26.58879365),
#     't-point dulhagan':(78.78377558,26.66745089),
#     't-point rama':(78.81041939,26.72280601),
#     't-point kosad':(78.80448961,26.73169951),
#     't-point khipona':(78.68977252,26.75359663)
#
# }
