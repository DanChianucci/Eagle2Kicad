'''
Created on Dec 23, 2011

@author: Dan Chianucci
'''
from xml.parsers.expat import ParserCreate
import codecs

myDict={}
tree=[]
level=0
polygonIndex=-1
polygonHolder=''
lastPolygonHolder=''
textHolder=''
lastTextHolder=''
textIndex=-1
addTo=myDict
contactRefs={}
signalIds={}

def main():
    inFile=open(input("Enter Name of Eagle File: "))
    contents=''
    for line in inFile:
        contents+=line.strip()  
    parse(contents)
    getContactRefs()
    printKicadFile()

def getContactRefs():
    global contactRefs
    signals=myDict['eagle']['drawing']['board']['signals']
    
    for signal in signals:
        sigRefs=signals[signal]['contactref']
        for ref in sigRefs:
            element = sigRefs[ref]['element']
            pad=sigRefs[ref]['pad']           
            
            if contactRefs.get(element)==None:
                contactRefs[element]={}
            contactRefs[element][pad]=signal

def printKicadFile():
    out=codecs.open(input("Output File: "),'a','utf-8')
    print()
    out.write('PCBNEW-BOARD Version 0 date 0/0/0000 00:00:00\n\n')
    
    writeEQUIPOT(out)
    writeMODULES(out)
    writeSEGMENTS(out)
    writeTRACKS(out)
    writeZONES(out)
#    Descriptions=['TRACK','ZONE','CZONE_OUTLINE',]
#    for desc in Descriptions:
#        writeDescriptionFor(desc,out,info)
    
    out.write('$EndBOARD')
    out.close()

def writeEQUIPOT(outFile):
    global myDict
    global signalIds
    subDict=myDict['eagle']['drawing']['board']['signals'] 
    i=0
    for signal in subDict:
        i+=1
        name=subDict[signal].get('name')
        signalIds[name]=str(i)
        outFile.write('$EQUIPOT\n')
        outFile.write('Na '+str(i)+' '+name+'\n')
        outFile.write('St~\n')
        outFile.write('$EndEQUIPOT\n\n')

def writeMODULES(outFile):
    global myDict
    global signalIds
    global contactRefs
    
    subDict=myDict['eagle']['drawing']['board']['elements']
    for name in subDict:
        info=subDict[name]
        package=info['package']
        library=info['library']
        libInfo=myDict['eagle']['drawing']['board']['libraries'][library]['packages'][package]
        x=convertCoordinate(info['x'])
        y=convertCoordinate(-float(info['y']))
        
        mirror=False
        if info.get('rot')==None:
            rot='0'
        else:
            rot=info['rot']
            if rot[0]=='M':
                mirror=True
                rot=str(int(float(rot[2:])*10))
            else:
                rot=str(int(float(rot[1:])*10))
        layer='0' if mirror else '15'
        
        outFile.write('$MODULE '+package+'\n')
        outFile.write('Po '+x+' '+y+' '+rot+' '+layer+' 00000000 00000000 ~~\n')
        outFile.write('Li '+package+'\n')
        outFile.write('Sc 00000000\n')
        outFile.write('Op 0 0 0\n')
        #Field Desc "Name/Value"
        #              T# x y xsize ysize rot penWidth N Visible layer "txt"
        outFile.write('T0 0 0 0 0 0 0 N I 25 "'+str(info.get('name'))+'"\n')
        outFile.write('T1 0 0 0 0 0 0 N I 26 "'+str(info.get('value'))+'"\n')
        #PAD Descriptions:
        if not libInfo.get('pad')==None:
            for pad in libInfo['pad']:
                padName=pad
                pad=libInfo['pad'][pad]
                outFile.write('$PAD\n')
                if pad.get('diameter')==None:
                    diameter=str(int(int(convertCoordinate(pad['drill']))*1.5))
                else:
                    diameter=convertCoordinate(pad['diameter'])
                outFile.write('Sh "'+pad.get('name')+'" C '+diameter+' '+diameter+' 0 0 '+rot+'\n')
                drill=convertCoordinate(pad['drill'])
                outFile.write('Dr '+drill+' 0 0\n')
                outFile.write('At STD N 00A88001\n') #00A88001 should tell it to go through all layers
                if not contactRefs.get(name)==None:
                    if not contactRefs[name].get(padName)==None:
                        netname=contactRefs[name][padName]
                        netNumber=signalIds[netname]
                        outFile.write('Ne '+netNumber+' "'+netname+'"\n')
                pX=convertCoordinate(pad['x'])
                pY=convertCoordinate(-float(pad['y']))
                outFile.write('Po '+pX+' '+pY+'\n')                      
                outFile.write('$EndPAD\n')
            
        if not libInfo.get('smd')==None:
            for smd in libInfo['smd']:
                smdName=smd
                smd=libInfo['smd'][smd]
                outFile.write('$PAD\n')      
                xsize=convertCoordinate(smd['dx'])
                ysize=convertCoordinate(smd['dy'])
                outFile.write('Sh "'+smdName+'" R '+xsize+' '+ysize+' 0 0 '+rot+'\n')
                outFile.write('Dr 0 0 0\n')
                
                if mirror:
                    layerMask ='00440001'
                else:
                    layerMask = '00888000'
                outFile.write('At SMD N '+layerMask+'\n')
                if not contactRefs.get(name)==None:
                    if not contactRefs[name].get(smdName)==None:
                        netname=contactRefs[name][smdName]
                        netNumber=signalIds[netname]
                        outFile.write('Ne '+netNumber+' "'+netname+'"\n')
                pX=convertCoordinate(smd['x'])
                pY=convertCoordinate(-float(smd['y']))
                outFile.write('Po '+pX+' '+pY+'\n')  
                
                outFile.write('$EndPAD\n')
                
        outFile.write('$EndMODULE '+package+'\n\n')

