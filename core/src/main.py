#!/usr/bin/env python

# Copyright 2022 by louis-e, https://github.com/louis-e/.
# MIT License
# Please see the LICENSE file that should have been included as part of this package.

# This file has been modified to be compatible with Irish geodata
# Modified by Lasith-Niro

import os
import sys
from textwrap import fill
import time
import gc
import argparse
import anvil
import requests
import json
from random import randint
from math import floor
import numpy as np
from tqdm import tqdm
from .getData import getData
from .processData import processData
from .config import *



parser = argparse.ArgumentParser(
    description="Arnis - Generate cities from real life in Minecraft using Python"
)
# parser.add_argument("--city", dest="city", help="Name of the city")
# parser.add_argument("--state", dest="state", help="Name of the state")
# parser.add_argument("--country", dest="country", help="Name of the country")


parser.add_argument("--bbox", dest="bbox", help="Bounding box of the city")
parser.add_argument("--path", dest="path", help="Path to the minecraft world")
parser.add_argument("--scale", dest="scale", help="Scale of the city")
parser.add_argument("--z", dest="z", help="Initial z coordinate", default=0, type=int)

parser.add_argument(
    "--debug",
    dest="debug",
    default=False,
    action="store_true",
    help="Enable debug mode",
)

args = parser.parse_args()


if args.bbox is None or args.path is None:
    print("Error! Missing arguments")
    os._exit(1)

gc.collect()
np.seterr(all="raise")
np.set_printoptions(threshold=sys.maxsize)
processStartTime = time.time()

regions = {}
for x in range(0, 3):
    for z in range(0, 3):
        regions["r." + str(x) + "." + str(z)] = anvil.EmptyRegion(0, 0)


def setBlock(block, x, y, z):
    flooredX = floor(x / 512)
    flooredZ = floor(z / 512)
    identifier = "r." + str(flooredX) + "." + str(flooredZ)
    if identifier not in regions:
        regions[identifier] = anvil.EmptyRegion(0, 0)
    regions[identifier].set_block(block, x - flooredX * 512, y, z - flooredZ * 512)

def setBlockwithElevation(block, x, y, z, elevation):
    elevation = int(elevation)
    print(f"elevation: {elevation}")
    if elevation < MIN_HEIGHT:
        elevation = MIN_HEIGHT
    elif elevation > MAX_HEIGHT:
        elevation = MAX_HEIGHT
    flooredX = floor(x / 512)
    flooredZ = floor(z / 512)
    identifier = "r." + str(flooredX) + "." + str(flooredZ)
    if identifier not in regions:
        regions[identifier] = anvil.EmptyRegion(0, 0)
    regions[identifier].set_block(block, x - flooredX * 512, y + elevation, z - flooredZ * 512)

def fillBlocks(block, x1, y1, z1, x2, y2, z2):
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                if not (x == x2 + 1 or y == y2 + 1 or z == z2 + 1):
                    setBlock(block, x, y, z)


mcWorldPath = args.path
# if mcWorldPath/region is exists, ask to delete it
if os.path.exists(mcWorldPath + "/region"):
    # ask in red

    print(
        f"\033[91m[WARN] \033[0m {mcWorldPath}/region is exists.\n"
        + "Do you want to delete it? (y/n) ",
        end="",
    )

    # TODO: wait 10 seconds for answer and if not answered, delete it
    answer = input()
    if answer == "y":
        for filename in os.listdir(mcWorldPath + "/region"):
            os.remove(mcWorldPath + "/region/" + filename)
    else:
        print("Aborting...")
        os._exit(1)

    #automatically press y and enter to delete it

# if mcWorldPath is not exists make a new dirs for mcWorldPath and region
if not (os.path.exists(mcWorldPath)):
    os.makedirs(mcWorldPath + "/region")

if mcWorldPath[-1] == "/":
    mcWorldPath = mcWorldPath[:-1]


