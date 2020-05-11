#!/usr/bin/python3

import json
import numpy as np
from enum import Enum
import math
import sys
import argparse


#tables from https://github.com/AndiB/PETSCIItoASCII/blob/master/src/python/tables.py
petToAscTable = [
0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x14,0x09,0x0d,0x11,0x93,0x0a,0x0e,0x0f,
0x10,0x0b,0x12,0x13,0x08,0x15,0x16,0x17,0x18,0x19,0x1a,0x1b,0x1c,0x1d,0x1e,0x1f,
0x20,0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2a,0x2b,0x2c,0x2d,0x2e,0x2f,
0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3a,0x3b,0x3c,0x3d,0x3e,0x3f,
0x40,0x61,0x62,0x63,0x64,0x65,0x66,0x67,0x68,0x69,0x6a,0x6b,0x6c,0x6d,0x6e,0x6f,
0x70,0x71,0x72,0x73,0x74,0x75,0x76,0x77,0x78,0x79,0x7a,0x5b,0x5c,0x5d,0x5e,0x5f,
0xc0,0xc1,0xc2,0xc3,0xc4,0xc5,0xc6,0xc7,0xc8,0xc9,0xca,0xcb,0xcc,0xcd,0xce,0xcf,
0xd0,0xd1,0xd2,0xd3,0xd4,0xd5,0xd6,0xd7,0xd8,0xd9,0xda,0xdb,0xdc,0xdd,0xde,0xdf,
0x80,0x81,0x82,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,0x8f,
0x90,0x91,0x92,0x0c,0x94,0x95,0x96,0x97,0x98,0x99,0x9a,0x9b,0x9c,0x9d,0x9e,0x9f,
0xa0,0xa1,0xa2,0xa3,0xa4,0xa5,0xa6,0xa7,0xa8,0xa9,0xaa,0xab,0xac,0xad,0xae,0xaf,
0xb0,0xb1,0xb2,0xb3,0xb4,0xb5,0xb6,0xb7,0xb8,0xb9,0xba,0xbb,0xbc,0xbd,0xbe,0xbf,
0x60,0x41,0x42,0x43,0x44,0x45,0x46,0x47,0x48,0x49,0x4a,0x4b,0x4c,0x4d,0x4e,0x4f,
0x50,0x51,0x52,0x53,0x54,0x55,0x56,0x57,0x58,0x59,0x5a,0x7b,0x7c,0x7d,0x7e,0x7f,
0xa0,0xa1,0xa2,0xa3,0xa4,0xa5,0xa6,0xa7,0xa8,0xa9,0xaa,0xab,0xac,0xad,0xae,0xaf,
0xb0,0xb1,0xb2,0xb3,0xb4,0xb5,0xb6,0xb7,0xb8,0xb9,0xba,0xbb,0xbc,0xbd,0xbe,0xbf
]

ascToPetTable = [
0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x14,0x20,0x0d,0x11,0x93,0x0a,0x0e,0x0f,
0x10,0x0b,0x12,0x13,0x08,0x15,0x16,0x17,0x18,0x19,0x1a,0x1b,0x1c,0x1d,0x1e,0x1f,
0x20,0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2a,0x2b,0x2c,0x2d,0x2e,0x2f,
0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3a,0x3b,0x3c,0x3d,0x3e,0x3f,
0x40,0xc1,0xc2,0xc3,0xc4,0xc5,0xc6,0xc7,0xc8,0xc9,0xca,0xcb,0xcc,0xcd,0xce,0xcf,
0xd0,0xd1,0xd2,0xd3,0xd4,0xd5,0xd6,0xd7,0xd8,0xd9,0xda,0x5b,0x5c,0x5d,0x5e,0x5f,
0xc0,0x41,0x42,0x43,0x44,0x45,0x46,0x47,0x48,0x49,0x4a,0x4b,0x4c,0x4d,0x4e,0x4f,
0x50,0x51,0x52,0x53,0x54,0x55,0x56,0x57,0x58,0x59,0x5a,0xdb,0xdc,0xdd,0xde,0xdf,
0x80,0x81,0x82,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,0x8f,
0x90,0x91,0x92,0x0c,0x94,0x95,0x96,0x97,0x98,0x99,0x9a,0x9b,0x9c,0x9d,0x9e,0x9f,
0xa0,0xa1,0xa2,0xa3,0xa4,0xa5,0xa6,0xa7,0xa8,0xa9,0xaa,0xab,0xac,0xad,0xae,0xaf,
0xb0,0xb1,0xb2,0xb3,0xb4,0xb5,0xb6,0xb7,0xb8,0xb9,0xba,0xbb,0xbc,0xbd,0xbe,0xbf,
0x60,0x61,0x62,0x63,0x64,0x65,0x66,0x67,0x68,0x69,0x6a,0x6b,0x6c,0x6d,0x6e,0x6f,
0x70,0x71,0x72,0x73,0x74,0x75,0x76,0x77,0x78,0x79,0x7a,0x7b,0x7c,0x7d,0x7e,0x7f,
0xe0,0xe1,0xe2,0xe3,0xe4,0xe5,0xe6,0xe7,0xe8,0xe9,0xea,0xeb,0xec,0xed,0xee,0xef,
0xf0,0xf1,0xf2,0xf3,0xf4,0xf5,0xf6,0xf7,0xf8,0xf9,0xfa,0xfb,0xfc,0xfd,0xfe,0xff
]