def writeSEGMENTS(outFile):
    plainWires=myDict['eagle']['drawing']['board']['plain']['wire']
    edges=[]
    topSilk=[]
    bottomSilk=[]
    
    for wire in plainWires:
        layer=wire['layer']
        if layer=='20':
            edges.append(wire)
        elif layer=='21':
            topSilk.append(wire)
        elif layer=='22':
            bottomSilk.append(wire)
        
    
    for edge in edges:
        outFile.write('$DRAWSEGMENT\n')
        x1=convertCoordinate(edge['x1'])
        y1=convertCoordinate(-float(edge['y1']))
        x2=convertCoordinate(edge['x2'])
        y2=convertCoordinate(-float(edge['y2']))
        width=convertCoordinate(edge['width'])
        outFile.write('Po 0 '+x1+' '+y1+' '+x2+' '+y2+' '+width+'\n')
        outFile.write('De 28 0 900 0 0\n')
        outFile.write('$EndDRAWSEGMENT\n\n')
    
    
def writeTRACKS(outFile):
    signals=myDict['eagle']['drawing']['board']['signals']
    outFile.write('$TRACK\n')
    for sigName in signals:
        signal=signals[sigName]
        if not signal.get('wire')==None:
            
            for wire in signal['wire']:
                x1=convertCoordinate(wire['x1'])
                y1=convertCoordinate(-float(wire['y1']))
                x2=convertCoordinate(wire['x2'])
                y2=convertCoordinate(-float(wire['y2']))
                width=convertCoordinate(wire['width'])
                outFile.write('Po 0 '+x1+' '+y1+' '+x2+' '+y2+' '+width+'\n')
                layer=wire['layer']
                if layer=='16':
                    layer='0'
                elif layer=='1':
                    layer='15'
                netCode=signalIds[sigName]
                outFile.write('De '+layer+' 0 '+netCode+' 0 0\n')
                
        if not signal.get('via')==None:
            for via in signal['via']:
                x=convertCoordinate(via['x'])
                y=convertCoordinate(-float(via['y']))
                drill=convertCoordinate(via['drill'])
                outFile.write('Po 3 '+x+' '+y+' '+x+' '+y+' '+drill+'\n')
                netCode=signalIds[sigName]
                outFile.write('De 15 1 '+netCode+' 0 0\n')
                outFile.write('Po 0 '+x+' '+y+' '+x+' '+y+' '+drill+'\n')
                outFile.write('De 0 0 '+netCode+' 0 0\n')
                outFile.write('Po 0 '+x+' '+y+' '+x+' '+y+' '+drill+'\n')
                outFile.write('De 15 0 '+netCode+' 0 0\n')
                pass
            
    outFile.write('$EndTRACK\n\n')