def saveRegion(region="all"):
    if region == "all":
        for key in regions:
            regions[key].save(mcWorldPath + "/region/" + key + ".mca")
            print(f"Saved {key}")
    else:
        regions[region].save(mcWorldPath + "/region/" + region + ".mca")
        print(f"Saved {region}")

def get_height_from_flask_app(lat, lon):
    url = "http://127.0.0.1:5000/get_height"

    try:
        response = requests.post(url)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        print("API is up and running!")
    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to connect to the API. {e}")
        sys.exit(1)

    try:
        # Make a POST request to get the height
        response = requests.post(url, data={'lat': lat, 'lon': lon})

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                height = float(data['height'])
                # print(f"Height at latitude {lat}, longitude {lon}: {height}")
            else:
                print(f"Error: {data['error']}")
        else:
            print(f"Failed to make the request. Status code: {response.status_code}")
        return height
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 0


def run():
    if not (os.path.exists(mcWorldPath + "/region")):
        print("[WARN] No Minecraft world found at given path")
        os.makedirs(mcWorldPath + "/region")

    get_height_from_flask_app(0,0)

    # rawdata = getData(args.city, args.state, args.country, args.debug)
    # import json
    # geojson_path = r"..\..\dublin.json"
    # with open(geojson_path, 'r') as f:
    #     s = f.read()
    #     s = s.replace('\'','\"')
    #     rawdata = json.loads(s)

    raw_data_file = r"arnis-debug-raw_data.json"
    # check if the raw_data_file exists
    if os.path.exists(raw_data_file):
        print(f"[INFO] \033[91m [OFFLINE] \033[0m Reading raw data from {raw_data_file}")
        # if exists, read the json file
        with open(raw_data_file, "r") as f:
            rawdata = json.loads(f.read())
    else:
        # crawl data from OSM using bbox
        rawdata = getData(args.bbox, args.debug)

    # create an image array from rawdata
    # imgarray = processData(rawdata, args)
    imgarray, imgTerrain = processData(rawdata, args)
    
    print("[INFO] Generating minecraft world...")

    x = 0
    z = 0
    doorIncrement = 0
    ElementIncr = 0
    ElementsLen = len(imgarray)
    lastProgressPercentage = 0
    # v3
    for row in tqdm(imgTerrain, desc="Generating terrain", total=len(imgTerrain), unit="row"):
        # print(row)
        for col in row:
            # Fill blocks from min_height to col
            setBlock(stone, x, col[0], z)
            # print(f"approximated height: {col[0]}")
            z += 1
        x += 1
        z = 0

    for i in tqdm(imgarray, desc="Generating city", total=len(imgarray), unit="row"):
        progressPercentage = round(100 * (ElementIncr + 1) / ElementsLen)
        if (
            progressPercentage % 10 == 0
            and progressPercentage != lastProgressPercentage
        ):
            print(f"Pixel {ElementIncr + 1}/{ElementsLen} ({progressPercentage}%)")
            lastProgressPercentage = progressPercentage

        z = 0

        for j in i:
            # v2
            # try:
            #     node_mapper_key = f"({x},{z})"
            #     xx, zz = node_mapper[node_mapper_key]
            #     xy_mapper_key = f"({xx},{zz})"
            #     lat, lon = xy_mapper[xy_mapper_key]
            #     elevation = get_height_from_flask_app(lat, lon)
            #     print(f"lat: {lat}, lon: {lon}, elevation: {elevation}")
            #     setBlockwithElevation(stone, x, 0, z, elevation)
            # except:
            #     print(f"Error: x: {x}, z: {z}")
            #     pass
            
            
            # v1: setting the terrain
            # try:
            #     for elevation in range(0, elevation_map[x, z]):
            #         setBlockwithElevation(stone, x, 0, z, elevation)
            # except:
            #     print(f"Error: x: {x}, z: {z}")
            #     pass

                
            setBlock(dirt, x, 0, z)
            if j == 0:  # Ground
                setBlock(light_gray_concrete, x, 1, z)                
            elif j == 10:  # Street (road)
                setBlock(black_concrete, x, 1, z)
                setBlock(air, x, 2, z)
            elif j == 11:  # Footway
                setBlock(gray_concrete, x, 1, z)
                setBlock(air, x, 2, z)
            elif j == 12:  # Natural path
                setBlock(cobblestone, x, 1, z)
            elif j == 14:  # Railway
                setBlock(iron_block, x, 2, z)
            elif j == 20:  # Parking
                setBlock(gray_concrete, x, 1, z)
            elif j == 21:  # Fountain border
                setBlock(light_gray_concrete, x, 2, z)
                setBlock(white_concrete, x, 1, z)
            elif j >= 22 and j <= 24:  # Fence
                if str(j)[-1] == "2" or int(str(j[0])[-1]) == 2:
                    setBlock(cobblestone_wall, x, 2, z)
                else:
                    fillBlocks(cobblestone, x, 2, z, x, int(str(j[0])[-1]), z)

                setBlock(grass_block, x, 1, z)
            elif j == 30:  # Meadow
                setBlock(grass_block, x, 1, z)
                randomChoice = randint(0, 2)
                if randomChoice == 0 or randomChoice == 1:
                    setBlock(grass, x, 2, z)
            elif j == 31:  # Farmland
                randomChoice = randint(0, 16)
                if randomChoice == 0:
                    setBlock(water, x, 1, z)
                elif randomChoice >= 1 and randomChoice <= 4:
                    if args.debug: 
                        print("[DEBUG] Adding a tree to farmland...")
                    addTree(x, z)
                else:
                    setBlock(farmland, x, 1, z)
                    randomChoice = randint(0, 2)
                    if randomChoice == 0:
                        setBlock(wheat, x, 2, z)
                    elif randomChoice == 1:
                        setBlock(carrots, x, 2, z)
                    else:
                        setBlock(potatoes, x, 2, z)
            elif j == 32:  # Forest
                setBlock(grass_block, x, 1, z)
                randomChoice = randint(0, 8)
                if args.debug:
                    print(f"[DEBUG] Random choice: {randomChoice}")
                if randomChoice >= 0 and randomChoice <= 5:
                    setBlock(grass, x, 2, z)
                else:
                    if args.debug: 
                        print("[DEBUG] Adding a tree to forest...")
                    addTree(x, z)
            elif j == 33:  # Cemetery
                setBlock(podzol, x, 1, z)
                randomChoice = randint(0, 100)
                if randomChoice == 0:
                    setBlock(cobblestone, x - 1, 2, z)
                    setBlock(stone_brick_slab, x - 1, 3, z)
                    setBlock(stone_brick_slab, x, 2, z)
                    setBlock(stone_brick_slab, x + 1, 2, z)
                elif randomChoice == 1:
                    setBlock(cobblestone, x, 2, z - 1)
                    setBlock(stone_brick_slab, x, 3, z - 1)
                    setBlock(stone_brick_slab, x, 2, z)
                    setBlock(stone_brick_slab, x, 2, z + 1)
                elif randomChoice == 2 or randomChoice == 3:
                    setBlock(red_flower, x, 2, z)
            elif j == 34:  # Beach
                setBlock(sand, x, 1, z)
            elif j == 35:  # Wetland
                randomChoice = randint(0, 2)
                if randomChoice == 0:
                    setBlock(grass_block, x, 1, z)
                else:
                    setBlock(water, x, 1, z)
            elif j == 36:  # Pitch
                setBlock(green_stained_hardened_clay, x, 1, z)
            elif j == 37:  # Swimming pool
                setBlock(water, x, 1, z)
                setBlock(white_concrete, x, 0, z)
            elif j == 38:  # Water
                setBlock(water, x, 1, z)
            elif j == 13:  # Bridge
                addBridge(x, z)
            elif j == 39:  # Raw grass
                setBlock(grass_block, x, 1, z)
            elif j >= 50 and j <= 59:  # House corner
                building_height = 5
                if j == 51:
                    building_height = 8
                elif j == 52:
                    building_height = 11
                elif j == 53:
                    building_height = 14
                elif j == 54:
                    building_height = 17
                elif j == 55:
                    building_height = 20
                elif j == 56:
                    building_height = 23
                elif j == 57:
                    building_height = 26
                elif j == 58:
                    building_height = 29
                elif j == 59:
                    building_height = 32

                fillBlocks(white_concrete, x, 1, z, x, building_height, z)

            elif j >= 60 and j <= 69:  # House wall
                building_height = 4
                if j == 61:
                    building_height = 7
                elif j == 62:
                    building_height = 10
                elif j == 63:
                    building_height = 13
                elif j == 64:
                    building_height = 16
                elif j == 65:
                    building_height = 19
                elif j == 66:
                    building_height = 22
                elif j == 67:
                    building_height = 25
                elif j == 68:
                    building_height = 28
                elif j == 69:
                    building_height = 31

                if doorIncrement == 25:
                    fillBlocks(white_stained_glass, x, 4, z, x, building_height, z)
                    setBlock(white_concrete, x, 1, z)
                    setBlock(dark_oak_door_lower, x, 2, z)
                    setBlock(dark_oak_door_upper, x, 3, z)
                    doorIncrement = 0
                else:
                    fillBlocks(white_concrete, x, 1, z, x, 2, z)
                    fillBlocks(white_stained_glass, x, 3, z, x, building_height, z)
                doorIncrement += 1
                setBlock(white_concrete, x, building_height + 1, z)
            elif j >= 70 and j <= 79:  # House interior
                if j >= 70:
                    setBlock(white_concrete, x, 5, z)
                    if j >= 71:
                        setBlock(white_concrete, x, 8, z)
                        if j >= 72:
                            setBlock(white_concrete, x, 11, z)
                            if j >= 73:
                                setBlock(white_concrete, x, 14, z)
                                if j >= 74:
                                    setBlock(white_concrete, x, 17, z)
                                    if j >= 75:
                                        setBlock(white_concrete, x, 20, z)
                                        if j >= 76:
                                            setBlock(white_concrete, x, 23, z)
                                            if j >= 77:
                                                setBlock(white_concrete, x, 26, z)
                                                if j >= 78:
                                                    setBlock(white_concrete, x, 29, z)
                                                    if j >= 78:
                                                        setBlock(
                                                            white_concrete, x, 32, z
                                                        )

                setBlock(glowstone, x, 1, z)

            z += 1
        x += 1
        ElementIncr += 1

    print("Saving minecraft world...")
    saveRegion()
    print(
        f"Done! Finished in {(time.time() - processStartTime):.2f} "
        + f"seconds ({((time.time() - processStartTime) / 60):.2f} minutes)"
    )
    os._exit(0)

def addBridge(x, z):
    setBlock(light_gray_concrete, x, 2, z)
    setBlock(light_gray_concrete, x - 1, 2, z - 1)
    setBlock(light_gray_concrete, x + 1, 2, z - 1)
    setBlock(light_gray_concrete, x + 1, 2, z + 1)
    setBlock(light_gray_concrete, x - 1, 2, z + 1)
    

def addTree(x, z):
    fillBlocks(log, x, 2, z, x, 8, z)
    fillBlocks(leaves, x - 2, 5, z - 2, x + 2, 6, z + 2)
    setBlock(air, x - 2, 6, z - 2)
    setBlock(air, x - 2, 6, z + 2)
    setBlock(air, x + 2, 6, z - 2)
    setBlock(air, x + 2, 6, z + 2)
    fillBlocks(leaves, x - 1, 7, z - 1, x + 1, 8, z + 1)
    setBlock(air, x - 1, 8, z - 1)
    setBlock(air, x - 1, 8, z + 1)
    setBlock(air, x + 1, 8, z - 1)
    setBlock(air, x + 1, 8, z + 1)
