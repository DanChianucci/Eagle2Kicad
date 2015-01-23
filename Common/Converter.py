"""
Created on Apr 2, 2012

@author: Dan
"""


class Converter(object):
    __slots__ = ("border", "cX", "cY", "factor", "rotFactor")

    def __init__(self, node=None):
        self.factor = 10000 / 25.4
        self.rotFactor = 10
        if node is None:
            self.border = None
            self.cX = 0
            self.cY = 0
        else:
            self.getBorder(node)

    def getBorder(self, node):
        """
        Gets the bounding box of the entire Board based on the board outline layer
        
        Returns:
            a dictionary containing info about the bounding box
            keys= left, right, top, bottom, cX, cY
        
        Preconditions:
            The board must have an edge Layer to get the bounds from
        """
        left = float('inf')
        right = float('-inf')
        top = float('-inf')
        bottom = float('inf')

        wires = node.find('drawing').find('board').find('plain').findall('wire')

        for wire in wires:
            if wire.get('layer') == '20':
                xs = (float(wire.get('x1')), float(wire.get('x2')))
                ys = (float(wire.get('y1')), float(wire.get('y2')))

                if max(xs) > right:
                    right = max(xs)
                if min(xs) < left:
                    left = min(xs)
                if max(ys) > top:
                    top = max(ys)
                if min(ys) < bottom:
                    bottom = min(ys)

        cX = (right - left) / 2
        cY = (top - bottom) / 2

        if abs(cX) == float('inf'):
            cX = 0

        if abs(cY) == float('inf'):
            cY = 0

        cX, cY = self.convertCoordinate(cX, cY, True)

        self.cX = cX
        self.cY = cY

    def convertUnit(self, unit):
        """
        Converts between Eagle mm and Kicad deciMils
        Param:
            units: the unit in mm
        Returns:
            string the unit in deciMils or none
        """
        return int(float(unit) * self.factor)

    def convertCoordinate(self, x, y, noTranspose=False, noInvert=False):
        """
        Converts between Eagle coordinates and Kicad coordinates by converting units,
        inverting the y axis, and centering the board onto the screen
        
        Params:
            x: the x position from Eagle
            y: the y position from Eagle
            noTranspose:     if True, board will not be centered
            noinvert:        if True, the y axis will not be inverted and the board 
                                will come out upside down
        Returns:
            (x,y): the coordinate in Kicad units
        """

        xTranspose = 0 if noTranspose else 58500 - self.cX
        yTranspose = 0 if noTranspose else 41355 - self.cY

        invertFactor = 1 if noInvert else -1

        if not x is None:
            x = xTranspose + int(float(x) * self.factor)
        if not y is None:
            y = yTranspose + int(invertFactor * float(y) * self.factor)
        return x, y

    def convertRotation(self, rotString):
        """
        Returns Eagle rotation strings to kicad rotations
    
        Params:
            rot: the eagle rotation string
    
        Returns:
            a kicad formatted dict with keys:
                rot,mirror,spin
     
        """

        mirror = False
        spin = False
        rot = 0

        if str(rotString) != "None":
            #mirror the rotation
            if rotString.find("M") >= 0:
                mirror = True
                rotString = rotString.replace("M", "")
                #spin the rotation
            if rotString.find("S") >= 0:
                spin = True
                rotString = rotString.replace("S", "")

            rotString = rotString.replace("R", "")
            rot = int(float(rotString) * 10)
        return {'rot': rot, 'mirror': mirror, 'spin': spin}


class SchemConverter(Converter):
    def __init__(self):
        Converter.__init__(self, None)
        self.factor = 1000 / 25.4

    def convertCoordinate(self, x, y, noTranspose="NotUsed", noInvert="notUsed"):
        return Converter.convertCoordinate(self, x, y, True, True)