def writeZONES(outFile):
    signals=myDict['eagle']['drawing']['board']['signals']
    outFile.write('$ZONE\n')
    for sigName in signals:
        signal=signals[sigName]
        if not signal.get('polygon')==None:            
            for polygon in signal['polygon']:
                vertexs=polygon['vertex']
                for _i in range(len(vertexs)):
                    nexti=(_i+1)%len(vertexs)
                    x1=convertCoordinate(vertexs[_i]['x'])
                    y1=convertCoordinate(-float(vertexs[_i]['y']))
                    x2=convertCoordinate(vertexs[nexti]['x'])
                    y2=convertCoordinate(-float(vertexs[nexti]['y']))
                    width=convertCoordinate(polygon['width'])
                    outFile.write('Po 0 '+x1+' '+y1+' '+x2+' '+y2+' '+width+'\n')
                    layer=polygon['layer']
                    if layer=='16':
                        layer='0'
                    elif layer=='1':
                        layer='15'
                    netCode=signalIds[sigName]                    
                    outFile.write('De '+layer+' 0 '+netCode+' 0 0\n')
    outFile.write('$EndZONE\n\n')

def writeDescriptionFor(desc,outFile,info):
    global myDict
    global signalIds
    global contactRefs
    
#    if desc=='SETUP':
#        outFile.write("$SETUP\n"+
#            "InternalUnit 1 MILIMETER\n"+
#            "Layers "+str(len(info))+'\n')
#        for layer in info:
#            outFile.write('Layer['+str(layer)+'] '+myDict['eagle']['drawing']['layers'][str(layer)]['name']+' signal\n')
#        outFile.write('$EndSETUP\n\n')
    
    if desc=='EQUIPOT':
        subDict=myDict['eagle']['drawing']['board']['signals'] 
        i=0
        for signal in subDict:
            i+=1
            name=subDict[signal].get('name')
            signalIds[name]=str(i)
            outFile.write('$EQUIPOT\n')
            outFile.write('Na '+str(i)+' '+name+'\n')
            outFile.write('St~\n')
            outFile.write('$EndEQUIPOT\n\n')
            
    elif desc=='MODULE':
        subDict=myDict['eagle']['drawing']['board']['elements']
        
        for name in subDict:
            info=subDict[name]
            package=info['package']
            library=info['library']
            libInfo=myDict['eagle']['drawing']['board']['libraries'][library]['packages'][package]
            x=convertCoordinate(info['x'])
            y=convertCoordinate(-float(info['y']))
            
            mirror=False
            if info.get('rot')==None:
                rot='0'
            else:
                rot=info['rot']
                if rot[0]=='M':
                    mirror=True
                    rot=str(int(float(rot[2:])*10))
                else:
                    rot=str(int(float(rot[1:])*10))
            
            layer='0' if mirror else '15'
            
            outFile.write('$MODULE '+package+'\n')
            outFile.write('Po '+x+' '+y+' '+rot+' '+layer+' 00000000 00000000 ~~\n')
            outFile.write('Li '+package+'\n')
            outFile.write('Sc 00000000\n')
            outFile.write('Op 0 0 0\n')
            #Field Desc "Name/Value"
            #              T# x y xsize ysize rot penWidth N Visible layer "txt"
            outFile.write('T0 0 0 0 0 0 0 N I 25 "'+str(info.get('name'))+'"\n')
            outFile.write('T1 0 0 0 0 0 0 N I 26 "'+str(info.get('value'))+'"\n')
            
            #PAD Descriptions:
            if not libInfo.get('pad')==None:
                for pad in libInfo['pad']:
                    padName=pad
                    pad=libInfo['pad'][pad]
                    outFile.write('$PAD\n')
                    if pad.get('diameter')==None:
                        diameter=str(int(int(convertCoordinate(pad['drill']))*1.5))
                    else:
                        diameter=convertCoordinate(pad['diameter'])
                    outFile.write('Sh "'+pad.get('name')+'" C '+diameter+' '+diameter+' 0 0 '+rot+'\n')
                    drill=convertCoordinate(pad['drill'])
                    outFile.write('Dr '+drill+' 0 0\n')
                    outFile.write('At STD N 00A88001\n') #00A88001 should tell it to go through all layers
                    ###HMMMM? will need to get this from will need to get a list of all contact refs
                    if not contactRefs.get(name)==None:
                        if not contactRefs[name].get(padName)==None:
                            netname=contactRefs[name][padName]
                            netNumber=signalIds[netname]
                            outFile.write('Ne '+netNumber+' "'+netname+'"\n')
                    pX=convertCoordinate(pad['x'])
                    pY=convertCoordinate(-float(pad['y']))
                    outFile.write('Po '+pX+' '+pY+'\n')                      
                    outFile.write('$EndPAD\n')
                
            if not libInfo.get('smd')==None:
                for smd in libInfo['smd']:
                    smdName=smd
                    smd=libInfo['smd'][smd]
                    outFile.write('$PAD\n')      
                    xsize=convertCoordinate(smd['dx'])
                    ysize=convertCoordinate(smd['dy'])
                    outFile.write('Sh "'+smdName+'" R '+xsize+' '+ysize+' 0 0 '+rot+'\n')
                    outFile.write('Dr 0 0 0\n')
                    outFile.write('At SMD N 00888000\n')
                    if not contactRefs.get(name)==None:
                        if not contactRefs[name].get(smdName)==None:
                            netname=contactRefs[name][smdName]
                            netNumber=signalIds[netname]
                            outFile.write('Ne '+netNumber+' "'+netname+'"\n')
                    pX=convertCoordinate(smd['x'])
                    pY=convertCoordinate(-float(smd['y']))
                    outFile.write('Po '+pX+' '+pY+'\n')  
                    
                    outFile.write('$EndPAD\n')
                    
            outFile.write('$EndMODULE '+package+'\n\n')

            
    else:
        outFile.write('$'+desc+'\n')
        outFile.write('$End'+desc+'\n\n')



