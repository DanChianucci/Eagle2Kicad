'''
Created on Dec 23, 2011

@author: Dan Chianucci
'''
from xml.etree.ElementTree import ElementTree
import codecs
import os
from Elements import LibModule, Converter



class LibConverter:
    __slots__=("name","modDir","symDir","tree","converter")
    
    myTree={}
    
    def __init__(self,fileName):
        self.name=fileName[:fileName.index('.')]
        self.modDir="Libraries/Modules"
        self.symDir="Libraries/Symbols"
        xmlTree = ElementTree(file=fileName)
        self.tree=xmlTree.getroot()
        self.converter=Converter()

        
    
    def writeLibFiles(self):
        os.makedirs(self.modDir,exist_ok=True)
        os.makedirs(self.symDir,exist_ok=True)
        
        modFileName=self.modDir+"/"+self.name+".mod"
        symFileName=self.symDir+"/"+self.name+".lib"
        docFileName=self.symDir+"/"+self.name+".dcm"
        
        modFile=codecs.open(modFileName,'w','utf-8')
        modFile.write("PCBNEW-LibModule-V0   00/00/0000-00:00:00\n")
        modFile.close()
        modFile=codecs.open(modFileName,'a','utf-8')
        
        symFile=codecs.open(symFileName,'w','utf-8')
        symFile.write("EESchema-LIBRARY Version 0.0  00/00/0000-00:00:00\n")
        symFile.close()
        symFile=codecs.open(symFileName,'a','utf-8')
        
        docFile=codecs.open(docFileName,'w','utf-8')
        docFile.write("EESchema-DOCLIB  Version 0.0  Date: 00/00/0000 00:00:00\n")
        docFile.close()
        docFile=codecs.open(docFileName,'a','utf-8')
        
        libnode=self.tree.find("drawing").find("library")
        packages=libnode.find("packages").findall("package")
        symbols=libnode.find("symbols").findall("symbol")
        
        modFile.write("$INDEX\n")
        for package in packages:
            modFile.write(str(package.get("name"))+"\n")
        modFile.write("$EndINDEX\n")
        
        for package in packages:
            self.writeModule(modFile,package)

        for symbol in symbols:
            self.writeSymbol(symFile,symbol)
            self.writeDoc(docFile,symbol)

        modFile.write("$EndLIBRARY")
        modFile.close()
        symFile.close()
        docFile.close()
    def writeModule(self,modFile,node):
        mod=LibModule(node,self.converter)
        mod.write(modFile)
    def writeSymbol(self,symFile,node):
        pass
    def writeDoc(self,docFile,node):
        pass

if __name__ == '__main__':
    a= LibConverter("myLib.xml")
    a.writeLibFiles()

