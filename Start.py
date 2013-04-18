import sys,inspect,os,traceback,datetime
from argparse import ArgumentParser

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# r'' means a raw string for multi environment (win/mac/*nix)
sys.path.append(scriptDir+r'/Board')
sys.path.append(scriptDir+r'/Library')
sys.path.append(scriptDir+r'/Schematic')
sys.path.append(scriptDir+r'/Common')


from Board import Board
from Library import Library
#from Schematic import Schematic

from tkinter import Tk,Frame,Label,Button,RIDGE,BOTH,X
from tkinter.filedialog   import askopenfilename     
from tkinter.filedialog   import asksaveasfilename
from tkinter.messagebox	import showinfo,showerror
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import XMLParser


logFile=open("Log.txt","a")

def startGui():
	root=Tk()
	root.wm_title("Eagle V6 to Kicad Converter")
	root.wm_minsize(400,200)
	frame = Frame(root, relief=RIDGE, bg="BLUE", borderwidth=2)
	frame.pack(fill=BOTH,expand=1)
	
	label = Label(frame, font=20, bg="BLUE", text="What Would You Like to Do:")
	label.pack(fill=X, expand=1)
	
	butBrd = Button(frame, text="Convert Board",command=convertBoardGUI)
	butBrd.pack(fill=X,expand=1)
	butLib = Button(frame, text="Convert Library",command=convertLibGUI)
	butLib.pack(fill=X,expand=1)
	butSch = Button(frame, text="Convert Schematic",command=convertSchGUI)
	butSch.pack(fill=X,expand=1)
	
	label = Label(frame,bg="BLUE", text="www.github.com/Trump211")
	label.pack(fill=X, expand=1)
	
	root.mainloop()

def getRootNode(fileName):
	parser = XMLParser(encoding="UTF-8")
	node = ElementTree()
	node.parse(fileNameparser)
	node = node.getroot()
	return node

def convertBoardGUI():
	fileName=askopenfilename(title = "Board Input",
					filetypes=[('Eagle V6 Board', '.brd'), ('all files', '.*')],
					defaultextension='.brd')
	
	outFileName=asksaveasfilename(title="Board Output",
					filetypes=[('KiCad Board', '.brd'), ('all files', '.*')],
					defaultextension='.brd')
	
	val = convertBoard(fileName,outFileName)
	if val[0]:
		showinfo("Conversion Complete",val[1])
	else:
		showerror("Error",val[1])

def convertBoard(fileName,outFileName):
	logFile.write("*******************************************\n")
	logFile.write("Converting: "+fileName+"\n")
	logFile.write("Outputing: "+outFileName+"\n\n")
	
	try:
		
		node = getRootNode(fileName)	
		brd=Board(node)
		open(outFileName,'w').close()
		outFile=open(outFileName,"a")
		brd.write(outFile)
		outFile.close()
	
	except BaseException as e:	
		logFile.write("Conversion Failed\n\n")
		logFile.write(traceback.format_exc())
		logFile.write("*******************************************\n\n\n")
		return False, "Error Converting Board \n"+str(e)+\
					  "\nSee Log.txt for more info"

	
	logFile.write("Conversion Successfull\n\n")
	logFile.write("*******************************************\n\n\n")	
	return True,"The Board Has Finished Converting"

def convertLibGUI():
	fileName=askopenfilename(title = "Input Library",
				filetypes=[('Eagle V6 Library', '.lbr'),('all files', '.*')],
				defaultextension='.lbr')
	
	modFileName=asksaveasfilename(title="Module Output Filename", 
					filetypes=[('KiCad Module', '.mod'), ('all files', '.*')], 
					defaultextension='.mod')
	
	symFileName=asksaveasfilename(title="Symbol Output Filename", 
					filetypes=[('KiCad Symbol', '.lib'), ('all files', '.*')], 
					defaultextension='.lib')
	
	val = convertLib(fileName,symFileName,modFileName)
	if val[0]:
		showinfo("Conversion Complete",val[1])
	else:
		showerror("Error",val[1])
		
