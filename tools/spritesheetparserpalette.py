#!/usr/bin/python3

# Converts sprite sheet data and png image to a C style array to be used as a sprite with Commander X16

from PIL import Image
from enum import Enum
import numpy as np
import math
import sys
import argparse


class Frame:
	def __init__(self, x_offset, y_offset):
		self.x_offset = x_offset
		self.y_offset = y_offset

class Animation:
	def __init__(self, frame_array):
		self.frame_array = frame_array

class Color:
	def __init__(self, r, g, b):
		self.red = r
		self.green = g
		self.blue = b

	def hexvalue(self):
		bp = (self.blue) & 0x0F
		gp = ((self.green) << 4) & 0xF0
		rp = ((self.red) << 8) & 0xF00
		return bp+gp+rp

class readMode(Enum):
	NONE = 0
	FILE = 1
	NAME = 2
	SPRITESIZE = 3
	FRAMES = 4
	ANIMATIONS = 5
	PALETTE = 6

tilemode = 0

mode = readMode.NONE;

spriteSize = (0,0)

frames = []
animations = []

name = ""
filename = ""

# parse arguments
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
    description='Converts a Spritesheet and png file to Commander X16 sprite data.\n\n'
    'Examples:\n\n'
    'spritesheetparser.py -s sheet1.spritesheet sheet1.inc\n')
parser.add_argument('output', help='the output file name')
parser.add_argument('-f', default='c', choices=['c','basic','acme'], help='output format: c for C array, basic for BASIC, acme for ACME assembler, default: c')
parser.add_argument('-s', help='File that contains the spritesheet description')
args = parser.parse_args()


# default x16 palette
# default_palette = [
# 0x0000,0xfff,0x800,0xafe,0xc4c,0x0c5,0x00a,0xee7,0xd85,0x640,0xf77,0x333,0x777,0xaf6,0x08f,0xbbb,0x000,0x111,0x222,0x333,0x444,0x555,0x666,0x777,0x888,0x999,0xaaa,0xbbb,0xccc,0xddd,0xeee,0xfff,0x211,0x433,0x644,0x866,0xa88,0xc99,0xfbb,0x211,0x422,0x633,0x844,0xa55,0xc66,0xf77,0x200,0x411,0x611,0x822,0xa22,0xc33,0xf33,0x200,0x400,0x600,0x800,0xa00,0xc00,0xf00,0x221,0x443,0x664,0x886,0xaa8,0xcc9,0xfeb,0x211,0x432,0x653,0x874,0xa95,0xcb6,0xfd7,0x210,0x431,0x651,0x862,0xa82,0xca3,0xfc3,0x210,0x430,0x640,0x860,0xa80,0xc90,0xfb0,0x121,0x343,0x564,0x786,0x9a8,0xbc9,0xdfb,0x121,0x342,0x463,0x684,0x8a5,0x9c6,0xbf7,0x120,0x241,0x461,0x582,0x6a2,0x8c3,0x9f3,0x120,0x240,0x360,0x480,0x5a0,0x6c0,0x7f0,0x121,0x343,0x465,0x686,0x8a8,0x9ca,0xbfc,0x121,0x242,0x364,0x485,0x5a6,0x6c8,0x7f9,0x020,0x141,0x162,0x283,0x2a4,0x3c5,0x3f6,0x020,0x041,0x061,0x082,0x0a2,0x0c3,0x0f3,0x122,0x344,0x466,0x688,0x8aa,0x9cc,0xbff,0x122,0x244,0x366,0x488,0x5aa,0x6cc,0x7ff,0x022,0x144,0x166,0x288,0x2aa,0x3cc,0x3ff,0x022,0x044,0x066,0x088,0x0aa,0x0cc,0x0ff,0x112,0x334,0x456,0x668,0x88a,0x9ac,0xbcf,0x112,0x224,0x346,0x458,0x56a,0x68c,0x79f,0x002,0x114,0x126,0x238,0x24a,0x35c,0x36f,0x002,0x014,0x016,0x028,0x02a,0x03c,0x03f,0x112,0x334,0x546,0x768,0x98a,0xb9c,0xdbf,0x112,0x324,0x436,0x648,0x85a,0x96c,0xb7f,0x102,0x214,0x416,0x528,0x62a,0x83c,0x93f,0x102,0x204,0x306,0x408,0x50a,0x60c,0x70f,0x212,0x434,0x646,0x868,0xa8a,0xc9c,0xfbe,0x211,0x423,0x635,0x847,0xa59,0xc6b,0xf7d,0x201,0x413,0x615,0x826,0xa28,0xc3a,0xf3c,0x201,0x403,0x604,0x806,0xa08,0xc09,0xf0b
# ]
# default_palette.reverse()
palette = {0: Color(0,0,0)}
nextpaletteentry = 1