class  Nav_Entry:
	def __init__(self, x_pos, y_pos, level, up, down, left, right,
				up_cond, down_cond, left_cond, right_cond):
		self.x = int(x_pos)
		self.y = int(y_pos)
		if(level.isnumeric()):
			self.level = int(level)
		else:
			self.level = 0xFF
		if(up.isnumeric()):
			self.up = int(up)
		else:
			self.up = 0xFF
		if(down.isnumeric()):
			self.down = int(down)
		else:
			self.down = 0xFF
		if(left.isnumeric()):
			self.left = int(left)
		else:
			self.left = 0xFF
		if(right.isnumeric()):
			self.right = int(right)
		else:
			self.right = 0xFF
		if(up_cond.isnumeric()):
			self.up_cond = int(up_cond)
		else:
			self.up_cond = 0xFF
		if(down_cond.isnumeric()):
			self.down_cond = int(down_cond)
		else:
			self.down_cond = 0xFF
		if(left_cond.isnumeric()):
			self.left_cond = int(left_cond)
		else:
			self.left_cond = 0xFF
		if(right_cond.isnumeric()):
			self.right_cond = int(right_cond)
		else:
			self.right_cond = 0xFF

class Level_Entry:
	def __init__(self, filename, palette):
		self.filename = filename
		self.palette = int(palette)

class Entity:
	def __init__(self, entity_type, x_pos, y_pos):
		self.entity_type = int(entity_type)
		self.x_pos = int(x_pos)
		self.y_pos = int(y_pos)

def get_entity_x_pos(elem):
	return elem.x_pos


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

palettes = {}

levels = {}

nav = {}

output_bytes = []

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

def clear_map_data():
	global tiles
	global background
	global maplist
	global nextBank
	global mapName
	global startx
	global starty
	global tilesetfile
	global current_pointer
	global next_pointer

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

def clear_output():
	global output_bytes
	output_bytes = []

def write_byte(inByte):
	global output_bytes
	output_bytes.append(inByte & 0xFF)

def write_word(word):
	lowByte = word & 0xFF
	highByte = word >> 8
	write_byte(lowByte)
	write_byte(highByte)

def write_string(str):
	write_byte(len(str))
	str = str.lower()
	for char in str:
		write_byte(ascToPetTable[ord(char)])

def skip_to_address(address):
	global output_bytes
	while(len(output_bytes) != address):
		write_byte(0)

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
	description='Converts a level config file into LEVEL.IND, MAP.NAV, and MAP files.\n\n'
	'Examples:\n\n'
	'buildlevels.py levels.cfg\n')
parser.add_argument('-input', default='levels.cfg', help='the level config file')
args = parser.parse_args()



def process_palette(lines_in):
	print("Generating palette list")
	#print(lines_in)
	i = 0
	ilen = len(lines_in)
	while(i < ilen):
		x = lines_in[i]
		x = x.strip(' \n:')
		num = int(x)
		i+=1
		x = lines_in[i]
		x = x.strip(' \n:\t')
		filename = x
		palettes[num] = filename
		i+=1
	#print(palettes)


def process_levels(lines_in):
	print("Generating level objects")
	#print(lines_in)
	i = 0
	ilen = len(lines_in)
	while(i < ilen):
		x = lines_in[i]
		x = x.strip(' \n:')
		num = int(x)
		filename = ''
		palette = ''
		while(1):
			i+=1
			if(i >= ilen):
				break
			x = lines_in[i]
			if(x[0].strip(':').isnumeric()):
				break
			x = x.strip(' \n\t')
			x = x.split(':')
			if(x[0] == "file"):
				filename = x[1]
			if(x[0] == "palette"):
				palette = x[1]
		levels[num] = Level_Entry(filename, palette)
	#print(levels)

