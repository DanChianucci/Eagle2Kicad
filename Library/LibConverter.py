'''
Created on Dec 23, 2011

@author: Dan Chianucci
'''
from libParser import libParser

myDict={}
contactRefs={}
signalIds={}
layerIds={}

def getLayerIds():
    global layerIds
    layerIds={'1':'15',
               '2':'14',
               '3':'13',
               '4':'12',
               '5':'11',
               '6':'10',
               '7':'9',
               '8':'8',
               '9':'7',
               '10':'6',
               '11':'5',
               '12':'4',
               '13':'3',
               '14':'2',
               '15':'1',
               '16':'0',
               '20':'28',
               '21':'21',
               '22':'20',
               '25':'25',
               '26':'25',
               '27':'26',
               '28':'26',
               '29':'23',
               '30':'22',
               '31':'19',
               '32':'18',
               '35':'17',
               '36':'16',
               '51':'26',
               '52':'27',
               '95':'26',
               '96':'27'}

def getContactRefs():
    global contactRefs
    signals=myDict['eagle']['drawing']['board']['signals']
    
    for signal in signals:
        sigRefs=signals[signal].get('contactref')
        if not sigRefs==None:
            for ref in sigRefs:
                element = sigRefs[ref]['element']
                pad=sigRefs[ref]['pad']           
                
                if contactRefs.get(element)==None:
                    contactRefs[element]={}
                contactRefs[element][pad]=signal


def main(inFileName=None,outFileName=None):
    global myDict
    if inFileName == None:
        inFile=open(input("Enter Name of Eagle File: "))
    else:
        inFile=open(inFileName)
    
    b=libParser()
    myDict=b.parse(inFile)
    getContactRefs()
    getLayerIds()
    printKicadFile(outFileName)

def printKicadFile(outFileName=None):
    pass

if __name__ == '__main__':
    main()

