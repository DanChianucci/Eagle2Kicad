These python scripts will eventually be able to convert an Eagle 6.0+ project into a Kicad Project.

All scripts are written in the python 3.2 grammer.
Please try it out and report any issues to the issue tracker.

Features so far:
	Convert Boards
		-Rectangle Graphics are not converted
	
	Convert Libraries
		-Very Limited Schematic Symbol support
	
To Convert Board:
	-copy the Eagle .brd file to the Board directory 
	-run Board.py (in the BOARD directory) 
	-it will ask for the name of an input file (the .brd you just copied)
	-it will ask for the name of an output file (anything.brd)
	-And thats it, the kicad .brd file is now in the Board directory

To Convert Library
	(note COnverting Libraries is still experimental)
	-copy the Eagle .lbr file to the Library directory 
	-run Library.py (in the Library directory) 
	-it will ask for the name of an input file (the .lbr file you just copied)
	-it will ask for the name of an output file (anything.mod)
	-And thats it, the kicad footprint library should be in the Library folder

!!!!!!!!!!!!NOTICE!!!!!!!!!!!!!!!!!
All boards converted using this script should be checked over to make sure everything looks good.
Take care to notice pad sizes, via sizes etcetera.  Make sure to run a DRC.	 