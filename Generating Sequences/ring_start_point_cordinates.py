import logging
from pathlib import Path
from datetime import datetime

#---------- Configuring Logs -------------#
# Create a logs directory (optional)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

blockName = "Sardarpur"

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
gps_shape_file = "References/Sardarpur/gps.shp"
segments_shape_file = "References/Sardarpur/OFC_NEW.shp"

version = f"{blockName}-1"

## The Start cordinate for main Rings is BHQ ##
BHQ_CORDINATE = '74.97507875 22.66384565'

rings = {
    'R1': BHQ_CORDINATE,
    'R2': BHQ_CORDINATE,
    'R3': BHQ_CORDINATE,
    'R4': BHQ_CORDINATE,
    'R5': BHQ_CORDINATE,
    'R6': BHQ_CORDINATE,
    'R7': BHQ_CORDINATE,
    'R2-C1':'74.84955910 22.70766059',
    'R4-C1':'75.11757640 22.75349899',
    'R5-C1': '75.04541697 22.90231969',
    'R5-C2': '75.05868402 22.76570134',
    'R7-C1': '75.11926852 22.64514307',
}

t_point_ring_spans = {
't-point bhatiabardi to bardpada':(74.84955910,22.70766059),
't-point bodli to kothdakala':(75.05868402,22.76570134),
't-point chotiyabalod to chirakhan':(75.11757640,22.75349899),
't-point gumanpura to amaliya':(74.84228041,22.60623324),
't-point kasharpura to sagwal':(75.11926852,22.64514307),
't-point sajod to ksehanariya':(75.06693546,22.95151681),
't-point salwa to rajod':(75.04541697,22.90231969),
't-point dedla to kothdakala':(75.05868402,22.76570134),
't-point utava to chalnimata':(74.81466487,22.65155177),
}
# Morena
# t_point_ring_spans = {
# 't-point baretha':(78.07777500,26.59153400),
# 't-point basaiya':(78.12391650,26.52089485),
# 't-point girgoni':(78.09522331,26.44608708),
# 't-point hetampur':(77.93661789,26.60670586),
# 't-point kharagpur':(78.11950704,26.40032730),
# 't-point kishanpur':(78.04494369,26.48836827),
# 't-point nanka':(78.15470612,26.46774643),
# 't-point naupura':(78.14470700,26.45445000),
# 't-point palpura':(78.04197601,26.61803274),
# 't-point piprai':(77.93185000,26.62412000),
# 't-point seva':(78.10805843,26.35875297),
# }
# Gangev
# t_point_ring_spans = {
# 't-point amaha':(81.57659718,24.80165722),
# 't-point baans':(81.61099214,24.83125148),
# 't-point badokhar':(81.53324395,24.78550690),
# 't-point chauri':(81.50195115,24.79135102),
# 't-point dagardua':(81.59009100,24.79539500),
# 't-point kadaila':(81.42467165,24.68035748),
# 't-point keoti':(81.45369171,24.78553194),
# 't-point lalgaon':(81.53563979,24.81814018),
# 't-point lauri khurd':(81.63274336,24.82239743),
# 't-point marhi kalan':(81.57147671,24.68683759),
# 't-point mauhariya':(81.55933590,24.79243073),
# 't-point rampur':(81.47398500,24.68174600),
# 't-point rampurava':(81.48996581,24.75044064),
# 't-point raura':(81.46870236,24.75741242),
# 't-point sirsa':(81.53076553,24.70468954),
# 't-point siswa':(81.57661100,24.85130245),
# 't-point tikuri 32':(81.63237681,24.75887289),
# 't-point tiwani':(81.50903800,24.64675540),
# 't-point katheri':(81.46279157,24.63500084),
# }
#--Gandhwani ----
# t_point_ring_spans = {
# 't-point behadada':(75.02804651, 22.42619967),
# 't-point beladi':(75.01297987,22.56125296),
# 't-point bilda':(74.93359346,22.45485990),
# 't-point chunapya':(74.90894546,22.49822635),
# 't-point dhaydi':(74.89024722,22.43570129),
# 't-point gandwani':(75.00778990,22.34123982),
# 't-point kota':( 74.90614554,22.43167441),
# 't-point shyadi':(74.93315834,22.38362661),
# 't-point ledgaon':(75.03328458,22.45002534),
# 't-point pithanpur':(75.02320096,22.50571069),
# 't-point soyla':(75.07120436,22.39467985),
# }
# -------------------Tirla-------------------
# t_point_ring_spans = {
# 't-point akoda':(75.19924214,22.69730199),
# 't-point chhota umriya':(75.30796026,22.49990651),
# 't-point nalawada':(75.16149431,22.67089348),
# 't-point kachhavda':(75.15416699,22.43300848),
# 't-point semlipura':(75.22490610,22.46208640),
# 't-point dedli k':(75.12905994,22.46877437),
# 't-point khidkyakala':(75.18876341,22.46660346),
# 't-point dholahanuman':(75.21427971,22.48485651),
# 't-point advi':(75.35220414,22.52282666),
# 't-point musapura':(75.28055602,22.54911594)
# }
#------------KATANGI----------------------------------
# t_point_ring_spans = {
# 't-point arjuni':(79.89803840,21.74260090),
# 't-point bothwa':(79.77509740,21.69510070),
# 't-point digadha':(79.70198400,21.60545000),
# 't-point lakhanwada':(79.87971595,21.77768536),
# 't-point paraswada ghat':(79.80403900,21.65826500),
# 't-point sawagi':(79.85124970,21.74835880),
# }

# RAIPUR

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
# 't-point khira':(81.43819564,24.58631400),
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
# 't-point hardua':(81.49857651,24.48971313),
# 't-point mahsua':(81.43039800,24.58948400),
# 't-point padara':(81.42116399,24.62352166),
# 't-point purena':(81.34651900,24.56029800),
# 't-point ulahi kala':(81.59047983,24.59984761),
# 't-point khaira':(24.53982100, 81.51107100)
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

# t_point_ring_spans = {
#     't-point sora' : (78.63246879,26.66857775),
#     't-point kanera':(78.56041825,26.72443601),
#     't-point pawai': (78.64268375,26.63690462),
#     't-point kadoura': (78.64111947,26.70137509),
#     't-point jouri kotwal':(78.70206957,26.71580772),
#     't-point naripura': (78.86502726,26.66113963),
#     't-point goarkhurd':(78.61915761, 26.59728580),
#     't-point dulhagan':(78.78377558,26.66745089),
#     't-point rama':(78.81041939,26.72280601),
#     't-point kosad':(78.78706951,26.73502299),
#     't-point khipona':(78.68977252,26.75359663),
#     't-point jaari':(78.70380835,26.59018265),
#     't-point khaderi':(78.58997066,26.69138319),
#     't-point kishupura':(78.73823295,26.72569035),
#     't-point madhaiyapura':(78.80782887,26.68666335),
#     't-point pali':(78.62059573, 26.61485308)
# }