def process_nav(lines_in):
	print("Generating nav objects")
	#print(lines_in)
	i = 0
	ilen = len(lines_in)
	while(i < ilen):
		x = lines_in[i]
		x = x.strip('\n:')
		num = int(x)
		x_pos = ''
		y_pos = ''
		level = ''
		up = ''
		down = ''
		left = ''
		right = ''
		up_cond = ''
		down_cond = ''
		left_cond = ''
		right_cond = ''
		while(1):
			i+=1
			if(i >= ilen):
				break
			x = lines_in[i]
			if(x[0].strip(':').isnumeric()):
				break
			x = x.strip(' \n\t')
			x = x.split(':')
			if(x[0] == "X"):
				x_pos = x[1]
			elif(x[0] == "Y"):
				y_pos = x[1]
			elif(x[0] == "LEVEL"):
				level = x[1]
			elif(x[0] == "UP"):
				x = x[1].split(',')
				up = x[0]
				if(len(x) > 1):
					up_cond = x[1]
			elif(x[0] == "DOWN"):
				x = x[1].split(',')
				down = x[0]
				if(len(x) > 1):
					down_cond = x[1]
			elif(x[0] == "LEFT"):
				x = x[1].split(',')
				left= x[0]
				if(len(x) > 1):
					left_cond = x[1]
			elif(x[0] == "RIGHT"):
				x = x[1].split(',')
				right = x[0]
				if(len(x) > 1):
					right_cond = x[1]
		nav[num] = Nav_Entry(x_pos, y_pos, level, up, down, left, right, up_cond, down_cond, left_cond, right_cond)


def process_and_write_map(filename):
	global tiles
	global background
	global maplist
	global nextBank
	global mapName
	global startx
	global starty
	global tilesetfile
	global current_pointer
	global next_pointer

	clear_map_data()
	#READ json file from Tiled
	with open(filename, "r") as read_file:
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
	# print("Opening map file to write")
	with open(mapName.upper() + ".MAP", "wb") as fileOut:
		clear_output()
		# fileOut.write("!to \"%s.O\", cbm\n*=0\n" % mapName.upper())
		# fileOut.write("!byte %s ; %s maps to load\n" % (len(maplist),len(maplist)))
		write_byte(len(maplist))
		next_pointer = 0x2000
		#Loop through each map layer.  Treating each layer as an individual map
		# print("Looping through map layers")
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

		# print("Finished loop")
		write_word(startx)
		write_word(starty)


		for i in range(len(maplist.keys())):
			if((len(maplist.keys()) > 1) and i==len(maplist.keys())-1):
				i = -1
			# print("Writing map #%s" % i)
			write_map(i)
			#fileOut.write(map_strings[i])

		# print("Writing file")
		fileOut.write(bytes(b'\x00\x00'))
		fileOut.write(bytes(output_bytes))
		# print("Done writing")

	with open(tilesetfile, "r") as tileset_file:
		clear_output()
		data = json.load(tileset_file)
		varsfilename = (mapName + ".var").upper()
		#varsassembledfilename = (mapName. + ".var").upper() #This is shortened to VA for X16 filename restrictions
		with open(varsfilename,"wb") as fileOut:
			#fileOut.write("!to \"%s\", cbm\n*=0\n" % varsassembledfilename)
			tiles = data["tiles"]
			for tile in tiles:
				type = int(tile["type"])
				type = type & 0xFF
				output_bytes.append(type)
			fileOut.write(bytes(b'\x00\x00'))
			fileOut.write(bytes(output_bytes))


with open(args.input, "r") as read_file:
	f1 = read_file.readlines()
	i = 0
	ilen = len(f1)
	while(i < ilen):
		x = f1[i]
		x = x.strip('\n')
		if(x == 'PALETTE:'):
			lines_in = []
			while(1):
				i+=1
				if(i >= ilen):
					break
				x= f1[i]
				x = x.strip('\n:')
				if(len(x)==0):
					break
				else:
					lines_in.append(x)
			process_palette(lines_in)
		elif(x == 'LEVELS:'):
			lines_in = []
			while(1):
				i+=1
				if(i >= ilen):
					break
				x= f1[i]
				x = x.strip('\n:')
				if(len(x)==0):
					break
				else:
					lines_in.append(x)
			process_levels(lines_in)
		elif(x == 'NAV:'):
			lines_in = []
			while(1):
				i+=1
				if(i >= ilen):
					break
				x= f1[i]
				x = x.strip('\n:')
				if(len(x)==0):
					break
				else:
					lines_in.append(x)
			process_nav(lines_in)
		else:
			i+=1

