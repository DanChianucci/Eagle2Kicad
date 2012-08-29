import sys,inspect,os
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir+"\\Board")
sys.path.append(scriptDir+"\\Library")
sys.path.append(scriptDir+"\\Schematic")
sys.path.append(scriptDir+"\\Common")


import Board
import Library
#import Schematic

from tkinter import Tk,Frame,Label,Button,RIDGE,BOTH,X
from tkinter.filedialog   import askopenfilename     
from tkinter.filedialog   import asksaveasfilename
from tkinter.messagebox	import showinfo,showerror
from xml.etree.ElementTree import ElementTree


def getChoice():
	print("What Would You Like to Do:")
	print("\t1. Convert Board")
	print("\t2. Convert Library")
	print("\t3. Convert Schematic")
	print("\t4. Quit")
	action=int(input("Input your choice: "))
	if action < 1 or action > 4:
		print("Invalid choice please enter a number")
	print("\n\n")
	return action
	
def main():
	choice=0	
	while(True):
		choice=getChoice()
		if choice ==1:
			print("Converting Board")
			file = input("Board Filename: ")
			print("File is "+file)
			
		elif choice==2:
			print("Converting Library")
			file = input("Library Filename: ")
			print("Library is " + file)
			
		elif choice==3:
			print("Schematic conversion not supported at this time")
			
		elif choice == 4:
			return
			
		else:
			pass



def startGui():
	root=Tk()
	root.wm_title("Eagle V6 to Kicad Converter")
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
		
	node = getRootNode(fileName)	
	brd=Board.Board(node)	
	brd.write(open(outFileName,"a"))
	showinfo("Board Complete","The Board Has Finished Converting \n Check Console for Errors")
	
def convertLib():
	fileName=askopenfilename(title = "Input Library",filetypes=[('Eagle V6 Library', '.lbr'), ('all files', '.*')], defaultextension='.lbr') 
	modFileName=asksaveasfilename(title="Module Output Filename", filetypes=[('KiCad Module', '.mod'), ('all files', '.*')], defaultextension='.mod')
	symFileName=asksaveasfilename(title="Symbol Output Filename", filetypes=[('KiCad Symbol', '.lib'), ('all files', '.*')], defaultextension='.lib')
	
	name=fileName.replace("/","\\")
	name=name.split("\\")[-1]
	name=name.split(".")[0]
	
	node = getRootNode(fileName)
	node=node.find("drawing").find("library")
	
	lib=Library.Library(node,name)			
	modFile=open(modFileName,"a")
	symFile=open(symFileName,"a")
			
	lib.writeLibrary(modFile,symFile)
	showinfo("Library Complete","The Modules and Symbols Have Finished Converting \n Check Console for Errors")
		
def convertSch():
	showerror("Error","Converting Schematics is not yet supported")

if __name__ == "__main__":
	startGui()		
