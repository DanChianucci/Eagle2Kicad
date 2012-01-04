This project is intended to eventually be able to convert an Eagle project to kicad without having eagle installed.

All scripts are written in the python 3.2 grammer.
The project is currently in the early stages, so please try it out and report any issues to the issue tracker.

It will only work with eagle files made with Eagle 6.0 and higher


Files:
	Eagle2kicad.py:
		Converts an eagle .brd to a kicad .brd so far 
		
		So Far: 
			Modules
			Signal Tracks
			PCB Edges
			Vias 
		
		Not Yet:
			Zones (For some reason they show up but can't be filled... then they dissappear)
			Graphics (both in modules, and plain)
			Text (No text whatsoever is transfered)
			
		
		 