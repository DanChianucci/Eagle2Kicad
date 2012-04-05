These python scripts will eventually be able to convert an Eagle 6.0+ 
Project into a Kicad Project.

Hurray Finally able to convert Libraries as well...
However so far it will only convert the footprints, not the symbols


All scripts are written in the python 3.2 grammer.
The project is currently in the early stages, so please try it out and 
report any issues to the issue tracker.

So far Converting between Boards does everything except the following:			
	Zones		
	Rectangle graphics
	
To use:
	-copy the Eagle .brd file to the Board directory 
	-run Board.py (in the BOARD directory) 
	-it will ask for the name of an input file (the .brd you just copied)
	-it will ask for the name of an output file (anything.brd)
	-And thats it, the kicad .brd file is now in the Board directory

Library Conversion:
	Converts Module footprints... (no schematic symbols yet)

Still Testing Library, if you want to try it out
	-copy the Eagle .lbr file to the Library directory 
	-run Library.py (in the BOARD directory) 
	-it will ask for the name of an input file (the .lbr file you just copied)
	-it will ask for the name of an output file (anything.mod)
	-And thats it, the kicad footprint library should be in the Library folder

	
			
		
		 