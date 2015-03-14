import logging
import traceback
import os.path
from datetime import datetime
from argparse import ArgumentParser

from Board.Board import Board
from Library.Library import Library

# from Schematic.Schematic import Schematic
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import XMLParser


# noinspection PyUnresolvedReferences
def import_tk():
    global Tk, Frame, Label, Button, RIDGE, BOTH, X, askopenfilename, asksaveasfilename, showinfo, showerror
    from tkinter import Tk, Frame, Label, Button, RIDGE, BOTH, X
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename
    from tkinter.messagebox import showinfo, showerror

def startGui():
    try:
        import_tk()
    except:
        logging.error("Error Starting GUI. Could Not Find Tkinter module" + "Please install the Python Tkinter module")
        return

    root = Tk()
    root.wm_title("Eagle V6 to KiCad Converter")
    root.wm_minsize(400, 200)
    frame = Frame(root, relief=RIDGE, bg="BLUE", borderwidth=2)
    frame.pack(fill=BOTH, expand=1)

    label = Label(frame, font=20, bg="BLUE", text="What Would You Like to Do:")
    label.pack(fill=X, expand=1)

    butBrd = Button(frame, text="Convert Board", command=convertBoardGUI)
    butBrd.pack(fill=X, expand=1)
    butLib = Button(frame, text="Convert Library", command=convertLibGUI)
    butLib.pack(fill=X, expand=1)
    butSch = Button(frame, text="Convert Schematic", command=convertSchGUI)
    butSch.pack(fill=X, expand=1)

    label = Label(frame, bg="BLUE", text="www.github.com/Trump211")
    label.pack(fill=X, expand=1)

    root.mainloop()

def startCmdLine(args):
    if args.Schem is not None:
        for sch in args.Schem:
            convertSch(sch[0], sch[1])

    if args.Board is not None:
        for brd in args.Board:
            convertBoard(brd[0], brd[1])

    if args.Library is not None:
        for lib in args.Library:
            convertLib(lib[0], lib[1], lib[2])



def getRootNode(fileName):
    parser = XMLParser(encoding="UTF-8")
    node = ElementTree()
    node.parse(fileName, parser)
    node = node.getroot()
    return node


def convertBoardGUI():
    fileName = askopenfilename(title="Board Input", filetypes=[('Eagle V6 Board', '.brd'), ('all files', '.*')],
                               defaultextension='.brd')
    if not fileName:
        return

    outFileName = asksaveasfilename(title="Board Output", filetypes=[('KiCad Board', '.brd'), ('all files', '.*')],
                                    defaultextension='.brd', initialfile=os.path.splitext(fileName)[0] + "KiCad")
    if not outFileName:
        return

    val = convertBoard(fileName, outFileName)
    if val[0]:
        showinfo("Conversion Complete", val[1])
    else:
        showerror("Error", val[1])


def convertBoard(fileName, outFileName):
    logging.info("*******************************************")
    logging.info("Converting: " + fileName)
    logging.info("Outputing: " + outFileName + "\n")

    try:

        node = getRootNode(fileName)
        brd = Board(node)
        open(outFileName, 'w').close()
        outFile = open(outFileName, "a")
        brd.write(outFile)
        outFile.close()

    except BaseException as e:
        logging.error("Conversion Failed")
        logging.error(traceback.format_exc())
        logging.info("*******************************************\n\n")
        return False, "Error Converting Board \n" + str(e) + "\nSee Log.txt for more info"

    logging.info("Conversion Successfull")
    logging.info("*******************************************\n\n")
    return True, "The Board Has Finished Converting"


def convertLibGUI():
    fileName = askopenfilename(title="Input Library", filetypes=[('Eagle V6 Library', '.lbr'), ('all files', '.*')],
                               defaultextension='.lbr')
    if not fileName: return

    modFileName = asksaveasfilename(title="Module Output Filename",
                                    filetypes=[('KiCad Module', '.mod'), ('all files', '.*')], defaultextension='.mod',
                                    initialfile=os.path.splitext(fileName)[0])
    if not modFileName: return

    symFileName = asksaveasfilename(title="Symbol Output Filename",
                                    filetypes=[('KiCad Symbol', '.lib'), ('all files', '.*')], defaultextension='.lib',
                                    initialfile=os.path.splitext(fileName)[0])
    if not symFileName: return

    val = convertLib(fileName, symFileName, modFileName)

    if val[0]:
        showinfo("Conversion Complete", val[1])
    else:
        showerror("Error", val[1])


