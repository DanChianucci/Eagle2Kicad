"""
Created on Apr 2, 2012

@author: Dan
"""


def getLayerId(layer):
    myDict = {'1': '15', #Component Layer (Top)
              '2': '14',
              '3': '13',
              '4': '12',
              '5': '11',
              '6': '10',
              '7': '9',
              '8': '8',
              '9': '7',
              '10': '6',
              '11': '5',
              '12': '4',
              '13': '3',
              '14': '2',
              '15': '1',
              '16': '0', #Copper Layer (Bottom)
              '20': '28', #Edge Layer
              '21': '21', #Component Silk Screen
              '22': '20', #Copper Silk Screen
              '25': '26', #tNames -> ECO1
              '26': '27', #bNames -> ECO2
              '27': '26', #tValues -> ECO1
              '28': '27', #bValues -> ECO2
              '29': '23', #Component Solder Mask
              '30': '22', #Copper Solder Mask
              '31': '19', #Component Solderpaste
              '32': '18', #Copper Solderpaste
              '35': '17', #Component Adhesive
              '36': '16', #Copper Adhesive
              '51': '25', #tDocu -> Comments
              '52': '25'}   #bDocu -> Comments

    if myDict.get(layer) is None:
        return '24'     #if its not in the dict put it on the draw layer

    return myDict.get(layer)


def makeLayerMask(layerList):
    pass


def makeViaMask(extent):
    hexDict = {'0': '0',
               '1': '1',
               '2': '2',
               '3': '3',
               '4': '4',
               '5': '5',
               '6': '6',
               '7': '7',
               '8': '8',
               '9': '9',
               '10': 'A',
               '11': 'B',
               '12': 'C',
               '13': 'D',
               '14': 'E',
               '15': 'F'}
    extent = extent.split("-")
    extent[0] = getLayerId(extent[0])
    extent[1] = getLayerId(extent[1])
    extent[0] = hexDict[extent[0]]
    extent[1] = hexDict[extent[1]]
    return extent[1] + extent[0]

    