def convertLib(fileName,symFileName,modFileName):

	logFile.write("*******************************************\n")
	logFile.write("Converting Lib: "+fileName+"\n")
	logFile.write("Module Output: "+modFileName+"\n")
	logFile.write("Symbol Output: "+symFileName+"\n")
	
	name=fileName.replace("/","\\")
	name=name.split("\\")[-1]
	name=name.split(".")[0]
	
	logFile.write("Lib Name: "+name+"\n")
	
	try:
		node = getRootNode(fileName)
		node=node.find("drawing").find("library")	
		lib=Library(node,name)
		
		open(modFileName,'w').close()
		open(symFileName,'w').close()
				
		modFile=open(modFileName,"a")
		symFile=open(symFileName,"a")
					
		lib.writeLibrary(modFile,symFile)
		
		modFile.close()
		symFile.close()
	except BaseException as e:	
		logFile.write("Conversion Failed\n\n")
		logFile.write(traceback.format_exc())
		logFile.write("*******************************************\n\n\n")
		
		return False, "Error Converting Library: '"+name+"'\n"+str(e)+"\nSee Log.txt for more info"	

	
	logFile.write("Conversion Successfull\n")
	logFile.write("*******************************************\n\n\n")		
	
	return True, "Conversion of Library '"+name+"' Complete"

def convertSchGUI():
	val=convertSch("N/A","N/A")
	if val[0]:
		showinfo("Conversion Complete",val[1])
	else:
		showerror("Error",val[1])
			
def convertSch(schFile,outFile):
	logFile.write("*******************************************\n")
	logFile.write("Converting Schem: \n")
	logFile.write("Conversion Failed: \n\n")
	logFile.write("Schematic Conversion not yet Supported\n\n")
	logFile.write("*******************************************\n\n\n")	
	
	return False, "Converting Schematics is not yet supported"

def startCmdLine():
		# Setup argument parser
		parser = ArgumentParser()
		parser.add_argument("-l","-L","--Library", 
						dest="Library", 
						nargs=3,
						metavar=("inFile","symFile","modFile"), 
						help="Convert an Eagle Library",
						action="append",
						type=str)
		
		parser.add_argument("-b","-B","--Board",
						dest="Board",
						nargs=2,
						metavar=("inFile","brdFile"),
						help="Convert an Eagle Board",
						action="append",
						type=str)
		
		parser.add_argument("-s","-S","--Schematic",
						dest="Schem",
						nargs=2,
						metavar=("inFile","schFile"),
						help="Convert an Eagle Schematic",
						action="append",
						type=str)
		
		# Process arguments
		args = parser.parse_args()
		
		if args.Schem != None:
			for sch in args.Schem:
				val = convertSch(sch[0],sch[1])
				if val[0]:
					sys.stdout.write(val[1]+"\n")
				else:
					sys.stderr.write(val[1]+"\n")
					
		if args.Board != None:
			for brd in args.Board:
				val = convertBoard(brd[0],brd[1])
				if val[0]:
					sys.stdout.write(val[1]+"\n")
				else:
					sys.stderr.write(val[1]+"\n")
		
		if args.Library != None:
			for lib in args.Library:
				val = convertLib(lib[0],lib[1],lib[2])
				if val[0]:
					sys.stdout.write(val[1]+"\n")
				else:
					sys.stderr.write(val[1]+"\n")
								
def main():
	now=datetime.datetime.now()
	logFile.write("###############################################################################\n")
	logFile.write("#Session: "+now.strftime("%Y-%m-%d %H:%M:%S")+"\n")
	logFile.write("###############################################################################\n\n\n")
	
	if len(sys.argv)>1:
		startCmdLine()
	else:
		startGui()
		
if __name__ == "__main__":
	main()
			
