import os
import requests
from random import choice
import overpy
import json
import geojson

# This file has been modified to be compatible with Irish geodata - by Lasith-Niro
# The original file can be found at https://github.com/louis-e/arnis.git
 
 
# for bbox
def getData(bbox, debug):
    print("Fetching data...")
    bbox = bbox.split(",")
    # convert bbox to float
    bbox = [float(i) for i in bbox]
    server = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
        [out:json][bbox:{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}];
        ( 
        node; 
        way;
        relation;
        );
        (._;>;);
        out;
        """
    if debug:
        print(overpass_query)
    try:
        data = requests.get(server, params={"data": overpass_query}).json()

        if len(data["elements"]) == 0:
            print("Error! No data available")
            os._exit(1)
    except Exception as e:
        if "The server is probably too busy to handle your request." in str(e):
            print("Error! OSM server overloaded")
        elif "Dispatcher_Client::request_read_and_idx::rate_limited" in str(e):
            print("Error! IP rate limited")
        else:
            print(f"Error! {e}")
        os._exit(1)

    if debug:
        out_file = f"data/osm_{'_'.join(map(str, bbox))}_raw_data.json"
        with open(out_file, "w") as f:
            json.dump(data, f)
    return data



# this is for GeoJson
# def getData(bbox, debug):
#     bbox = bbox.split(",")
#     # counting the number of features
#     features = 0

#     # Define your Overpass query to retrieve OSM data within the bbox
#     overpass_query = f"""
#     [bbox:{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}];
#     ( 
#     way["highway"];
#     way["building"];
#     way["water"];
#     way["landuse"];
#     relation["building"];
#     );
#     /*added by auto repair*/
#     (._;>;);
#     /*end of auto repair*/
#     out body;
#     """

#     # Initialize the Overpass API client
#     api = overpy.Overpass()

#     # Define a mapping of OSM tags to categories
#     tag_category_mapping = {
#         'building': 'Building',
#         'highway': 'Road',
#         'water': 'Water',
#         'landuse': 'Land Use',
#         'leisure': 'Leisure',
#         'amenity': 'Amenity',
#         'natural': 'Natural',
#         'railway': 'Railway',
#         'power': 'Power',
#         'beach': 'Beach',
#         'farmland': 'Farmland',
#         'meadow': 'Meadow',
#         'park': 'Park',
#         'forest': 'Forest',
#         'parking': 'Parking',
#         'railway': 'Railway',
#         'bridge': 'Bridge',
#         'street': 'Street',
#         'footway': 'Footway'
#         # Add more tags and categories as needed
#     }

#     # Execute the Overpass query and save the result as a GeoJSON file
#     osm_data = api.query(overpass_query)

#     # Convert the result to GeoJSON format
#     geojson_data = {
#         "type": "FeatureCollection",
#         "features": []
#     }

#     for way in osm_data.ways:
#         # Initialize category to 'Other' as a default
#         category = 'Other'

#         for tag in way.tags:
#             # Check if the tag is in the mapping, and assign the corresponding category
#             if tag in tag_category_mapping:
#                 category = tag_category_mapping[tag]
#                 features += 1
#             print(f"{way.id} -> {category}")

#         feature = {
#             "type": "Feature",
#             "geometry": {
#                 "type": "LineString",
#                 "coordinates": [(float(node.lon), float(node.lat)) for node in way.nodes]
#             },
#             "properties": {
#                 "category": category,
#                 "tags": way.tags
#             }
#         }
#         geojson_data["features"].append(feature)

#     print(f"Total number of features: {features}")
#     # Save the result as a GeoJSON file
#     with open("osm_data.geojson", "w") as f:
#         json.dump(geojson_data, f)
#     return geojson_data

# # original data parser
# def getData(city, state, country, debug):
#     print("Fetching data...")
#     api_servers = [
#         "https://overpass-api.de/api/interpreter",
#         "https://lz4.overpass-api.de/api/interpreter",
#         "https://z.overpass-api.de/api/interpreter",
#         "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
#         "https://overpass.openstreetmap.ru/api/interpreter",
#         "https://overpass.kumi.systems/api/interpreter",
#     ]
#     url = choice(api_servers)
#     query1 = (
#         """
#         [out:json];
#         area[name="""
#         + '"'
#         + city
#         + '"'
#         + """]->.city;
#         area[name="""
#         + '"'
#         + state
#         + '"'
#         + """]->.state;
#         area[name="""
#         + '"'
#         + country
#         + '"'
#         + """]->.country;
#         way(area.country)(area.state)(area.city)[!power][!place][!ferry];
#         (._;>;);
#         out;
#     """
#     )

#     print(f"Chosen server: {url}")
#     try:
#         data = requests.get(url, params={"data": query1}).json()

#         if len(data["elements"]) == 0:
#             print("Error! No data available")
#             os._exit(1)
#     except Exception as e:
#         if "The server is probably too busy to handle your request." in str(e):
#             print("Error! OSM server overloaded")
#         elif "Dispatcher_Client::request_read_and_idx::rate_limited" in str(e):
#             print("Error! IP rate limited")
#         else:
#             print(f"Error! {e}")
#         os._exit(1)

#     if debug:
#         with open("arnis-debug-raw_data.json", "w", encoding="utf-8") as f:
#             f.write(str(data))
#     return data