with open(args.s, "r") as fileIn:
	f1 = fileIn.readlines()
	for x in f1:
		if(x.startswith("!")):
			if(x == "!file\n"):
				mode = readMode.FILE
			if(x == "!name\n"):
				mode = readMode.NAME
			if(x == "!spritesize\n"):
				mode = readMode.SPRITESIZE
			if(x == "!frames\n"):
				mode = readMode.FRAMES
			if(x == "!animations\n"):
				mode = readMode.ANIMATIONS
			if(x == "!tile\n"):
				tilemode = 1
			if(x == "!palette\n"):
				mode = readMode.PALETTE
		elif(len(x)!=1):
			if(mode == readMode.FILE):
				x = x.strip("\n ")
				filename = x
			elif(mode == readMode.NAME):
				x = x.strip("\n ")
				name = x
			elif(mode == readMode.SPRITESIZE):
				x = x.strip("\n ")
				x=x.split(",")
				if(len(x)!=2):
					print("ERROR!  improper sprite size\n")
					break
				spriteSize = (int(x[0]),int(x[1]))

			elif(mode == readMode.FRAMES):
				if(tilemode == 1):
					x = x.strip("\n")
					x = x.split(",")
					x_tiles = int(x[0])
					y_tiles = int(x[1])
					x_pixel_size = spriteSize[0]
					y_pixel_size = spriteSize[1]
					for row in range(y_tiles):
						for col in range(x_tiles):
							x_coord = col * x_pixel_size
							y_coord = row * y_pixel_size
							frames.append(Frame(int(x_coord),int(y_coord)))
				else:
					x = x.strip("\n")
					x = x.split(":")
					key = int(x[0])
					x = x[1].split(",")
					frames.append(Frame(int(x[0]),int(x[1])))

			elif(mode == readMode.ANIMATIONS):
				x = x.strip("\n")
				x = x.split(":")
				key = int(x[0])
				framesStrings = x[1].split(",")
				frameList = []
				for frame in framesStrings:
					x = frame.split("~")
					frameKey = x[0]
					frameDuration = x[1]
					frameList.append((int(frameKey),int(frameDuration)))

				animations.append(Animation(frameList))

			elif(mode == readMode.PALETTE):
				x = x.strip("\n")
				x = x.split(",")
				red = int(x[0],16)
				green = int(x[1],16)
				blue = int(x[2],16)
				palette[nextpaletteentry] = Color(red,green,blue)
				nextpaletteentry += 1


	fileIn.close()

# load image
im = Image.open(filename)
# palettelist = im.getpalette()
# print(palettelist)
# palette = {}
# for i in range(16):
# 	red = palettelist[i*3]
# 	green = palettelist[i*3+1]
# 	blue = palettelist[i*3+2]
# 	palette[i] = Color(red, green, blue)
#
# print(palette[2].red)
# print(palette[2].green)
# print(palette[2].blue)
p = np.array(im)


# info table file output
infoFilename = args.output + ".inc"
if(tilemode==0):
	with open(infoFilename, "w") as fileOut:

		fileOut.write("%s_data:\n" % name)
		fileOut.write("	!16 $0000 ;Vram offset will be set here\n") #Will be populated in game by vram offset
		fileOut.write("	!16 $%04x ; Frame offset\n" % (spriteSize[0]*spriteSize[1]//2)) # frame offset
		fileOut.write("	!8 $%02x ;number of frames\n" % len(frames)) #Number of frames
		fileOut.write("	!8 $%02x ;number of animations\n" % len(animations)) #Number of frames
	    #write animation data
	    # animations can have up to 4 frames
	    # data is layed out
	    # {FRAME INDEX 1} {DURATION} {FRAME INDEX 2} {DURATION} {FRAME INDEX 3} {DURATION} {FRAME INDEX 4} {DURATION}
		fileOut.write("%s_animations:\n" % name)

		for animation in animations:
			fileOut.write("    !byte ")
			for i in range(0,4):
				if(len(animation.frame_array) <= i):
					fileOut.write("$%02x,$%02x" % (0,0))
				else:
					frame = animation.frame_array[i]
					fileOut.write("$%02x,$%02x" % (frame[0],frame[1]))
				if(i<3):
					fileOut.write(",")
			fileOut.write("\n")


		fileOut.write("%s_filename_length:\n" %name)
		fileOut.write("	!byte %s\n" %(len(name)+2))
		fileOut.write("%s_filename:\n" %name)
		fileOut.write("	!pet \"%s.o\"" % name)

		fileOut.close()

#data file output
dataFilename = args.output + "data.inc"
with open(dataFilename, "w") as fileOut:
	fileOut.write("!to \"%s.O\", cbm\n*=0\n" % name.upper())
	#write data
	fileOut.write("%s:\n" % name)
	for frame in frames:
		for y in range(frame.y_offset,spriteSize[1]+frame.y_offset):
			fileOut.write("    !byte ")
			rowBest = []
			for x in range(frame.x_offset,frame.x_offset+spriteSize[0]):
				# get pixel color
				r, g, b, a = p[y][x]

				# use index 0 for transparent color
				if a == 0:
					best = 0
					#print("Transparent!")
				else:
					#print("Not transparent!")
					# find best palette match, start searching from top to allow index 16 for black color
					d = 1e9
					best = 0
					for key in palette.keys():
						if key == 0:
							continue
						entry = palette[key].hexvalue()
						rp = ((entry >> 8) & 0xf) << 4
						gp = ((entry >> 4) & 0xf) << 4
						bp = (entry & 0xf) << 4
						dr = r - rp
						dg = g - gp
						db = b - bp
						d0 = dr * dr + dg * dg + db * db

						if d0 < d: #32,112,240
							best = key
							d = d0
				#print("Appending: %s" % best)
				rowBest.append(best)

			# write palette index
			i = 1
			while (i <len(rowBest)):
				best = (rowBest[i] << 4) + rowBest[i-1]
				fileOut.write("$%01x%01x" % (best & 0x0F,best >> 4))
				if (i < len(rowBest)-1):
					fileOut.write(",")
				i += 2
			fileOut.write("\n")
	fileOut.close()