def convertLib(fileName, symFileName, modFileName):
    logging.info("*******************************************")
    logging.info("Converting Lib: " + fileName)
    logging.info("Module Output: " + modFileName)
    logging.info("Symbol Output: " + symFileName)

    name = fileName.replace("/", "\\")
    name = name.split("\\")[-1]
    name = name.split(".")[0]

    logging.info("Lib Name: " + name + "\n")

    try:
        node = getRootNode(fileName)
        node = node.find("drawing").find("library")
        lib = Library(node, name)

        open(modFileName, 'w').close()
        open(symFileName, 'w').close()

        modFile = open(modFileName, "a")
        symFile = open(symFileName, "a")

        lib.writeLibrary(modFile, symFile)

        modFile.close()
        symFile.close()

    except BaseException as e:
        logging.error("Error Converting Library: '" + name + "'")
        logging.error(traceback.format_exc())
        logging.info("*******************************************\n\n")
        return False, "Error Converting Library \n" + str(e) + "\nSee Log.txt for more info"

    logging.info("Conversion Successfull")
    logging.info("*******************************************\n\n")

    return True, "Conversion of Library '" + name + "' Complete"


def convertSchGUI():
    val = convertSch("N/A", "N/A")
    if val[0]:
        showinfo("Conversion Complete", val[1])
    else:
        showerror("Error", val[1])


def convertSch(schFile, outFile):
    logging.info("*******************************************")
    logging.info("Converting Schem: " + schFile)
    logging.info("Outputing: " + outFile)
    logging.error("Error Converting  " + schFile + ":")
    logging.error("Schematic Conversion not yet Supported")
    logging.info("*******************************************\n\n")

    return False, "Converting Schematics is not yet supported"



def parseargs():
    # Setup argument parser
    parser = ArgumentParser(prog="Eagle2KiCad")
    parser.add_argument("-l", "-L", "--Library", dest="Library", nargs=3, metavar=("inFile", "symFile", "modFile"),
                        help="Convert an Eagle Library", action="append", type=str)

    parser.add_argument("-b", "-B", "--Board", dest="Board", nargs=2, metavar=("inFile", "brdFile"),
                        help="Convert an Eagle Board", action="append", type=str)

    parser.add_argument("-s", "-S", "--Schematic", dest="Schem", nargs=2, metavar=("inFile", "schFile"),
                        help="Convert an Eagle Schematic", action="append", type=str)

    parser.add_argument('-v', '--verbosity', dest="Verbosity", choices=(0, 1), default=0, type=int,
                        help="Verbosity Level ")


    # Process arguments
    return parser.parse_args()

def setupLogging(verbosity, use_console):
    lvl = (logging.INFO, logging.DEBUG)[verbosity]

    logging.getLogger().setLevel(0)

    fh = logging.FileHandler("Log.txt")
    fh.setLevel(lvl)
    logging.getLogger().addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)  # always show Warnings and Errors in the Console
    if use_console:
        ch.setLevel(lvl)  # Use user preference if in non-gui mode
    logging.getLogger().addHandler(ch)

    logging.info("###############################################################################")
    logging.info("#Session: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logging.info("###############################################################################")
    logging.log(lvl, "Logging at Level: " + logging.getLevelName(lvl) + "\n\n")


def shutdownLogging():
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)

def main():
    args = parseargs()
    use_console = not (args.Board is None and args.Library is None and args.Schem is None)
    setupLogging(args.Verbosity, use_console)

    if use_console:
        startCmdLine(args)
    else:
        startGui()

    shutdownLogging()




if __name__ == "__main__":
    main()

