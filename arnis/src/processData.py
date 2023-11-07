#!/usr/bin/env python
# coding: utf-8

# This file has been modified to be compatible with Irish geodata - by Lasith-Niro

from time import time
from cv2 import imwrite
import numpy as np
from random import randint

from .bresenham import bresenham_2d as bresenham
from .floodFill import floodFill

import pyproj
from pyproj import CRS

import geopandas as gpd
from rasterio.features import geometry_mask
from rasterio.transform import from_origin

# add tqdm

# def processData(data, args):
#     gdf = gpd.read_file("osm_data.geojson")
#     xmin, ymin, xmax, ymax = gdf.total_bounds
#     # print(gdf.total_bounds)
#     pixel_value = 0.00001
#     nodata_value = 0

#     category_mapping = {
#         'Building': 55,
#         'Road': 10,
#         'Water': 38,
#         'Land Use': 39,
#         'Leisure': 5,
#         'Amenity': 6,
#         'Natural': 7,
#         'Railway': 14,
#         'Power': 9,
#         'Other': 0
#     }
#     width = int((xmax - xmin) / pixel_value)
#     height = int((ymax - ymin) / pixel_value)
#     print(f"> width: {width}\n> height: {height}")
#     img = np.zeros((height, width, 1), dtype=np.uint8)
#     img.fill(nodata_value)
    

#     for index, row in gdf.iterrows():
#         geom = row['geometry']
#         category = row['category']

#         if category in category_mapping:
#             category_value = category_mapping[category]
#         else:
#             category_value = 0
        
#         print(f"> {index}/{len(gdf)}: {category} -> {category_value}")
        
#         shapes = [(geom, 1)]
#         mask = geometry_mask(shapes, out_shape=(height, width), transform=from_origin(xmin, ymax, pixel_value, pixel_value), invert=True)
#         img[mask] = category_value

#         # fill the inside of the polygon
#         for y in range(height):
#             for x in range(width):
#                 if mask[y][x] == True:
#                     img[y][x] = category_value
#     # save the image
#     imwrite("osm_data.png", img)
#     return np.flip(img, axis=1)
#     # return img
import math

ROTATION_DEGREES = -90.0  # This is the rotation of roads relative to true north.
ROTATION_RADIANS = math.radians(ROTATION_DEGREES)

INVERSE_ROTATION_MATRIX = np.array([[math.cos(ROTATION_RADIANS), math.sin(ROTATION_RADIANS), 0],
                                    [-math.sin(ROTATION_RADIANS), math.cos(ROTATION_RADIANS), 0],
                                    [0, 0, 1]])

# offset of the origin of the map in the EPSG:2157 coordinate system
BLOCK_OFFSET_X = 667000
BLOCK_OFFSET_Z = 6640000


def convert_lat_long_to_x_z(lat, long):
    """
    Converts the given latitude and longitude coordinates to Minecraft x and z coordinates. Uses a pipeline to convert
    from EPSG:4326 (lat/lon) to EPSG:2157.
    :param lat: the latitude coordinate
    :param long: the longitude coordinate
    :return: the Minecraft x and z coordinates of the given latitude and longitude
    """
    pipeline = "+proj=pipeline +step +proj=axisswap +order=2,1 +step +proj=unitconvert +xy_in=deg +xy_out=rad +step " \
               "+proj=ortho +lat_0=60.00 +lon_0=23.0000"
    transformer = pyproj.Transformer.from_pipeline(pipeline)
    transformed_x, transformed_z = transformer.transform(lat, long)
    x, z, _ = np.matmul(INVERSE_ROTATION_MATRIX, np.array([transformed_x - BLOCK_OFFSET_X,
                                                           transformed_z - BLOCK_OFFSET_Z,
                                                           1]))
    # z = -z  # flip z axis to match Minecraft
    return int(x), int(z)

