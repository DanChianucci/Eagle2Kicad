# Eagle2KiCAD EDA Converter
----------------------------

This project aims to provide a simple way to convert an Eagle CAD project into a KiCad Project.

All scripts are written in the python 3.2 grammar, and have been released under the MIT Licence.

Please report any issues to the issue tracker

If you would like to contribute, please fork this repository, make your changes, and then send me a pull request.

Features so far:
----------------
- Convert Boards
	- Rectangle Graphics are not converted
- Convert Libraries
     - Schematic Symbol Conversions  (.lib)
     - Board Footprint Conversion (.mod)


GUI:
----
      
To Convert a file run Start.py located in the root of the download zip file

1. A gui will pop up asking what to do.
2. Choose an option
3. Select the file to convert.
4. Select the Output file(s)
5. A message will appear stating whether or not the conversion was sucessful
6. Check the log.txt and Console to see if there were any issues

CMD Line:
----------

Alternatively you may use the command line options.

    usage: Eagle2KiCad [-h] [-l inFile symFile modFile] [-b inFile brdFile]
                       [-s inFile schFile] [-v {0,1}]

    optional arguments:
      -h, --help            show this help message and exit
      -l inFile symFile modFile, -L inFile symFile modFile, --Library inFile symFile modFile
                            Convert an Eagle Library
      -b inFile brdFile, -B inFile brdFile, --Board inFile brdFile
                            Convert an Eagle Board
      -s inFile schFile, -S inFile schFile, --Schematic inFile schFile
                            Convert an Eagle Schematic
      -v {0,1}, --verbosity {0,1}
                            Verbosity Level


>**Note:** 
>
>- Tags may be repeated multiple times. This feature can be used to do batch conversions
>- Tags may be mixed together.  You are not limited to converting only boards or only libraries
 
Contributors:
-------------
- Trump211
- Magtux
- Myval
- yoneken
- If I have forgotten someone please send me an email and I'll add to this list
    
# <font color="red">!!!NOTICE:!!!</font>
----------
All boards converted using this script should be checked over to make sure everything looks good.
Take care to notice pad sizes, via sizes, via layers, etc.  Make sure to run a DRC.	 
