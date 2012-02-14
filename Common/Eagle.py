"""
Eagle.py
Describes an instance of an eagle File
"""
from xml.etree.ElementTree import ElementTree
from Board import Board
from Schematic import Schematic
from Library import Library

class Eagle():
    __slots__=('version','compatability','drawing')
    
    def __init__(self,root):
        self.version=root.get('version')
        self.drawing=Drawing(root.find('drawing'))

class Drawing():
    __slots__=('settings','grid','layers','EdaDoc')

    def __init__(self,Node):
        self.settings={}
        self.grid={}
        self.layers={}        
        self.getSettings(Node.find('settings'))
        self.getGrid(Node.find('grid'))
        self.getLayers(Node.find('layers'))
        self.getEDA(Node)
        
    def getGrid(self,gridNode):
#        <!ELEMENT grid EMPTY>
#        <!ATTLIST grid
#             distance      %Real;         #IMPLIED
#            unitdist      %GridUnit;     #IMPLIED
#            unit          %GridUnit;     #IMPLIED
#            style         %GridStyle;    "lines"
#            multiple      %Int;          "1"
#            display       %Bool;         "no"
#            altdistance   %Real;         #IMPLIED
#            altunitdist   %GridUnit;     #IMPLIED
#            altunit       %GridUnit;     #IMPLIED
        self.grid=gridNode.attrib
        
    def getSettings(self,settingsNode):
        for setting in settingsNode.findall('setting'):
            for key in setting.keys():
                self.settings[key]=setting.get(key)
                  
    def getLayers(self,layersNode):
        for layer in list(layersNode):#._children:
            self.layers[layer.get('number')]=Layer(layer)

    def getEDA(self,drawingRoot):
        if not drawingRoot.find('library')==None:
            self.EdaDoc=Library(drawingRoot.find('library'))
        elif not drawingRoot.find('schematic'):
            self.EdaDoc=Schematic(drawingRoot.find('schematic'))
        elif not drawingRoot.find('board'):
            self.EdaDoc=Board(drawingRoot.find('board'))

class Layer():
    __slots__=('attributes')
    def __init__(self,LayerNode):
        self.attributes=LayerNode.attrib
   

if __name__ == '__main__':
    """ Parse an Eagle XML file into a design """
    xmltree = ElementTree(file='test.xml')
    root = xmltree.getroot()    
    eagle=Eagle(root)
    print('')