#Write MAP.NAV file
with open('MAP.NAV', "wb") as nav_file:
	clear_output()
	for i in range(len(nav)):
		entry = nav[i]
		write_byte(entry.x)
		write_byte(entry.y)
		write_byte(entry.level)
		write_byte(entry.up)
		write_byte(entry.down)
		write_byte(entry.left)
		write_byte(entry.right)
		write_byte(entry.up_cond)
		write_byte(entry.down_cond)
		write_byte(entry.left_cond)
		write_byte(entry.right_cond)



	nav_file.write(bytes(b'\x00\x00'))
	nav_file.write(bytes(output_bytes))




for i in range(len(levels)):
	clear_output()
	entry = levels[i]
	# print(entry.filename)
	process_and_write_map("tilemaps/" + entry.filename)

clear_output()
process_and_write_map("tilemaps/mapmap.json")


palette_offsets = {}
tileset_offset = 0
maptileset_offset = 0

#write index file
with open('LEVEL.IND',"wb") as ind_file:
	clear_output()
	write_word(0) # IS overwritten later with nav file pointer
	write_byte(len(levels)+1)
	for i in range(len(levels)+1):
		write_word(0) #TODO overwrite with map_files table address
	#write_word(0) #TODO replace with map map files table address

	#write palettes
	for i in range(len(palettes)):
		palette_offsets[i] = len(output_bytes)+1
		filename = palettes[i]
		write_string(filename)


	#write tilesets
	tileset_offset = len(output_bytes)+1
	write_string("testsh.o")

	maptileset_offset = len(output_bytes)+1
	write_string("mapsh.o")




	#write level indexes
	for i in range(len(levels)):
		#assign pointer in index
		current_output_pointer = len(output_bytes)
		output_bytes[3+(2*i)] = current_output_pointer & 0xFF
		output_bytes[3+(2*i)+1] = current_output_pointer>>8 & 0xFF
		entry = levels[i]

		#Write table
		# level1_map_files:
		# 	!word testtilesname
		# 	!word level1filename
		# 	!word level1varsname
		# 	!word testpalettename
		#
		# 	!byte 6
		# level1filename:
		# 	!pet "l1.map"
		#
		# 	!byte 6
		# level1varsname:
		# 	!pet "l1va.o"

		write_word(tileset_offset)
		thisfilename_pointer = len(output_bytes)
		write_word(0) #TODO overwrite
		thisvarsname_pointer = len(output_bytes)
		write_word(0) #TODO overwrite
		write_word(palette_offsets[entry.palette])

		output_bytes[thisfilename_pointer] =  len(output_bytes)+1 & 0xFF
		output_bytes[thisfilename_pointer+1] = (len(output_bytes)+1)>>8 & 0xFF


		mapfilename = entry.filename.strip(' \n\t').replace('map.json','.map').upper()
		write_string(mapfilename)

		output_bytes[thisvarsname_pointer] = len(output_bytes)+1 & 0xFF
		output_bytes[thisvarsname_pointer+1] = (len(output_bytes)+1)>>8 & 0xFF

		varfilename = entry.filename.strip(' \n\t').replace('map.json','.var').upper()
		write_string(varfilename)



	#write map map indexes
	current_output_pointer = len(output_bytes)
	output_bytes[3+2*len(levels)] = current_output_pointer & 0xFF
	output_bytes[3+2*len(levels)+1] = current_output_pointer>>8 & 0xFF

	write_word(maptileset_offset)
	thisfilename_pointer = len(output_bytes)
	write_word(0) #TODO overwrite
	thisvarsname_pointer = len(output_bytes)
	write_word(0) #TODO overwrite
	write_word(palette_offsets[1]) #TODO maybe have in index?

	output_bytes[thisfilename_pointer] =  len(output_bytes)+1 & 0xFF
	output_bytes[thisfilename_pointer+1] = (len(output_bytes)+1)>>8 & 0xFF


	mapfilename = "mapmap.json".strip(' \n\t').replace('map.json','.map').upper()
	write_string(mapfilename)

	output_bytes[thisvarsname_pointer] = len(output_bytes)+1 & 0xFF
	output_bytes[thisvarsname_pointer+1] = (len(output_bytes)+1)>>8 & 0xFF

	varfilename = "mapmap.json".strip(' \n\t').replace('map.json','.var').upper()
	write_string(varfilename)


	current_output_pointer = len(output_bytes)+1
	output_bytes[0] = current_output_pointer & 0xFF
	output_bytes[1] = current_output_pointer>>8 & 0xFF
	write_string("MAP.NAV")

	ind_file.write(bytes(b'\x00\x00'))
	ind_file.write(bytes(output_bytes))







#print(palettes)
