'''
Created on Apr 3, 2012

@author: Dan
'''
from Converter import Converter
from Module import Module
from xml.etree.ElementTree import ElementTree

class Library(object):
    #<!ELEMENT library (description?, packages?, symbols?, devicesets?)>
    #<!ATTLIST library
    #        name          %String;       #REQUIRED -- only in libraries used inside boards or schematics --
    #     >
    __slots__=("name","modules","symbols","converter")
    
    def __init__(self,node,name,converter=None):
        

        self.name=name
        
        node = ElementTree(file=fileName)
        node = node.getroot()
        node = node.find("drawing").find("library")
        
        if converter==None:
            converter=Converter()

        self.modules=[]
        self.symbols=[]
        
        packages=node.find("packages").findall("package")
        symbols=node.find("symbols").findall("symbol")
        
        if packages !=None:
            for package in packages:
                self.modules.append(Module(package,converter))
#        if symbols!=None:
#            for symbol in symbols:
#                self.symbols[symbol.get("name")]=Symbol(symbol)
        
    def writeLibrary(self, modFile=None , symFile=None , docFile=None ):
        if modFile != None:
            self.writeModFile(modFile)
        if symFile != None:
            self.writeSymFile(symFile)
        if docFile != None:
            self.writeDocFile(docFile)
    
    def writeModFile(self,modFile):
        modFile.write("PCBNEW-LibModule-V0   00/00/0000-00:00:00\n")
        
        modFile.write("$INDEX\n")
        for module in self.modules:
            modFile.write(module.package+"\n")
        modFile.write("$EndINDEX\n")        
        
        for module in self.modules:
            module.write(modFile)
        
        modFile.write("$EndLIBRARY")
        modFile.close()
        
    def writeSymFile(self,symFile):
        symFile.write("EESchema-LIBRARY Version 0.0  00/00/0000-00:00:00\n")

    def writeDocFile(self,docFile):
        docFile.write("EESchema-DOCLIB  Version 0.0  Date: 00/00/0000 00:00:00\n")

if __name__=="__main__":
    fileName=input("Input Filename: ")
    outFileName=input("Output Filename: ")
    
    name=fileName.replace("/","\\")
    name=name.split("\\")[-1]
    name=name.split(".")[0]
    node = ElementTree(file=fileName)
    node = node.getroot()
    node = node.find("drawing").find("library")
    lib=Library(node,name)    
    file=open(outFileName,"a")
    lib.writeLibrary(file)
    print("DONE!")         
        