'''
Created on Apr 3, 2012

@author: Dan
'''
import sys
if "../Common" not in sys.path:
    sys.path.append("..\Common")

from Converter import Converter, SchemConverter
from Module import Module
from Symbol import Symbol
from xml.etree.ElementTree import ElementTree

class Library(object):
    __slots__=("name","modules","symbols","converter")
    
    def __init__(self,node,name,converter=None):
        

        self.name=name
        
        if converter==None:
            converter=Converter()
        symConverter=SchemConverter()

        self.modules=[]
        self.symbols=[]
        
        packages=node.find("packages").findall("package")
        symbols=node.find("symbols").findall("symbol")
        
        if packages !=None:
            for package in packages:
                self.modules.append(Module(package,converter))
        if symbols!=None:
            for symbol in symbols:
                self.symbols.append(Symbol(symbol,symConverter))
        
    def writeLibrary(self, modFile=None , symFile=None , docFile=None ):
        if modFile != None:
            self.writeModFile(modFile)
        if symFile != None:
            self.writeSymFile(symFile)
        if docFile != None:
            self.writeDocFile(docFile)
    
    def writeModFile(self,modFile):
        modFile.write("PCBNEW-LibModule-V1   00/00/0000-00:00:00\n")
        
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
        for symbol in self.symbols:
            symbol.write(symFile)
        symFile.write("# End Library")

    def writeDocFile(self,docFile):
        docFile.write("EESchema-DOCLIB  Version 0.0  Date: 00/00/0000 00:00:00\n")

if __name__=="__main__":
    fileName=input("Input Library: ") 
    modFileName=input("Output Modules: ") 
    symFileName=input("Output Symbols: ") 
    
    name=fileName.replace("/","\\")
    name=name.split("\\")[-1]
    name=name.split(".")[0]
    
    node = ElementTree(file=fileName)
    node = node.getroot()
    node = node.find("drawing").find("library")
    
    lib=Library(node,name)    
    modFile=open(modFileName,"a")
    symFile=open(symFileName,"a")
    lib.writeLibrary(modFile,symFile)

        
