These python scripts will eventually be able to convert an Eagle 6.0+ 
Project into a Kicad Project.

For now it is only able to convert .brd files

All scripts are written in the python 3.2 grammer.
The project is currently in the early stages, so please try it out and 
report any issues to the issue tracker.

So far Converting between Boards does everything except the following:
			
	Zones: they show up but can't be filled...then they dissappear)			
	Text in modules					
	Names/Values textLayer in modules			
	Rectangle graphics
	
To use:
	-copy the Eagle file to the BOARD directory 
	-run brdConverter.py (in the BOARD directory) 
	-it will ask for the name of an input file, and output file
	-the input file is the name of the file you just copied

Library Conversion:
	Converts Module footprints... (no schematic symbols yet)

Still Testing libconverter, so not supported yet
	
			
		
		 