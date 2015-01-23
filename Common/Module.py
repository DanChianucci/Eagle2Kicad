from Common.Shapes import *
import logging

class Module(object):
    """
    Represents a module aka footprint
    """
    __slots__ = ("x", "y", "rotation", "mirror", "layer", "package",
                 "description", "keywords", "reference", "value", "drawings",
                 "pads", "texts", "contacts")

    def __str__(self):
        return "Module: " + str(self.package)

    def __init__(self, node, converter, elementNode=None, contacts=None):
        if elementNode is None:
            self.x = 0
            self.y = 0
            self.rotation = 0
            self.mirror = False
            self.layer = 15

        else:
            self.x, self.y = converter.convertCoordinate(elementNode.get("x"), elementNode.get("y"))
            rotation = converter.convertRotation(elementNode.get("rot"))
            self.rotation = rotation.get('rot')
            self.mirror = rotation.get('mirror')
            self.layer = 0 if self.mirror else 15

        if contacts is None:
            self.contacts = {}
        else:
            self.contacts = contacts

        self.package = node.get("name")

        description = node.find("description")
        if description is not None:
            self.description = str(description.text).split('\n')[0]
        else:
            self.description = ""

        self.keywords = ""
        self.reference = "T0 0 0 0 0 0 0 N I 25 \"ref**\"\n"
        self.value = "T1 0 0 0 0 0 0 N I 26 \"val**\"\n"
        self.drawings = []
        self.pads = []

        self.getParts(node, converter, elementNode)

    def getParts(self, node, converter, elementNode=None):
        #(polygon | wire | text | circle | rectangle | frame | hole | pad | smd)

        self.drawings = []

        lines = node.findall("wire")
        if lines is not None:
            for line in lines:
                line = Line(line, converter, True)
                self.drawings.append(line)

        polygons = node.findall("polygon")
        if polygons is not None:
            for polygon in polygons:
                polygon = Polyline(polygon, converter, True)
                self.drawings.append(polygon)

        circles = node.findall("circle")
        if circles is not None:
            for circ in circles:
                circ = Circle(circ, converter, True)
                self.drawings.append(circ)

        rectangles = node.findall("rectangle")
        if rectangles is not None:
            for rect in rectangles:
                rect = Rectangle(rect, converter, True)
                self.drawings.append(rect)

        self.texts = []
        #TODO replacing the ref with the actual name will mess up the positioning
        texts = node.findall("text")
        if texts is not None:
            for text in texts:
                text = Text(text, converter, True)
                if text.val == ">NAME":
                    if elementNode is not None:
                        text.val = elementNode.get("name")
                    self.reference = text.moduleRep(0)
                elif text.val == ">VALUE":
                    if elementNode is not None:
                        text.val = elementNode.get("value")
                    self.value = text.moduleRep(1)
                else:
                    self.texts.append(text)

        self.pads = []
        holes = node.findall("hole")
        for hole in holes:
            hole = Hole(hole, converter, True)
            self.pads.append(hole)

        pads = node.findall("pad")
        for pad in pads:
            contact = self.contacts.get(pad.get("name"))
            pad = Pad(pad, converter, self.rotation, self.mirror, contact)
            self.pads.append(pad)

        smds = node.findall("smd")
        for smd in smds:
            contact = self.contacts.get(smd.get("name"))
            smd = Pad(smd, converter, self.rotation, self.mirror, contact)
            self.pads.append(smd)

    def write(self, outFile):
        logging.debug("Writing Module "+str(self.package))

        outFile.write("$MODULE " + self.package + "\n")
        outFile.write("Po " + str(self.x) + " " + str(self.y) + " " + str(self.rotation) + " " + str(
            self.layer) + " " + "00000000 00000000 ~~\n")
        outFile.write("Li " + self.package + "\n")
        if self.description != "":
            outFile.write("Cd " + self.description + "\n")
        if not self.keywords == "":
            outFile.write("Kw " + self.keywords + "\n")

        outFile.write("Sc 00000000\n")
        outFile.write("Op 0 0 0\n")

        #Field Descriptions
        outFile.write(self.reference)
        outFile.write(self.value)
        goto = min((10, len(self.texts)))#only 12 fields
        for _i in range(goto):
            outFile.write(self.texts[_i].moduleRep(_i + 2))

        #drawings
        for elem in self.drawings:
            outFile.write(elem.moduleRep())


        #        #Pads
        for pad in self.pads:
            outFile.write(pad.moduleRep())

        outFile.write("$EndMODULE " + self.package + "\n")


