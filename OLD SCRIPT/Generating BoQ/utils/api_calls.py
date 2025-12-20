from .methods import *
def finding_road_name(row):
    print('*')
    lat, lon = row['st_Lat_Long_Auth'].split(',')[0], row['st_Lat_Long_Auth'].split(',')[1]
    roads_place_id_url = f"https://roads.googleapis.com/v1/nearestRoads?points={lat},{lon}&key={api_key}"
    response_pid = requests.get(roads_place_id_url)
    data = response_pid.json()
    road_name = []
    try:
        for loc in data['snappedPoints']:
            place_id = loc["placeId"]
            road_name_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name&key={api_key}"
            response_pname = requests.get(road_name_url)
            data = response_pname.json()
            if data['result']['name'] == 'Unnamed Road':
                road_name.append('')
            else:
                road_name.append(data['result']['name'])
        return ", ".join(road_name)
    except:
        return road_name


def finding_landmark(row, value):
    print('#')
    lat, lon = row['st_Lat_Long_Auth'].split(',')[0], row['st_Lat_Long_Auth'].split(',')[1]
    place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=20&type=establishment&key={api_key}"
    response = requests.get(place_url)
    data = response.json()
    landmark = []
    geometry_lat = []
    geometry_lng = []
    try:
        for r in data['results']:
            landmark.append(r['name'])
            geometry_lat.append(str(r['geometry']['location']['lat']))
            geometry_lng.append(str(r['geometry']['location']['lng']))
        if value == 'name':
            return ', '.join(landmark)
        if value == 'lat':
            return ','.join(geometry_lat)
        if value == 'lng':
            return ','.join(geometry_lng)
    except:
        return None


def finding_village(row):
    print('~')
    lat1, lon1 = row['st_Lat_Long_Auth'].split(',')[0], row['st_Lat_Long_Auth'].split(',')[1]
    place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat1},{lon1}&radius=20&key={api_key}"
    response_1 = requests.get(place_url)
    data_1 = response_1.json()
    lat2, lon2 = row['end_Lat_Long_Auth'].split(',')[0], row['end_Lat_Long_Auth'].split(',')[1]
    place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat2},{lon2}&radius=20&key={api_key}"
    response_2 = requests.get(place_url)
    data_2 = response_2.json()
    name = []
    try:
        for r in data_1['results']:
            name.append(r['name'])
        for r in data_2['results']:
            name.append(r['name'])
        return '-'.join(name).capitalize()
    except:
        return None