#!/usr/bin/python3

import json
import numpy as np
from enum import Enum
import math
import sys
import argparse

class Entity:
	def __init__(self, entity_type, x_pos, y_pos):
		self.entity_type = int(entity_type)
		self.x_pos = int(x_pos)
		self.y_pos = int(y_pos)

def get_entity_x_pos(elem):
	return elem.x_pos

class Map:
	def __init__(self, mapNumber, jsonData):
		self.map_number = int(mapNumber)
		for prop in jsonData["properties"]:
			if(prop["name"]=="RealHeight"):
				self.height = prop["value"]
			if(prop["name"]=="RealWidth"):
				self.width = prop["value"]
		self.data = jsonData["data"]
		self.entities = {}
		self.start_pointer = 0
		for i in range(int(self.width // 32)):
			self.entities[i] = []
	def addEntities(self, objectData):
		for object in objectData["objects"]:
			type = object["type"]
			x = object["x"]
			y = object["y"]
			newEntity = Entity(type, x, y)
			#The map is divided into sections of entities that are loaded together
			section = int((newEntity.x_pos / 16) // 32)
			self.entities[section].append(newEntity)
		#Reorder based on x coordinate
		# print("before:")
		# for entity in self.entities:
		# 	print(entity.x_pos)
		for section in self.entities.keys():
			self.entities[section].sort(key=get_entity_x_pos)
		# print("after:")
		# for entity in self.entities:
		# 	print(entity.x_pos)


def write_byte(inByte):
	output_bytes.append(inByte & 0xFF)

def write_word(word):
	lowByte = word & 0xFF
	highByte = word >> 8
	write_byte(lowByte)
	write_byte(highByte)

def skip_to_address(address):
	while(len(output_bytes) != address):
		write_byte(0)


def write_map(number):
	map = maplist[number]
	entities = map.entities
	#Write each section of entities in the the map to a different
	# page of memory
	for section in entities.keys():
		start_address = 0x0100 *(section+1) + map.start_pointer
		# map_strings[i] += ("*=$%s\n" % hex(start_address).lstrip("0x"))
		skip_to_address(start_address)


		for entity in entities[section]:
			# map_strings[i] += ("!word $%s," % hex(entity.x_pos).lstrip("0x"))
			write_word(entity.x_pos)
			# map_strings[i] += (" $%s\n" % hex(entity.y_pos).lstrip("0x"))
			write_word(entity.y_pos)
			# map_strings[i] += ("!byte $%s," % hex(entity.entity_type).lstrip("0x"))
			write_byte(entity.entity_type)
			# map_strings[i] += (" $00\n") #unused for now
			write_byte(0)

		#fill the rest of page with 0
		# fill_amount = 256-(6*len(entities[section]))
		# map_strings[i] += ("!fill $%s\n" % hex(fill_amount).lstrip("0x"))

	#The tilemap data starts at address $2000
	# map_strings[i] += ("*=$%s\n" % hex(current_pointer+0x2000).lstrip("0x"))
	skip_to_address(map.start_pointer+0x2000)
	for y in range(map.height):
		# map_strings[i] += ("\t!byte ")
		for x in range(map.width):
			#Maybe not use fixed 256 here
			tileIndex = y * 256 + x
			tileValue = map.data[tileIndex] - 1
			lowByte = tileValue & 0xFF
			#map_strings[i] += ("%d, " % lowByte)
			write_byte(lowByte)
			#do second byte palette offset and highest part of tile number
			tileNumberHighByte = (tileValue >> 8) & 0x03
			tileFlippedHorizontally = ((tileValue & 0x80000000) != 0)
			tileFlippedVertically = ((tileValue & 0x40000000) != 0)
			#tileFlippedDiagonally = ((tileValue & 0x20000000) != 0) #should not be used #TODO maybe add warning
			paletteoffsetByte = 0 << 4
			flipbyte = (int(tileFlippedHorizontally) << 2) | (int(tileFlippedVertically) << 3)
			highByte = tileNumberHighByte | paletteoffsetByte | flipbyte

			# if(x==map.width-1):
			# 	map_strings[i] += ("%d" % highByte)
			# else:
			# 	map_strings[i] += ("%d, " % highByte)

			write_byte(highByte)

		# map_strings[i] += ("\n")

tiles = {}
background = []
maplist = {}
nextBank = 1
mapName = ""
startx = 0
starty = 0
tilesetfile = ""
current_pointer = 0
next_pointer = 0

map_strings = {}

output_bytes = []


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
	description='Converts a tile map description file to a .inc file to include in assembly.\n\n'
	'Examples:\n\n'
	'tilemapper.py -o tile_map.inc map1.tilemap\n'
	'Read the tilemap map1.tilemap and generate in file tile_map.inc\n\n')
parser.add_argument('input', help='the tilemap input file name')
#parser.add_argument('output', help='the output file name')
args = parser.parse_args()

#READ json file from Tiled
with open(args.input, "r") as read_file:
	data = json.load(read_file)
	#set up maps
	for prop in data["properties"]:
		if(prop["name"]=="MapName"):
			mapName = prop["value"]
		if(prop["name"]=="startx"):
			startx = prop["value"]
		if(prop["name"]=="starty"):
			starty = prop["value"]

	tilesetfile = "tilemaps/" + data["tilesets"][0]["source"] #TODO loop through props

	for layer in data["layers"]:
		if(layer["type"] == "tilelayer"):
			maplist[layer["properties"][0]["value"]] = Map(layer["properties"][0]["value"], layer)
	#attach objects
	for layer in data["layers"]:
		if(layer["type"] == "objectgroup"):
			maplist[layer["properties"][0]["value"]].addEntities(layer)


#Write main map index file
with open(mapName.upper() + ".MAP", "wb") as fileOut:
	# fileOut.write("!to \"%s.O\", cbm\n*=0\n" % mapName.upper())
	# fileOut.write("!byte %s ; %s maps to load\n" % (len(maplist),len(maplist)))
	write_byte(len(maplist))
	next_pointer = 0x2000
	#Loop through each map layer.  Treating each layer as an individual map
	for i in range(len(maplist.keys())):
		if((len(maplist.keys()) > 1) and i==len(maplist.keys())-1):
			i = -1
		map = maplist[i]
		map_strings[i] = ""
		#fileOut.write("tilemap%d:\n" % i)
		heightValue = 0
		if(map.height == 64):
			heightValue = 1
		elif(map.height == 128):
			heightValue = 2
		elif(map.height == 256):
			heightValue = 3
		widthValue = 0
		if(map.width == 64):
			widthValue = 1
		elif(map.width == 128):
			widthValue = 2
		elif(map.width == 256):
			widthValue = 3

		# fileOut.write("!byte %s ; Width Value\n" % widthValue) #TODO make sure game accounts for both -1s
		# fileOut.write("!byte %s ; Height Value\n" % heightValue)
		write_byte(widthValue)
		write_byte(heightValue)
		mapsize = map.width * map.height * 2
		banks =  math.ceil(mapsize / 8192)
		banks = banks + 1 # account for entity bank
		current_pointer = next_pointer
		next_pointer = current_pointer + banks * 0x2000
		map.start_pointer = current_pointer
		# fileOut.write("!byte %s ; Next Highram Bank\n" % nextBank)
		write_byte(nextBank)
		nextBank += banks



		# fileOut.write("!word %s ;startx\n" % startx)
		# fileOut.write("!word %s ;starty\n" % starty)
		#write_word(startx)
		#write_word(starty)
		# fileOut.write("!byte %s\n" % len(mapfilename))
		# fileOut.write("!pet \"%s\"\n" % mapfilename.lower())

		# NOW consolidating into 1 file
		#Write individual map file
		#with open(mapfilename + ".asm", "w") as fileOutMap:
		#fileOut.write("!to \"%s\", cbm\n*=0\n" % mapfilename.upper())
		# map_strings[i] += ("*=$%s\n" % hex(current_pointer).lstrip("0x"))
		# map_strings[i] += ("!word $FF\n")


	write_word(startx)
	write_word(starty)


	for i in range(len(maplist.keys())):
		if((len(maplist.keys()) > 1) and i==len(maplist.keys())-1):
			i = -1
		write_map(i)
		#fileOut.write(map_strings[i])

	fileOut.write(bytes(b'\x00\x00'))
	fileOut.write(bytes(output_bytes))


with open(tilesetfile, "r") as tileset_file:
	data = json.load(tileset_file)
	varsfilename = mapName + "vars.asm"
	varsassembledfilename = (mapName + "va.o").upper() #This is shortened to VA for X16 filename restrictions
	with open(varsfilename,"w") as fileOut:
		fileOut.write("!to \"%s\", cbm\n*=0\n" % varsassembledfilename)
		tiles = data["tiles"]
		for tile in tiles:
			type = int(tile["type"])
			fileOut.write("!byte %d\n" %type)