class Pad(object):
    __slots__ = ("name", "drill", "xSize", "ySize", "x", "y", "contact", "kind", "shape", "layerMask", "rot")

    def __init__(self, node, converter, modRot=0, modMirror=False, contact=None):
        #PAD Shape: (square | round | octagon | long | offset)
        """
        Gets info for a given pad
        
        Params:
            node: the pad's xml node
            modRot: the rotation of the module in 10th of a degree
            modMirror, whether the module is mirrored or not
            contact, the contactRef of the pad         
        """

        rot = modRot
        pName = node.get("name")
        shapeType = node.tag
        pX, pY = converter.convertCoordinate(node.get('x'), node.get('y'), True)

        if shapeType == 'pad':
            drill = converter.convertUnit(node.get('drill'))
            if node.get('diameter') is None:
                diameter = str(int(int(drill) * 1.5))#TODO find default diameter for vias i think its 0
            else:
                diameter = converter.convertUnit(node.get('diameter'))
            xSize = diameter
            ySize = diameter
            kind = 'STD'
            layerMask = '00C0FFFF'#00C0FFFF should tell it to go through all layers
            shape = 'O'

        elif shapeType == 'smd':#TODO smd roundness
            drill = 0
            xSize = converter.convertUnit(node.get('dx'))
            ySize = converter.convertUnit(node.get('dy'))
            kind = 'SMD'
            layerMask = '00440001' if modMirror else '00888000'
            shape = 'R'

        else:
            drill = 0
            xSize = 0
            ySize = 0
            kind = '0'
            layerMask = '0'
            shape = '0'

        if not node.get('rot') is None:
            pRot = converter.convertRotation(node.get('rot')).get('rot')
            rot = int(pRot) + int(modRot)

        self.name = pName
        self.drill = str(drill)
        self.xSize = str(xSize)
        self.ySize = str(ySize)
        self.x = str(pX)
        self.y = str(pY)
        self.contact = contact
        self.kind = kind
        self.shape = shape
        self.layerMask = layerMask
        self.rot = str(rot)

    def moduleRep(self):
        myString = '$PAD\n'
        myString += 'Sh "' + self.name + '" ' + self.shape + ' ' + self.xSize + ' ' + self.ySize + ' 0 0 ' + self.rot \
                    + '\n'
        myString += 'Dr ' + self.drill + ' 0 0\n'
        myString += 'At ' + self.kind + ' N ' + self.layerMask + '\n'
        if not self.contact is None:
            myString += 'Ne ' + self.contact.get('num') + ' "' + self.contact.get('name') + '"\n'
        myString += 'Po ' + self.x + ' ' + self.y + '\n'
        myString += '$EndPAD\n'
        return myString


class Hole(object):
    __slots__ = ("x", "y", "drill", "layerMask")

    def __init__(self, node, converter, noTranspose=False):
        self.layerMask = "00E0FFFF"
        x, y = converter.convertCoordinate(node.get("x"), node.get("y"), noTranspose)
        drill = converter.convertUnit(node.get("drill"))
        self.x = str(x)
        self.y = str(y)
        self.drill = str(drill)

    def moduleRep(self):
        myString = '$PAD\n'
        myString += 'Sh \"Hole\" C ' + self.drill + ' ' + self.drill + ' 0 0 0\n'
        myString += 'Dr ' + self.drill + ' 0 0\n'
        myString += 'At HOLE N ' + self.layerMask + '\n'
        myString += 'Po ' + self.x + ' ' + self.y + '\n'
        myString += '$EndPAD\n'
        return myString

    def brdRep(self):
        print("Warning: Holes are not allowed outside of module footprints")
        print("\tHole at: " + str((self.x, self.y)) + " \tSize: " + self.drill)
        return ""