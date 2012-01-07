This project is intended to eventually be able to convert an Eagle project to kicad without having eagle installed.

All scripts are written in the python 3.2 grammer.
The project is currently in the early stages, so please try it out and report any issues to the issue tracker.

It will only work with eagle files made with Eagle 6.0 and higher

The board will show up in kicad centered in the red sheet


Files:
	Eagle2kicad.py:
		Converts an eagle .brd to a kicad .brd so far 
		
		So Far: 
			Modules
				Names/Values
				Pads
				Graphics
					Lines
					Arcs
			
			Signal
				Connections
				Tracks
				Vias
				
			PCB Edges
			
			Graphics:
				Lines
				Arcs
				Text 
		
		Not Yet:
			Zones 
				(For some reason they show up but can't be filled... then they dissappear)
			
			Modules:
				Text
				Graphics
					Polygons
					Circles
					Rectangles					
				Names/Values textLayer
			
			Graphics:
				Circles
				Rectangles
				Polygons
			
		
		 