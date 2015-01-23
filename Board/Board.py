"""
Created on Apr 3, 2012

@author: Dan
"""

from xml.etree.ElementTree import ElementTree
from Common.Converter import Converter
from Common.Module import Module
from Common.Shapes import Track, Via, Line, Circle, Polyline, Text, Zone


class Board(object):
    """
    classdocs
    """

    __slots__ = ("signals", "contacts", "elements", "tracks", "plain", "Zones", "polygon")

    def __init__(self, xmlnode, converter=None):
        if converter is None:
            converter = Converter(xmlnode)

        self.signals = {}
        self.contacts = {}
        self.elements = []
        self.tracks = []
        self.polygon = []
        self.plain = []

        signals = xmlnode.find("drawing").find("board").find("signals")
        libraries = xmlnode.find("drawing").find("board").find("libraries").findall("library")
        elements = xmlnode.find("drawing").find("board").find("elements").findall("element")
        plain = xmlnode.find("drawing").find("board").find("plain")

        self.getContacts(signals)
        libraryDict = self.getLibDict(libraries)
        self.getModules(elements, libraryDict, converter)
        self.getTracks(signals, converter)
        self.getGraphics(plain, converter)


    def getContacts(self, signals):
        """
        Adds all contact References to the global variable 'contactRefs'
        which is a dictionary containing Keys for each component, and each key 
        points to another dictionary with the components pins as keys, where each 
        key contains the signal name that the pin is connected to
            
        Preconditions:
            The .brd file has been read in and myTree has been created
        
        Postconditions:
            the contactRefs variable has been set
        """
        i = 1
        for signal in signals:
            sigName = signal.get("name")

            #give a number to the signal
            if self.signals.get(sigName) is None:
                self.signals[sigName] = str(i)
                i += 1

            #make a dict of all contactRefs   
            sigRefs = signal.findall('contactref')
            if not sigRefs is None:
                for sigRef in sigRefs:
                    element = sigRef.get('element')
                    pad = sigRef.get('pad')

                    if self.contacts.get(element) is None:
                        self.contacts[element] = {}

                    if self.contacts[element].get(pad) is None:
                        self.contacts[element][pad] = {}

                    sigName = signal.get("name")
                    sigNum = self.signals.get(sigName)
                    self.contacts[element][pad]["name"] = sigName
                    self.contacts[element][pad]["num"] = sigNum

    def getLibDict(self, libraries):
        libDict = {}

        for library in libraries:
            libName = library.get("name")
            for package in library.find("packages").findall("package"):
                modName = package.get("name")
                if libDict.get(libName) is None:
                    libDict[libName] = {}
                libDict[libName][modName] = package

        return libDict

    def getModules(self, elements, libraryDict, converter):
        for element in elements:
            elementPackage = element.get("package")
            elementLib = element.get("library")
            libNode = libraryDict.get(elementLib).get(elementPackage)
            modContacts = self.contacts.get(element.get("name"))
            module = Module(libNode, converter, element, modContacts)
            self.elements.append(module)

    def getTracks(self, signals, converter):
        for signal in signals:
            tracks = signal.findall("wire")
            vias = signal.findall("via")
            zones = signal.findall("polygon")
            netCode = self.signals.get(signal.get("name"))
            for track in tracks:
                self.tracks.append(Track(track, converter, netCode))
            for via in vias:
                self.tracks.append(Via(via, converter, netCode))
            for _zone in zones:
                self.polygon.append(Zone(_zone, converter, signal.get("name"), netCode))

    def getGraphics(self, plain, converter):
        wires = plain.findall("wire")
        polygons = plain.findall("polygon")
        texts = plain.findall("text")
        circles = plain.findall("circle")

        for wire in wires:
            self.plain.append(Line(wire, converter))
        for polygon in polygons:
            self.plain.append(Polyline(polygon, converter))
        for text in texts:
            self.plain.append(Text(text, converter))
        for circle in circles:
            self.plain.append(Circle(circle, converter))

    def write(self, outFile):
        outFile.write('PCBNEW-BOARD Version 0 date 0/0/0000 00:00:00\n')
        self.writeEQUIPOT(outFile)
        self.writeMODULES(outFile)
        self.writeGRAPHICS(outFile)
        self.writeTRACKS(outFile)
        outFile.write("$EndBOARD\n")

    def writeEQUIPOT(self, outFile):
        """
        Writes the EQUIPOT Sections to the outFile
        
        Params:
            Outfile: the file to output to
        
        Postconditions:
            The section has been written to the outfile
        """
        for signal in self.signals:
            signame = signal
            num = self.signals.get(signame)
            outFile.write('$EQUIPOT\n')
            outFile.write('Na ' + num + ' ' + signame + '\n')
            outFile.write('St~\n')
            outFile.write('$EndEQUIPOT\n')

    def writeMODULES(self, outFile):
        for element in self.elements:
            element.write(outFile)

    def writeTRACKS(self, outFile):
        outFile.write("$TRACK\n")
        for track in self.tracks:
            outFile.write(track.boardRep())
        outFile.write("$EndTRACK\n")
        for zones in self.polygon:
            outFile.write(zones.boardRep())

    def writeGRAPHICS(self, outFile):
        for graphic in self.plain:
            outFile.write(graphic.boardRep())


if __name__ == "__main__":
    fileName = input("Input Filename: ")
    outFileName = input("Output Filename: ")

    name = fileName.replace("/", "\\")
    name = name.split("\\")[-1]
    name = name.split(".")[0]

    node = ElementTree(file=fileName)
    node = node.getroot()

    brd = Board(node)

    brd.write(open(outFileName, "a"))