def processData(data, args):
    print("Parsing data...")
    resDownScaler = float(args.scale)
    processingStartTime = time()

    # proj_string = "+proj=ortho +lat_0=60.00 +lon_0=23.0000"
    # ortho = CRS.from_proj4(proj_string)
    # ortho_proj = pyproj.Transformer.from_crs("epsg:4326", ortho, always_xy=True).transform
    
    source_crs = pyproj.CRS("epsg:4326")  # WGS 84, which is commonly used for latitude and longitude
    target_crs = pyproj.CRS("epsg:3785")  # Web Mercator (epsg:3785)
    transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)

    latitudes = []
    longitudes = []

    print(f"[INFO] Processing {len(data['elements'])} elements...")
    
    for element in data["elements"]:
        if element["type"] == "node":
            o_x, o_y = convert_lat_long_to_x_z(element["lat"], element["lon"])
            latitudes.append(o_x)
            longitudes.append(o_y)


            # ortho_x, ortho_y = transformer.transform(element['lat'], element['lon'])
            # # print(f"{element['lat']} -> {ortho_x}, {element['lon']} -> {ortho_y}")
            # latitudes.append(ortho_x)
            # longitudes.append(ortho_y)
        
    # latitudes, longitudes = np.array(latitudes), np.array(longitudes)
    min_lat, max_lat = min(latitudes), max(latitudes)
    min_lon, max_lon = min(longitudes), max(longitudes)

    print(f"> min_lat = {min_lat}")
    print(f"> max_lat = {max_lat}")
    print(f"> min_lon = {min_lon}")
    print(f"> max_lon = {max_lon}")

    greatestElementX = max_lat
    greatestElementY = max_lon
    lowestElemenetX = min_lat
    lowestElemenetY = min_lon
    greatestElementX -= lowestElemenetX
    greatestElementY -= lowestElemenetY

    # for element in data["elements"]:
    #     if(element['type'] == 'node'):
    #         ortho_x, ortho_y = ortho_proj(element['lon'], element['lat'])
    #         element['lon'] = ortho_x - min_lat
    #         element['lat'] = ortho_y - min_lon

    #         # print(f"{x0} -> {element['lat']}, {y0} -> {element['lon']}")

    #         # element["lat"] = int(str(element["lat"]).replace(".", ""))
    #         # element["lon"] = int(str(element["lon"]).replace(".", ""))

    #         if element["lat"] > greatestElementX:
    #             greatestElementX = element["lat"]
    #         if element["lon"] > greatestElementY:
    #             greatestElementY = element["lon"]

    # for element in data["elements"]:
    #     if element["type"] == "node":
    #         if len(str(element["lat"])) != len(str(greatestElementX)):
    #             for i in range(
    #                 0, len(str(greatestElementX)) - len(str(element["lat"]))
    #             ):
    #                 element["lat"] *= 10
                    
    #         if len(str(element["lon"])) != len(str(greatestElementY)):
    #             for i in range(
    #                 0, len(str(greatestElementY)) - len(str(element["lon"]))
    #             ):
    #                 element["lon"] *= 10
    
    # lowestElementX = greatestElementX
    # lowestElementY = greatestElementY
    

    # for element in data["elements"]:
    #     if element["type"] == "node":
    #         if element["lat"] < lowestElementX:
    #             lowestElementX = element["lat"]
    #         if element["lon"] < lowestElementY:
    #             lowestElementY = element["lon"]
    
    # nodesDict = {}
    # for element in data["elements"]:
    #     if element["type"] == "node":
    #         element["lat"] -= lowestElementX
    #         element["lon"] -= lowestElementY
    #         nodesDict[element["id"]] = [element["lat"], element["lon"]]

    # for element in data["elements"]:
    #     if(element['type'] == 'node'):
    #         ortho_x, ortho_y = ortho_proj(element['lon'], element['lat'])
    #         element['lat'] = ortho_x - min_lat
    #         element['lon'] = ortho_y - min_lon


    nodesDict = {}
    for element in data["elements"]:
        if(element['type'] == 'node'):
            # ortho_x, ortho_y = transformer.transform(element["lat"], element["lon"])
            # ortho_x -= lowestElemenetX
            # ortho_y -= lowestElemenetY
            ortho_x, ortho_y = convert_lat_long_to_x_z(element["lat"], element["lon"])
            ortho_x -= min_lat
            ortho_y -= min_lon
            nodesDict[element["id"]] = [ortho_x, ortho_y]


    orig_posDeterminationCoordX = 0
    orig_posDeterminationCoordY = 0
    map_posDeterminationCoordX = 0
    map_posDeterminationCoordY = 0
    maxBuilding = (0, 0)
    # greatestElementX = max_lat - min_lat
    # greatestElementY = max_lon - min_lon
    minBuilding = (greatestElementX, greatestElementY)
    
    nodeIndexList = []
    for i, element in enumerate(data["elements"]):
        if element["type"] == "way":
            for j, node in enumerate(element["nodes"]):
                element["nodes"][j] = nodesDict[node]

            if "tags" in element and "building" in element["tags"]:
                if orig_posDeterminationCoordX == 0:
                    orig_posDeterminationCoordX = element["nodes"][0][0]
                    orig_posDeterminationCoordY = element["nodes"][0][1]
                    map_posDeterminationCoordX = round(
                        element["nodes"][0][0] / resDownScaler
                    )
                    map_posDeterminationCoordY = round(
                        element["nodes"][0][1] / resDownScaler
                    )

                for coordinate in element["nodes"]:
                    cordX = round(coordinate[0] / resDownScaler)
                    cordY = round(coordinate[1] / resDownScaler)

                    if cordX > maxBuilding[0]:
                        maxBuilding = (cordX, maxBuilding[1])
                    elif cordX < minBuilding[0]:
                        minBuilding = (cordX, minBuilding[1])

                    if cordY > maxBuilding[1]:
                        maxBuilding = (maxBuilding[0], cordY)
                    elif cordY < minBuilding[1]:
                        minBuilding = (minBuilding[0], cordY)

        elif element["type"] == "node":
            nodeIndexList.append(i)

    for i in reversed(nodeIndexList):
        del data["elements"][i]

    minBuilding = (minBuilding[0] - 50, minBuilding[1] - 50)
    maxBuilding = (maxBuilding[0] + 50, maxBuilding[1] + 50)
    minMaxDistX = maxBuilding[0] - minBuilding[0] 
    minMaxDistY = maxBuilding[1] - minBuilding[1]

    for i, element in enumerate(data["elements"]):
        if element["type"] == "way":
            for j, node in enumerate(element["nodes"]):
                subtractedMinX = (
                    round(element["nodes"][j][0] / resDownScaler) - minBuilding[0]
                )
                subtractedMinY = (
                    round(element["nodes"][j][1] / resDownScaler) - minBuilding[1]
                )

                if subtractedMinX > 0 and subtractedMinX <= minMaxDistX:
                    element["nodes"][j][0] = subtractedMinX
                elif subtractedMinX <= 0 and not (
                    element["nodes"][j][0] > 0 and element["nodes"][j][0] <= minMaxDistX
                ):
                    element["nodes"][j][0] = 0
                if subtractedMinY > 0 and subtractedMinY <= minMaxDistY:
                    element["nodes"][j][1] = subtractedMinY
                elif subtractedMinY <= 0 and not (
                    element["nodes"][j][1] > 0 and element["nodes"][j][1] <= minMaxDistY
                ):
                    element["nodes"][j][1] = 0

                if element["nodes"][j][0] >= minMaxDistX:
                    element["nodes"][j][0] = minMaxDistX - 1
                if element["nodes"][j][1] >= minMaxDistY:
                    element["nodes"][j][1] = minMaxDistY - 1
    lowestElementX = min_lat
    lowestElementY = min_lon
    if args.debug:
        print(f"minMaxDistX: {minMaxDistX}")
        print(f"minMaxDistY: {minMaxDistY}")
        print(f"Greatest element X: {greatestElementX}")
        print(f"Greatest element Y: {greatestElementY}")
        print(f"Lowest element X: {lowestElementX}")
        print(f"Lowest element Y: {lowestElementY}")
        print(
            "Original position determination reference coordinates: "
            + f"{orig_posDeterminationCoordX}, {orig_posDeterminationCoordY}"
        )
        print(
            "Map position determination reference coordinates: "
            + f"{map_posDeterminationCoordX}, {map_posDeterminationCoordY}"
        )
        with open("arnis-debug-processed_data.json", "w", encoding="utf-8") as f:
            f.write(str(data))
        print("=========================================")
        print(minMaxDistY)
        print(minMaxDistX)
        print("=========================================")
    img = np.zeros(
        (
            minMaxDistY,
            minMaxDistX,
            1,
        ),
        np.uint8,
    )

    img.fill(0)
    imgLanduse = img.copy()

    print("Processing data...")

    ElementIncr = 0
    ElementsLen = len(data["elements"])
    lastProgressPercentage = 0
    for element in reversed(data["elements"]):
        progressPercentage = round(100 * (ElementIncr + 1) / ElementsLen)
        if (
            progressPercentage % 10 == 0
            and progressPercentage != lastProgressPercentage
        ):
            print(f"Element {ElementIncr + 1}/{ElementsLen} ({progressPercentage}%)")
            lastProgressPercentage = progressPercentage

        if element["type"] == "way" and "tags" in element:
            if "building" in element["tags"]:
                # print("Building")
                previousElement = (0, 0)
                cornerAddup = (0, 0, 0)
                currentBuilding = np.array([[0, 0]])
                for coordinate in element["nodes"]:
                    # try:
                    #     buildingHeight = int(element["tags"]["building:levels"])
                    #     if args.debug:
                    #         print(f"Building height [OSM]: {buildingHeight}")
                    # except Exception:
                    #     buildingHeight = 2
                    buildingHeight = element["tags"].get("building:levels", 2)
                    # if args.debug:
                    #     print(f"Building height [OSM]: {buildingHeight}")
                    if previousElement != (0, 0):
                        if "height" in element["tags"]:
                            if len(element["tags"]["height"]) >= 3:
                                buildingHeight = 9
                            elif len(element["tags"]["height"]) == 1:
                                buildingHeight = 2
                            elif element["tags"]["height"][:1] == "1":
                                buildingHeight = 3
                            elif element["tags"]["height"][:1] == "2":
                                buildingHeight = 6
                            else:
                                buildingHeight = 9

                        # if ("building:levels" in element["tags"] and element["tags"]["building:levels"].isnumeric() and int(float(element["tags"]["building:levels"])) <= 8 and int(float(element["tags"]["building:levels"])) >= 1 ):
                        #     buildingHeight = str(int(float(element["tags"]["building:levels"])) - 1)

                        for i in bresenham(
                            coordinate[0],
                            coordinate[1],
                            previousElement[0],
                            previousElement[1],
                        ):
                            if not (
                                str(img[i[1]][i[0]][0])[:1] == "6"
                                and img[i[1]][i[0]][0] > int("6" + str(buildingHeight))
                            ):
                                img[i[1]][i[0]] = int("6" + str(buildingHeight))

                        currentBuilding = np.append(
                            currentBuilding, [[coordinate[0], coordinate[1]]], axis=0
                        )

                        if not (
                            str(img[coordinate[1]][coordinate[0]][0])[:1] == "5"
                            and img[coordinate[1]][coordinate[0]][0]
                            > int("5" + str(buildingHeight))
                        ):
                            img[coordinate[1]][coordinate[0]] = int(
                                "5" + str(buildingHeight)
                            )

                        if not (
                            str(img[previousElement[1]][previousElement[0]][0])[:1]
                            == "5"
                            and img[previousElement[1]][previousElement[0]][0]
                            > int("5" + str(buildingHeight))
                        ):
                            img[previousElement[1]][previousElement[0]] = int(
                                "5" + str(buildingHeight)
                            )

                        cornerAddup = (
                            cornerAddup[0] + coordinate[0],
                            cornerAddup[1] + coordinate[1],
                            cornerAddup[2] + 1,
                        )
                    previousElement = (coordinate[0], coordinate[1])
            
                # print(f"Builiding: {buildingHeight}") 
                if args.debug:
                    if "building:levels" in element["tags"]:
                        print(f"Height [OSM]>> {element['tags']['building:levels']}    Height [MC]>> {buildingHeight}")

                if cornerAddup != (0, 0, 0):
                    img = floodFill(
                        img,
                        round(cornerAddup[1] / cornerAddup[2]),
                        round(cornerAddup[0] / cornerAddup[2]),
                        int("7" + str(buildingHeight)),
                        currentBuilding,
                        minMaxDistX,
                        minMaxDistY,
                        elementType="building",
                    )

            # water -> bridge
            elif "bridge" in element["tags"]:
                # print("Bridge")   
                previousElement = (0, 0)
                for coordinate in element["nodes"]:
                    if previousElement != (0, 0):
                        for i in bresenham(coordinate[0], coordinate[1], previousElement[0], previousElement[1]):
                            img[i[1]][i[0]] = 13
                    previousElement = (coordinate[0], coordinate[1])

            elif "highway" in element["tags"]:
                # print("Highway")
                previousElement = (0, 0)
                for coordinate in element["nodes"]:
                    highwayType = 10
                    if (previousElement != (0, 0) and element["tags"]["highway"] != "corridor" and previousElement != (0, 0) and element["tags"]["highway"] != "steps" and element["tags"]["highway"] != "bridge" ):
                        blockRange = 2
                        highwayType = 10

                        if (element["tags"]["highway"] == "path" or element["tags"]["highway"] == "footway"):
                            blockRange = 1
                            highwayType = 11
                        elif element["tags"]["highway"] == "motorway":
                            blockRange = 4
                        elif element["tags"]["highway"] == "track":
                            blockRange = 1
                            highwayType = 12
                        elif ( "lanes" in element["tags"] and element["tags"]["lanes"] != "1" and element["tags"]["lanes"] != "2" ):
                            blockRange = 4

                        for i in bresenham(coordinate[0], coordinate[1], previousElement[0], previousElement[1]):
                            for x in range(i[0] - blockRange, i[0] + blockRange + 1):
                                for y in range(i[1] - blockRange, i[1] + blockRange + 1):
                                    if ( x < minMaxDistX and y < minMaxDistY and img[y][x] == 0 ):
                                        img[y][x] = highwayType
                    previousElement = (coordinate[0], coordinate[1])
            

            elif "landuse" in element["tags"]:
                # print("Landuse")
                previousElement = (0, 0)
                cornerAddup = (0, 0, 0)
                currentLanduse = np.array([[0, 0]])
                for coordinate in element["nodes"]:                    
                    landuseType = 39
                    if (previousElement != (0, 0) and element["tags"]["landuse"] != "industrial" and element["tags"]["landuse"] != "residential"):
                        if (element["tags"]["landuse"] == "greenfield" or element["tags"]["landuse"] == "meadow" or element["tags"]["landuse"] == "grass"):
                            landuseType = 30
                        elif element["tags"]["landuse"] == "farmland":
                            landuseType = 31
                        elif element["tags"]["landuse"] == "forest":
                            landuseType = 32
                        elif element["tags"]["landuse"] == "cemetery":
                            landuseType = 33
                        elif element["tags"]["landuse"] == "beach":
                            landuseType = 34

                        # print(f'LandUseName: {element["tags"]["landuse"]}')
                        # print(f"LanduseType: {landuseType}")

                        for i in bresenham( coordinate[0],coordinate[1],previousElement[0],previousElement[1],):
                            if imgLanduse[i[1]][i[0]] == 0:
                                imgLanduse[i[1]][i[0]] = landuseType

                        currentLanduse = np.append(
                            currentLanduse, [[coordinate[0], coordinate[1]]], axis=0
                        )
                        cornerAddup = (
                            cornerAddup[0] + coordinate[0],
                            cornerAddup[1] + coordinate[1],
                            cornerAddup[2] + 1,
                        )
                    previousElement = (coordinate[0], coordinate[1])
                    # print(f"Landuse: {landuseType}")

                if cornerAddup != (0, 0, 0):
                    imgLanduse = floodFill(
                        imgLanduse,
                        round(cornerAddup[1] / cornerAddup[2]),
                        round(cornerAddup[0] / cornerAddup[2]),
                        landuseType,
                        currentLanduse,
                        minMaxDistX,
                        minMaxDistY,
                    )


            elif "natural" in element["tags"]:
                # print("Natural")
                previousElement = (0, 0)
                cornerAddup = (0, 0, 0)
                currentNatural = np.array([[0, 0]])
                for coordinate in element["nodes"]:
                    naturalType = 39
                    if previousElement != (0, 0):
                        if (
                            element["tags"]["natural"] == "scrub"
                            or element["tags"]["natural"] == "grassland"
                        ):
                            naturalType = 30
                        elif (
                            element["tags"]["natural"] == "beach"
                            or element["tags"]["natural"] == "sand"
                        ):
                            naturalType = 34
                        elif (
                            element["tags"]["natural"] == "wood"
                            or element["tags"]["natural"] == "tree_row"
                        ):
                            naturalType = 32
                        elif element["tags"]["natural"] == "wetland":
                            naturalType = 35
                        elif element["tags"]["natural"] == "water":
                            naturalType = 38

                        for i in bresenham(
                            coordinate[0],
                            coordinate[1],
                            previousElement[0],
                            previousElement[1],
                        ):
                            if imgLanduse[i[1]][i[0]] == 0:
                                imgLanduse[i[1]][i[0]] = naturalType

                        currentNatural = np.append(
                            currentNatural, [[coordinate[0], coordinate[1]]], axis=0
                        )
                        cornerAddup = (
                            cornerAddup[0] + coordinate[0],
                            cornerAddup[1] + coordinate[1],
                            cornerAddup[2] + 1,
                        )
                    previousElement = (coordinate[0], coordinate[1])

                if cornerAddup != (0, 0, 0):
                    if naturalType != 32:
                        imgLanduse = floodFill(
                            imgLanduse,
                            round(cornerAddup[1] / cornerAddup[2]),
                            round(cornerAddup[0] / cornerAddup[2]),
                            naturalType,
                            currentNatural,
                            minMaxDistX,
                            minMaxDistY,
                        )
                    else:
                        imgLanduse = floodFill(
                            imgLanduse,
                            round(cornerAddup[1] / cornerAddup[2]),
                            round(cornerAddup[0] / cornerAddup[2]),
                            naturalType,
                            currentNatural,
                            minMaxDistX,
                            minMaxDistY,
                            elementType="tree_row",
                        )

            elif "leisure" in element["tags"]:
                # print("Leisure")
                previousElement = (0, 0)
                cornerAddup = (0, 0, 0)
                currentLeisure = np.array([[0, 0]])
                for coordinate in element["nodes"]:
                    leisureType = 39
                    if (
                        previousElement != (0, 0)
                        and element["tags"]["leisure"] != "marina"
                    ):
                        if (
                            element["tags"]["leisure"] == "park"
                            or element["tags"]["leisure"] == "playground"
                            or element["tags"]["leisure"] == "garden"
                        ):
                            leisureType = 30
                        elif element["tags"]["leisure"] == "pitch":
                            leisureType = 36
                        elif element["tags"]["leisure"] == "swimming_pool":
                            leisureType = 37

                        for i in bresenham(
                            coordinate[0],
                            coordinate[1],
                            previousElement[0],
                            previousElement[1],
                        ):
                            if imgLanduse[i[1]][i[0]] == 0:
                                imgLanduse[i[1]][i[0]] = leisureType

                        currentLeisure = np.append(
                            currentLeisure, [[coordinate[0], coordinate[1]]], axis=0
                        )
                        cornerAddup = (
                            cornerAddup[0] + coordinate[0],
                            cornerAddup[1] + coordinate[1],
                            cornerAddup[2] + 1,
                        )
                    previousElement = (coordinate[0], coordinate[1])

                if cornerAddup != (0, 0, 0):
                    imgLanduse = floodFill(
                        imgLanduse,
                        round(cornerAddup[1] / cornerAddup[2]),
                        round(cornerAddup[0] / cornerAddup[2]),
                        leisureType,
                        currentLeisure,
                        minMaxDistX,
                        minMaxDistY,
                    )

            elif "waterway" in element["tags"]:
                # print("Waterway")
                previousElement = (0, 0)
                for coordinate in element["nodes"]:
                    if previousElement != (0, 0) and not (
                        "layer" in element["tags"]
                        and (
                            element["tags"]["layer"] == "-1"
                            or element["tags"]["layer"] == "-2"
                            or element["tags"]["layer"] != "-3"
                        )
                    ):
                        # managing the width of the waterway
                        # TODO: how to map without the width tag?
                        waterwayWidth = 15
                        if "width" in element["tags"]:
                            try:
                                waterwayWidth = int(element["tags"]["width"])
                                if args.debug:
                                    print(f"Waterway width [OSM]: {waterwayWidth}")
                            except Exception:
                                waterwayWidth = int(float(element["tags"]["width"]))

                        for i in bresenham(
                            coordinate[0],
                            coordinate[1],
                            previousElement[0],
                            previousElement[1],
                        ):
                            for x in range(
                                round(i[0] - waterwayWidth / 2),
                                round(i[0] + waterwayWidth + 1 / 2),
                            ):
                                for y in range(
                                    round(i[1] - waterwayWidth / 2),
                                    round(i[1] + waterwayWidth + 1 / 2),
                                ):
                                    if (
                                        x < minMaxDistX
                                        and y < minMaxDistY
                                        and img[y][x] != 13
                                    ):
                                        img[y][x] = 38
                    previousElement = (coordinate[0], coordinate[1])

            elif "amenity" in element["tags"]:
                # print("Amenity")
                previousElement = (0, 0)
                cornerAddup = (0, 0, 0)
                currentAmenity = np.array([[0, 0]])
                amenityType = 20
                for coordinate in element["nodes"]:
                    if previousElement != (0, 0) and (
                        element["tags"]["amenity"] == "parking"
                        or element["tags"]["amenity"] == "fountain"
                    ):
                        if element["tags"]["amenity"] == "parking":
                            amenityType = 20
                        elif element["tags"]["amenity"] == "fountain":
                            amenityType = 21

                        for i in bresenham(
                            coordinate[0],
                            coordinate[1],
                            previousElement[0],
                            previousElement[1],
                        ):
                            if imgLanduse[i[1]][i[0]] == 0:
                                imgLanduse[i[1]][i[0]] = amenityType

                        currentAmenity = np.append(
                            currentAmenity, [[coordinate[0], coordinate[1]]], axis=0
                        )
                        cornerAddup = (
                            cornerAddup[0] + coordinate[0],
                            cornerAddup[1] + coordinate[1],
                            cornerAddup[2] + 1,
                        )
                    previousElement = (coordinate[0], coordinate[1])

                if amenityType == 21:
                    amenityType = 37
                if cornerAddup != (0, 0, 0):
                    imgLanduse = floodFill(
                        imgLanduse,
                        round(cornerAddup[1] / cornerAddup[2]),
                        round(cornerAddup[0] / cornerAddup[2]),
                        amenityType,
                        currentAmenity,
                        minMaxDistX,
                        minMaxDistY,
                    )
            

            elif "railway" in element["tags"]:
                # print("Railway")
                previousElement = (0, 0)
                for coordinate in element["nodes"]:
                    if (
                        previousElement != (0, 0)
                        and element["tags"]["railway"] != "proposed"
                    ):
                        for i in bresenham(
                            coordinate[0] - 2,
                            coordinate[1] - 2,
                            previousElement[0] - 2,
                            previousElement[1] - 2,
                        ):
                            if i[0] < minMaxDistX and i[1] < minMaxDistY:
                                img[i[1]][i[0]] = 14
                        for i in bresenham(
                            coordinate[0] + 1,
                            coordinate[1] + 1,
                            previousElement[0] + 1,
                            previousElement[1] + 1,
                        ):
                            if i[0] < minMaxDistX and i[1] < minMaxDistY:
                                img[i[1]][i[0]] = 14
                    previousElement = (coordinate[0], coordinate[1])

            elif "barrier" in element["tags"]:
                # print("Barrier")
                previousElement = (0, 0)
                for coordinate in element["nodes"]:
                    if previousElement != (0, 0):
                        wallHeight = 1
                        if (
                            "height" in element["tags"]
                            and str(element["tags"]["height"])
                            .replace(".", "")
                            .isnumeric()
                        ):
                            wallHeight = round(int(float(element["tags"]["height"])))
                        if wallHeight > 3:
                            wallHeight = 2

                        for i in bresenham(
                            coordinate[0],
                            coordinate[1],
                            previousElement[0],
                            previousElement[1],
                        ):
                            if (
                                str(img[i[1]][i[0]][0])[:1] != 5
                                and str(img[i[1]][i[0]][0])[:1] != 6
                                and str(img[i[1]][i[0]][0])[:1] != 7
                            ):
                                img[i[1]][i[0]] = int("2" + str((wallHeight + 1)))
                    previousElement = (coordinate[0], coordinate[1])
                    
            ElementIncr += 1

    print("Calculating layers...")
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if imgLanduse[x][y] != 0 and img[x][y] == 0:
                img[x][y] = imgLanduse[x][y]

    print(
        f"Processing finished in {(time() - processingStartTime):.2f} seconds"
        + f"({((time() - processingStartTime) / 60):.2f} minutes)"
    )

    img = np.fliplr(img)
    img = np.rot90(img, 1)
    # flip
    # img2 = np.rot90(img2, 1) # need to check here
    
    if args.debug:
        imwrite("arnis-debug-map.png", img)
        print("[INFO] Map image saved to arnis-debug-map.png")
    # flip and return the image
    return img
