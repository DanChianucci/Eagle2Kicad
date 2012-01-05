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


def getLayerIds():
        return{'1':'15',
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

layerIds=getLayerIds()

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
    writeGRAPHICS(out)
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


def getWireInfo(wire):
        x1=convertCoordinate(wire.get('x1'))
        if x1==None:
            print('x1=none')
            return None
        y1=convertCoordinate(-float(wire.get('y1')))
        if y1==None:
            print('y1=none')
            return None
        x2=convertCoordinate(wire.get('x2'))
        if x2==None:
            print('x2=none')
            return None
        y2=convertCoordinate(-float(wire.get('y2')))
        if y2==None:
            print('y2=none')
            return None
        width=convertCoordinate(wire.get('width'))
        if width==None:
            print('width=none')
            return None
        layer=layerIds.get(wire.get('layer'))
        if layer==None:
            print('layer=none')
            return None
        curve=wire.get('curve')
        if not curve==None:
            curve=str(int(float(curve)*10))     
        return {'x1':x1,'y1':y1,'x2':x2,'y2':y2,'width':width,'layer':layer,'curve':curve}
    
def getTextInfo(text):
    global layerIds
    
    txtData=text['txtData']
    x=convertCoordinate(text['x'])
    y=convertCoordinate(-float(text['y']))
    xSize=convertCoordinate(float(text['size']))#5/7.0)
    ySize=convertCoordinate(text['size'])
    
    wMod=text.get('ratio')
    if wMod==None:
        wMod='8'
    width=str(int(ySize)*int(wMod)//100)

    
    rot=text.get('rot')
    if rot==None:
        rot='0'
        mirror='1'
        spin=False
    else:
        rot=getRotationInfo(rot)
        mirror='0' if rot['mirror'] else '1'
        spin=rot['spin']
        rot=rot['rot']

    if not (rot=='0' or rot=='900' or rot=='1800' or rot=='2700' or rot=='3600'):
        return None
     
    layer=layerIds[text['layer']]
    style='Normal'
    
    if spin:
        justification='L'
    
    elif int(rot)<=900 or int(rot)>2700:
        justification='L'
        
    else:
        justification='R'
        rot=str(int(rot)-1800)
    
    rot=int(rot)
    offset=int(ySize)//2
    sign=1
    if justification=='R':
        sign=-1
    if (rot+3600)%3600==0:
        y=str(int(y)-offset*sign)
    elif(rot+3600)%3600==900:
        x=str(int(x)-offset*sign)
    elif(rot+3600)%3600==1800:
        y=str(int(y)+offset*sign)
    elif(rot+3600)%3600==2700:
        x=str(int(x)+offset*sign)
        
    rot=str(rot)
    return {'text':txtData,'x':x,'y':y,'xSize':xSize,'ySize':ySize,'width':width,'rot':rot,'mirror':mirror,'just':justification,'layer':layer,'style':style}
  
def getRectInfo(rect):
    pass

def getCircInfo(circ):
    pass

def getViaInfo(via):
        x=convertCoordinate(via.get('x'))
        if x==None:
            return None
        y=convertCoordinate(-float(via.get('y')))
        if y==None:
            return None
        drill=convertCoordinate(via.get('drill'))
        if drill==None:
            return None
        return {'x':x,'y':y,'drill':drill}
        
def getPolyInfo(poly):
    pass

def getRotationInfo(rot):
    mirror=False
    spin=False
    if rot==None:
        rot='0'
    else:
        if rot[0]=='M':
            mirror=True
            rot=str(int(float(rot[2:])*10))
        elif rot[0]=='S':
            spin=True
            rot=str(int(float(rot[2:])*10))
        else:
            rot=str(int(float(rot[1:])*10))
    
    return {'rot':rot,'mirror':mirror,'spin':spin}

def getModInfo(mod):
    
    x=convertCoordinate(mod['x'])
    y=convertCoordinate(-float(mod['y']))
    rotation = getRotationInfo(mod.get('rot'))
    layer='0' if rotation['mirror'] else '15'
    package=mod.get('package')
    lib=mod.get('library')
    name=str(mod.get('name'))
    value=str(mod.get('value'))
    return {'x':x,'y':y,'rot':rotation['rot'],'mirror':rotation['mirror'],'layer':layer,'package':package,'lib':lib,'name':name,'value':value}

def getPadInfo(pad,modName,modRot,mirror):
    rot=modRot
    name=pad.get('name')
    shapeType='smd' if pad.get('drill')==None else 'pad'
    pX=convertCoordinate(pad['x'])
    pY=convertCoordinate(-float(pad['y']))    
    net=None
    if not contactRefs.get(modName)==None:
        if not contactRefs[modName].get(name)==None:
            netName=contactRefs[modName][name]
            netNumber=signalIds[netName]
            net={'name':netName,'num':netNumber}
    
    if shapeType=='pad':
        drill=convertCoordinate(pad['drill'])
        if pad.get('diameter')==None:
            diameter=str(int(int(drill)*1.5))
        else:
            diameter=convertCoordinate(pad['diameter'])
        xSize=diameter
        ySize=diameter
        kind='STD'
        layerMask='00A88001'#00A88001 should tell it to go through all layers
        shape='C'
    
    elif shapeType=='smd':
        drill='0'
        xSize=convertCoordinate(pad['dx'])
        ySize=convertCoordinate(pad['dy'])
        if not pad.get('rot')==None:
            pRot=getRotationInfo(pad['rot'])['rot']
            rot=str(int(pRot)+int(modRot))
        kind='SMD'
        layerMask ='00440001' if mirror else '00888000'
        shape='R'
            
    return {'name':name,'drill':drill,'xSize':xSize, 'ySize':ySize,'x':pX,'y':pY,'net':net,'kind':kind,'shape':shape,'layerMask':layerMask,'rot':rot}                     

    

def writeMODULES(outFile):
    global myDict
    global signalIds
    global contactRefs
    
    subDict=myDict['eagle']['drawing']['board']['elements']
    for name in subDict:
        info=subDict[name]
        mod=getModInfo(info)
        libInfo=myDict['eagle']['drawing']['board']['libraries'][mod['lib']]['packages'][mod['package']]
        
        outFile.write('$MODULE '+mod['package']+'\n')
        outFile.write('Po '+mod['x']+' '+mod['y']+' '+mod['rot']+' '+mod['layer']+' 00000000 00000000 ~~\n')
        outFile.write('Li '+mod['package']+'\n')
        outFile.write('Sc 00000000\n')
        outFile.write('Op 0 0 0\n')
        
        #Field Desc "Name/Value"
        #              T# x y xsize ysize rot penWidth N Visible layer "txt"
        outFile.write('T0 0 0 0 0 0 0 N I 25 "'+mod['name']+'"\n')
        outFile.write('T1 0 0 0 0 0 0 N I 26 "'+mod['value']+'"\n')
        
        #Drawing
        if not libInfo.get('wire')==None:
            for wire in libInfo['wire']:
                w=getWireInfo(wire)

                if not w==None:
                    wtype='DS ' if w['curve']==None else 'DA '
                    curve=' ' if w['curve']==None else (' '+w['curve']+' ')
                    outFile.write(wtype+w['x1']+' '+w['y1']+' '+w['x2']+' '+w['y2']+curve+w['width']+' '+w['layer']+'\n')
        
        #PAD Descriptions:
        mirror=mod['mirror']
        allConnects=[]
        if not libInfo.get('pad')==None:
            for pad in libInfo['pad']:
                allConnects.append(libInfo['pad'][pad])            
        
        if not libInfo.get('smd')==None:
            for smd in libInfo['smd']:
                allConnects.append(libInfo['smd'][smd])
        
        for pad in allConnects:
            #pad=allConnects[pad]
            p=getPadInfo(pad,name,mod['rot'],mirror)
            outFile.write('$PAD\n')
            outFile.write('Sh "'+p['name']+'" '+p['shape']+' '+p['xSize']+' '+p['ySize']+' 0 0 '+p['rot']+'\n')
            outFile.write('Dr '+p['drill']+' 0 0\n')
            outFile.write('At '+p['kind']+' N '+p['layerMask']+'\n') 
            if not p.get('net')==None:
                outFile.write('Ne '+p['net']['num']+' "'+p['net']['name']+'"\n')
            outFile.write('Po '+p['x']+' '+p['y']+'\n')                      
            outFile.write('$EndPAD\n')
                
        outFile.write('$EndMODULE '+mod['package']+'\n\n')

def writeGRAPHICS(outFile):
    plainWires=myDict['eagle']['drawing']['board']['plain']['wire']
    plainText=myDict['eagle']['drawing']['board']['plain']['text']
#    plainCircles=myDict['eagle']['drawing']['board']['plain']['circle']
#    plainRects=myDict['eagle']['drawing']['board']['plain']['rectangle']
#    plainPolys=myDict['eagle']['drawing']['board']['plain']['polygon']
    
    for line in plainWires:        
        info=getWireInfo(line)
        if not info == None:
            outFile.write('$DRAWSEGMENT\n')         
            outFile.write('Po 0 '+info['x1']+' '+info['y1']+' '+info['x2']+' '+info['y2']+' '+info['width']+'\n')
            outFile.write('De '+info['layer']+' 0 900 0 0\n')
            outFile.write('$EndDRAWSEGMENT\n\n')
    
    for text in plainText:
        info=getTextInfo(text)
        if not info==None:
            outFile.write('$TEXTPCB\n')         
            outFile.write('Te "'+info['text']+'"\n')
            outFile.write('Po '+info['x']+' '+info['y']+' '+info['xSize']+' '+info['ySize']+' '+info['width']+' '+info['rot']+'\n')
            outFile.write('De '+info['layer']+' '+info['mirror']+' 0000 '+info['style']+' '+info['just']+'\n')
            outFile.write('$EndTEXTPCB\n\n')

def writeTRACKS(outFile):
    signals=myDict['eagle']['drawing']['board']['signals']
    outFile.write('$TRACK\n')
    
    for sigName in signals:
        signal=signals[sigName]
        if not signal.get('wire')==None:            
            for wire in signal['wire']:
                w = getWireInfo(wire)
                netCode=signalIds[sigName]
                if not w == None:
                    outFile.write('Po 0 '+w['x1']+' '+w['y1']+' '+w['x2']+' '+w['y2']+' '+w['width']+'\n')                
                    outFile.write('De '+w['layer']+' 0 '+netCode+' 0 0\n')
                
        if not signal.get('via')==None:
            for via in signal['via']:
                v=getViaInfo(via)
                netCode=signalIds[sigName]
                if not v==None:
                    outFile.write('Po 3 '+v['x']+' '+v['y']+' '+v['x']+' '+v['y']+' '+v['drill']+'\n')                    
                    outFile.write('De 15 1 '+netCode+' 0 0\n')
            
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
                    netCode=signalIds[sigName]   
                    layer=layerIds.get(polygon['layer'])
                    if not layer == None:
                        outFile.write('Po 0 '+x1+' '+y1+' '+x2+' '+y2+' '+width+'\n')                 
                        outFile.write('De '+layer+' 0 '+netCode+' 0 0\n')
                        
    outFile.write('$EndZONE\n\n')
    

def convertCoordinate(coord):
    if coord==None:
        return None
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