def convertCoordinate(coord):
    return str(int(float(coord)/25.4*10000))

   
def start_element(name, attrs):
    global tree
    global myDict
    global polygonHolder
    global polygonIndex
    global lastPolygonHolder 
    global textHolder
    global lastTextHolder
    global textIndex
    global addTo
    
    addTo=myDict
    
    if name=='autorouter' or name=='designrules' or tree.__contains__('designrules') or tree.__contains__('autorouter'):
            tree.append(name)
            return None
    
    if len(tree)>0:     
        for unit in tree:
            addTo=addTo[unit]
    
    if name=='setting':
        for key in attrs:
            addTo[key]=attrs[key]        
    else:
        if name=='layer': 
            name=attrs['number']
            addTo[name]=attrs            
        
        elif name=='element' or name=='signal' or name=='library' or name=='class' or name=='package' or name=='attribute':
            name=attrs['name']
            addTo[name]=attrs
        
        elif name=='smd' or name=='pad':
            if addTo.get(name)==None:
                addTo[name]={}
            pname=attrs['name']
            addTo[name][pname]=attrs
        
        elif name=='contactref':
            if addTo.get('contactref')==None:
                addTo['contactref']={}
            name=attrs['element']+':'+attrs['pad']
            addTo['contactref'][name]=attrs
            
        elif name=='wire' or name=='circle' or name=='rectangle' or name=='polygon' or name=='via':
            if name=='polygon':
                polygonHolder=tree[-1]
                if not polygonHolder == lastPolygonHolder:
                    polygonIndex=-1
                    lastPolygonHolder=polygonHolder
                polygonIndex+=1
                
            if addTo.get(name)==None:
                addTo[name]=[]
            
            addTo[name].append(attrs)
        
        elif name=='vertex':
            #vertexs lie within polygon... therefore addTo will be a list of dictionaries see above
            #we must add the vertex to the correct dictionary
            if addTo[polygonIndex].get('vertex')==None: #makes sure there is a vertex list in the polygon
                addTo[polygonIndex]['vertex']=[]
            addTo[polygonIndex]['vertex'].append(attrs)

        
        elif name=='text':
            textHolder=tree[-1]
            if not textHolder == lastTextHolder:
                textIndex=-1
                lastTextHolder=textHolder
            textIndex+=1
                
            if addTo.get(name)==None:
                addTo[name]=[]            
            addTo[name].append(attrs)
        
        else:
            addTo[name]=attrs    
        
    tree.append(name)   
    
def end_element(name):
    global tree
    tree.pop()

def char_data(data):
    global tree
    global addTo
    global textIndex
    
    if tree[-1]=='text':
        if addTo['text'][textIndex].get('txtData')==None:
            addTo['text'][textIndex]['txtData']=''
        addTo['text'][textIndex]['txtData']+=data

def parse(contents):
    encoding='utf-8'
    p=ParserCreate(encoding)
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data    
    p.Parse(contents)
    
if __name__ == '__main__':
    main()

