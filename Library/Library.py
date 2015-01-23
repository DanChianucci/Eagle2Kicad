'''
Created on Apr 3, 2012

@author: Dan
'''

from Common.Converter import *
from Common.Module import *
from Common.Symbol import DevicePart
from Common.Device import Deviceset


class Library(object):
    __slots__ = ("name", "modules", "symbols", "converter", "deviceparts")

    def __init__(self, node, name, converter=None):


        self.name = name

        if converter is None:
            converter = Converter()
        symConverter = SchemConverter()

        self.modules = []
        self.deviceparts = []
        devicesetsLst = []
        symbolsHash = {}

        packages = node.find("packages").findall("package")
        if packages != None:
            for package in packages:
                self.modules.append(Module(package, converter))

        devicesets = node.find("devicesets").findall("deviceset")
        if devicesets != None:
            for deviceset in devicesets:
                ds = Deviceset(deviceset, symConverter)
                devicesetsLst.append(ds)

        symbols = node.find("symbols").findall("symbol")
        if symbols != None and len(devicesetsLst) != 0: #strange if not?
            for symbol in symbols:
                sn = symbol.get("name")
                if sn in symbolsHash:
                    print("The symbol with the same name %s already exists!" % sn)
                else:
                    symbolsHash[sn] = symbol

            for deviceset in devicesetsLst: #strange if not?
                #just iterater over all posible device packages
                for device in deviceset.getDevices():
                    #we have to create a number of symbols to match diffrent pin configurations
                    #the real name of device is <deviceset> name plus name of <device>
                    #symlink is just a scheme representation of the set of devices or devicessts 
                    device.setFullName(deviceset.name)
                    dp = DevicePart(device, symbolsHash, deviceset.getGates(), symConverter)
                    self.deviceparts.append(dp)


    def writeLibrary(self, modFile=None, symFile=None, docFile=None):
        if modFile != None:
            self.writeModFile(modFile)
        if symFile != None:
            self.writeSymFile(symFile)
        if docFile != None: #not used at the moment
            self.writeDocFile(docFile)

    def writeModFile(self, modFile):
        modFile.write("PCBNEW-LibModule-V1   00/00/0000-00:00:00\n")

        modFile.write("$INDEX\n")
        for module in self.modules:
            modFile.write(module.package + "\n")
        modFile.write("$EndINDEX\n")

        for module in self.modules:
            module.write(modFile)

        modFile.write("$EndLIBRARY")
        modFile.close()

    def writeSymFile(self, symFile):
        symFile.write("EESchema-LIBRARY Version 0.0  00/00/0000-00:00:00\n")
        for devicepart in self.deviceparts:
            devicepart.write(symFile)
        symFile.write("# End Library")

    def writeDocFile(self, docFile):
        docFile.write("EESchema-DOCLIB  Version 0.0  Date: 00/00/0000 00:00:00\n")

        
