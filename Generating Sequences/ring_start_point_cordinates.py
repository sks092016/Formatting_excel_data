import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Tirla"

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
gps_shape_file = "References/tirla/gps.shp"
segments_shape_file = "References/tirla/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '75.23870515 22.57863611 '

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R1-C1':'75.35220414 22.52282666',
    'R2-C1':'75.15416699 22.43300848',
    'R4-C1':'75.16149431 22.67089348',
}
t_point_ring_spans = {
't-point akoda':(75.19924214,22.69730199),
't-point chhota umriya':(75.30796026,22.49990651),
't-point dilavra':(75.35220414,22.52282666),
't-point nalawada':(75.16149431,22.67089348),
't-point kachhavda':(75.15416699,22.43300848),
't-point semlipura':(75.22490610,22.46208640),
't-point dedli-k':(75.12905994,22.46877437),
't-point khidkyakala':(75.21427971,22.48485651),

}

#------------KATANGI----------------------------------
# t_point_ring_spans = {
# 't-point arjuni':(79.89803840,21.74260090),
# 't-point bothwa':(79.77509740,21.69510070),
# 't-point digadha':(79.70198400,21.60545000),
# 't-point lakhanwada':(79.87971595,21.77768536),
# 't-point paraswada ghat':(79.80403900,21.65826500),
# 't-point sawagi':(79.85124970,21.74835880),
# }

# Non Spur T-POINT SPANS points or Segments which are part of closed Ring
# t_point_ring_spans = {
# 't-point badagaon' :(81.45114996,24.49484547),
# 't-point badwar':(81.54640512,24.49606327),
# 't-point banjari':(81.49937600,24.49446100),
# 't-point budawa':(81.50438400,24.55654300),
# 't-point chaudiyar':(81.48317200,24.45845600),
# 't-point gerui':(81.45100700,24.51699000),
# 't-point hardik no.2':(81.56694806,24.61301191),
# 't-point itaha':(81.31819800,24.61441800),
# 't-point jaraha':(81.64483000,24.53378800 ),
# 't-point kharahari':(81.38262008,24.63783091 ),
# 't-point khira':(81.43819564,24.58631400 ),
# 't-point kuiyan khurd':(81.54908373,24.60661923 ),
# 't-point lauwa urf lakshmanpur':(81.35390412,24.64396084 ),
# 't-point madhi':(81.48479172,24.60470097 ),
# 't-point methauri':(81.56110378,24.65191355 ),
# 't-point narraha':(81.58744113,24.56482988 ),
# 't-point navagaon':(81.38697700,24.61357600 ),
# 't-point new manikwar no.1':(81.60809217,24.56605400 ),
# 't-point paliya 351':(81.53322834,24.60899372 ),
# 't-point raghurajgarh':(81.63577167,24.62046290 ),
# 't-point ramnai':(81.40536169,24.56230873 ),
# 't-point raura':(81.43039800,24.58948400 ),
# 't-point sirsa':(81.64859100,24.59250400 ),
# 't-point sursa khurd':(81.48684400,24.59873800 ),
# 't-point tamradesh':(81.65514200,24.55692300 ),
# }
#-----------Balaghat------------
# t_point_ring_spans = {
# 't-point hirapur':(80.23990620,21.84237850),
# 't-point khursodi':(80.19631269,21.75354787)
# }
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
