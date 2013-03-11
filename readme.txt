These python scripts will eventually be able to convert an Eagle 6.0+ project into a Kicad Project.

All scripts are written in the python 3.2 grammer.
Please try it out and report any issues to the issue tracker.

Features so far:
        Convert Boards
            -Rectangle Graphics are not converted
        Convert Libraries
            -Schematic Symbol Conversions thanks to ???
        
To Convert a file run Start.py located in the root of the download zip file
A gui will pop up asking what to do.
    -# Choose an option
    -# Select the file to convert.
    -# Select the Output file(s)
    -# A message will appear stating whether or not the conversion was sucessful
    -# check the log.txt to see if there were any issues

!!!!!!!!!!!!NOTICE!!!!!!!!!!!!!!!!!
All boards converted using this script should be checked over to make sure everything looks good.
Take care to notice pad sizes, via sizes etcetera.  Make sure to run a DRC.	 