#!/bin/bash
all: INTRO.SP externaltools

quick:
	make clean && make -j10 all

OS_VERSION = $(shell cat /proc/version)
ARCH = $(shell arch)

ifneq (,$(findstring Microsoft,$(OS_VERSION)))
EMU = ../bin/x16emu.exe
else
EMU = ../bin/x16emu
endif

#TODO Handle both apple silicon and not python
ifeq ($(ARCH),arm64)
PYTHON = arch -x86_64 python3
else
PYTHON = python3
endif

START = $(EMU) -prg SSE.PRG
DEBUG = $(EMU) -debug -prg SSE.PRG


LEVELCONFIG = $(PYTHON) ./tools/buildlevels.py
SPRITECONFIG = $(PYTHON) ./tools/buildsprites.py
SPRITEPARSER = $(PYTHON) tools/spritesheetparserpalette.py

%sheetdata.inc::  images/%s.spritesheet images/%s.png
	$(SPRITEPARSER) -s  $< $*sheet

run: all
	$(START) -run -scale 2 -joy1 -joy2

externaltools:  SPRITE.IND LEVEL.IND ENTITY.IND

LEVEL.IND: levels.cfg TESTPA.O MAPPA.O
	$(LEVELCONFIG)

*.MAP: LEVEL.IND

SPRITE.IND: sprite.cfg
	$(SPRITECONFIG)


clean:
	rm -f *.O.asm *.o.asm *.bin *data.inc tile*.inc *sheet.inc sheet*.inc maptilesheet.inc tilesheet.inc music.inc playersheet.inc floatsprite.inc floatspritedata.inc slashsprite.inc playermapsprite.inc spinner.inc tilemaps/*.csv *SP.O TILEMAP.O *map.inc test.inc l1.inc l1vars.asm l2vars.asm l3vars.asm forest.inc map.inc small.inc forestvars.asm testvars.asm smallvars.asm mapvars.asm healthsprite.inc playermap.inc playermapdata.inc playersprite.inc spinnersprite.inc popoutsprite.inc popoutspritedata.inc *.MAP *.VAR SPRITE.IND LEVEL.IND *.SPR *.spr MAP.NAV *.TSH *.tsh
