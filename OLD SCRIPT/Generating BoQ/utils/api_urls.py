lat = 0
lon = 0
place_id = ''
api_key = ''
#API URLS
# GOOGLE
place_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=50&key={api_key}"
roads_place_id_url = f"https://roads.googleapis.com/v1/nearestRoads?points={lat},{lon}&key={api_key}"
road_name_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name&key={api_key}"

# OPENSM
url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
headers_village_name = {
    'User-Agent': 'village-lookup-script'
}
headers_road_name = {
    'User-Agent': 'road-name-fetcher-script'
}