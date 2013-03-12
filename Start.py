import sys,inspect,os,traceback,datetime
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir+"\\Board")
sys.path.append(scriptDir+"\\Library")
sys.path.append(scriptDir+"\\Schematic")
sys.path.append(scriptDir+"\\Common")


from Board import Board
from Library import Library
#from Schematic import Schematic

from tkinter import Tk,Frame,Label,Button,RIDGE,BOTH,X
from tkinter.filedialog   import askopenfilename     
from tkinter.filedialog   import asksaveasfilename
from tkinter.messagebox	import showinfo,showerror
from xml.etree.ElementTree import ElementTree



logFile=open("Log.txt","a")

def startGui():
	root=Tk()
	root.wm_title("Eagle V6 to Kicad Converter")
	root.wm_minsize(400,200)
	frame = Frame(root, relief=RIDGE, bg="BLUE", borderwidth=2)
	frame.pack(fill=BOTH,expand=1)
	
	label = Label(frame, font=20, bg="BLUE", text="What Would You Like to Do:")
	label.pack(fill=X, expand=1)
	
	butBrd = Button(frame, text="Convert Board",command=convertBoard)
	butBrd.pack(fill=X,expand=1)
	butLib = Button(frame, text="Convert Library",command=convertLib)
	butLib.pack(fill=X,expand=1)
	butSch = Button(frame, text="Convert Schematic",command=convertSch)
	butSch.pack(fill=X,expand=1)
	
	label = Label(frame,bg="BLUE", text="www.github.com/Trump211")
	label.pack(fill=X, expand=1)
	
	root.mainloop()

def getRootNode(fileName):
	node = ElementTree(file=fileName)
	node = node.getroot()
	return node

def convertBoard():
	
	fileName=askopenfilename(title = "Board Input", filetypes=[('Eagle V6 Board', '.brd'), ('all files', '.*')], defaultextension='.brd') 
	outFileName=asksaveasfilename(title="Board Output", filetypes=[('KiCad Board', '.brd'), ('all files', '.*')], defaultextension='.brd')
	
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
	
	except Exception as e:
		showerror("Error",str(e)+"\nSee Log.txt for more info")		
		logFile.write("Conversion Failed\n\n")
		logFile.write(traceback.format_exc())
		logFile.write("*******************************************\n\n\n")
		return
	
	logFile.write("Conversion Successfull\n\n")
	logFile.write("*******************************************\n\n\n")	
	showinfo("Board Complete","The Board Has Finished Converting")
	
def convertLib():
	fileName=askopenfilename(title = "Input Library",filetypes=[('Eagle V6 Library', '.lbr'), ('all files', '.*')], defaultextension='.lbr') 
	modFileName=asksaveasfilename(title="Module Output Filename", filetypes=[('KiCad Module', '.mod'), ('all files', '.*')], defaultextension='.mod')
	symFileName=asksaveasfilename(title="Symbol Output Filename", filetypes=[('KiCad Symbol', '.lib'), ('all files', '.*')], defaultextension='.lib')
	
	logFile.write("*******************************************\n")
	logFile.write("Converting Lib: "+fileName+"\n")
	logFile.write("Module Output: "+modFileName+"\n")
	logFile.write("Symbol Output: "+symFileName+"\n")
	
	name=fileName.replace("/","\\")
	name=name.split("\\")[-1]
	name=name.split(".")[0]
	
	logFile.write("Lib name: "+name+"\n")
	
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
	except Exception as e:
		showerror("Error",str(e)+"\nSee Log.txt for more info")		
		logFile.write("Conversion Failed\n\n")
		logFile.write(traceback.format_exc())
		logFile.write("*******************************************\n\n\n")
		return
	
	logFile.write("Conversion Successfull\n")
	logFile.write("*******************************************\n\n\n")		
	showinfo("Library Complete","The Modules and Symbols Have Finished Converting \n Check Console for Errors")
		
def convertSch():
	logFile.write("*******************************************\n")
	logFile.write("Converting Schem: \n")
	logFile.write("Conversion Failed: \n\n")
	logFile.write("Schematic Conversion not yet Supported\n\n")
	logFile.write("*******************************************\n\n\n")	
	
	showerror("Error","Converting Schematics is not yet supported")

if __name__ == "__main__":
	now=datetime.datetime.now()
	logFile.write("###############################################################################\n")
	logFile.write("#Session: "+now.strftime("%Y-%m-%d %H:%M:%S")+"\n")
	logFile.write("###############################################################################\n\n\n")
	
	startGui()
			
