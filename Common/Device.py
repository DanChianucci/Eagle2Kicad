"""
Created on 9 Oct 2012

@author: konmik
"""


class Connect(object):
    """represents connect tag"""

    def __init__(self, node, converter):
        self.gate = node.get("gate")
        self.pin = node.get("pin")
        self.pad = node.get("pad")


class Technology(object):
    """represents technology tag"""

    def __init__(self, node, converter):
        self.name = node.get("name")


class Device(object):
    """represents device tag"""

    def __init__(self, node, converter):
        self.connects = {}
        self.name = node.get("name")
        self.package = node.get("package")
        self.fullName = self.name
        self.technologies = []

        technologies = node.find("technologies")
        if technologies is not None:
            for technology in technologies:
                t = Technology(technology, converter)
                self.technologies.append(t)

        connects = node.find("connects")
        if connects is not None:
            for connect in connects:
                c = Connect(connect, converter)
                self.connects[c.pin] = c

    def setFullName(self, prefix):
        if prefix[-1:] == "*":  #does set name has *
            self.fullName = prefix[:-1] + self.name
        else:
            self.fullName = prefix + self.name

    def getPadsByPinName(self, name):
        if self.connects.get(name) is not None:
            return self.connects.get(name).pad.split()
        else:
            return ["NC"]


class Gate(object):
    """represents gate tag, it is used when we may swap patrt o device"""

    def __init__(self, node, converter):
        self.name = node.get("name")
        self.symbol = node.get("symbol")
        self.x = node.get("x")
        self.y = node.get("y")
        #TODO: some attributes are ignored

    def getSymbol(self):
        return self.symbol

    def getName(self):
        return self.name


class Deviceset(object):
    """represents deviceset tag, it is used to mutch differnt packages to the same symbol"""

    def __init__(self, node, converter):
        self.gates = []
        self.devices = []

        self.name = node.get("name")
        self.prefix = node.get("prefix")

        gates = node.find("gates")
        if gates != None:
            for gate in gates:
                g = Gate(gate, converter)
                self.gates.append(g)  # put to the dict. for faster access

        devices = node.find("devices")
        if devices != None:
            for device in devices:
                self.devices.append(Device(device, converter))


    def isSymbolIncluded(self, symbol):
        """@return true if here is a gate for the symbol"""
        return symbol in self.gates

    def getDevices(self):
        return self.devices

    def getGates(self):
        return self.gates


