'''
Created on Apr 2, 2012

@author: Dan
'''
import math
import LayerIds

class Converter(object):
    __slots__ = ("border","cX","cY","factor","rotFactor")
    
    def __init__(self,node=None):
        self.factor=1/(25.4)*10000
        self.rotFactor=10
        if node==None:
            self.border=None
            self.cX=0
            self.cY=0
        else:
            self.getBorder(node)
    
    def getBorder(self,node):
        """
        Gets the bounding box of the entire Board based on the board outline layer
        
        Returns:
            a dictionary containing info about the bounding box
            keys= left, right, top, bottom, cX, cY
        
        Preconditions:
            The board must have an edge Layer to get the bounds from
        """
        left=float('inf')
        right=float('-inf')
        top=float('-inf')
        bottom=float('inf')
        
        wires=node.find('drawing').find('board').find('plain').findall('wire')
        
        for wire in wires:
            if wire.get('layer')=='20':
                xs=(float(wire['x1']),float(wire['x2']))
                ys=(float(wire['y1']),float(wire['y2']))
                
                if max(xs)>right:
                    right=max(xs)
                if min(xs)<left:
                    left=min(xs)
                if max(ys)>top:
                    top=max(ys)
                if min(ys)<bottom:
                    bottom=min(ys)
        
        cX=(right-left)/2
        cY=(top-bottom)/2
        
        cX,cY=self.convertCoordinate(cX,cY,True)
        
        self.cX=cX
        self.cY=cY
        
    def convertUnit(self,unit): 
        """
        Converts between Eagle mm and Kicad deciMils
        Param:
            units: the unit in mm
        Returns:
            string the unit in deciMils or none
        """
        return int(float(unit)*self.factor)
    
    def convertCoordinate(self,x,y,noTranspose=False,noInvert=False):
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
        

        xTranspose=0 if noTranspose else 58500-self.cX
        yTranspose=0 if noTranspose else 41355-self.cY
            
        invertFactor= 1 if noInvert else -1
        
        if not x==None: 
            x=xTranspose+int(float(x)*self.factor)
        if not y==None:
            y=yTranspose+int(invertFactor*float(y)*self.factor)
        return x,y

    def convertRotation(self,rotString):
        """
        Returns Eagle rotation strings to kicad rotations
    
        Params:
            rot: the eagle rotation string
    
        Returns:
            a kicad formatted dict with keys:
                rot,mirror,spin
     
        """

        mirror=False
        spin=False
        
        if rotString==None:
            rot=0
        else:
            if rotString[0]=='M':
                mirror=True
                rot=int(float(rotString[2:])*10)
            elif rotString[0]=='S':
                spin=True
                rot=int(float(rotString[2:])*10)
            else:
                rot=int(float(rotString[1:])*10)
        return {'rot':rot,'mirror':mirror,'spin':spin}
    
class Module(object):
    '''
    Represents a module aka footprint
    '''
    __slots__=("converter","x","y","rotation","mirror","layer","name",
               "description","keywords","reference","value","drawings","pads","texts")
    
    def __str__(self):
        return "Module: "+str(self.name)
    
    def write(self,outFile):
        outFile.write("$MODULE "+self.name+"\n")
        outFile.write("Po "+str(self.x)+" "+str(self.y) +" "+str(self.rotation)+" "+str(self.layer)+"00000000 00000000 ~~\n")
        outFile.write("Li "+self.name+"\n")
        if self.description != "":
            outFile.write("Cd "+self.description+"\n")        
        if not self.keywords == "":
            outFile.write("Kw "+self.keywords+"\n")
            
        outFile.write("Sc 00000000\n")
        outFile.write("Op 0 0 0\n")
        
        #Field Descriptions
        outFile.write(self.reference)
        outFile.write(self.value)
        goto=min((10,len(self.texts)))#only 12 fields
        for _i in range(goto):            
            outFile.write(self.texts[_i].moduleRep(_i+2)) 
        
        #drawings
        for elem in self.drawings:
            outFile.write(elem.moduleRep())
            
#        #Pads
        for pad in self.pads:
            outFile.write(pad.moduleRep())
        
        
        outFile.write("$EndMODULE "+self.name+"\n")
           
    def getParts(self,node):
        #(polygon | wire | text | circle | rectangle | frame | hole | pad | smd)
        
        self.drawings=[]
        polygons=node.findall("polygon")
        lines=node.findall("wire")        
        circles=node.findall("circle")
        rects=node.findall("rectangle")
        
        
        if lines != None:
            for line in lines:
                line=Line(line,self.converter,True)
                self.drawings.append(line)
        if polygons != None:
            for polygon in polygons:
                polygon=Polyline(polygon,self.converter,True)
                self.drawings.append(polygon)
        if circles != None:
            for circ in circles:
                circ=Circle(circ,self.converter,True)
                self.drawings.append(circ)

#        if rects != None:
#            for rect in rects:
#                rect=Rectangle(rect)
#                self.drawings.append(rect)            
#        
        self.texts=[]
        texts=node.findall("text")
        if texts != None:
            for text in texts:
                text=Text(text,self.converter,True)                
                if text.val==">NAME":
                    self.reference=text.moduleRep(0)
                elif text.val==">VALUE":
                    self.value=text.moduleRep(1)
                else:
                    self.texts.append(text) 
                            
        self.pads=[]
        holes=node.findall("hole")
        pads=node.findall("pad")
        smds=node.findall("smd")
        
#        for hole in holes:
#                hole=Pad(hole,self.converter,True)
#                self.pads.append(hole) 
        for pad in pads:
                pad=Pad(pad,self.converter,True)
                self.pads.append(pad) 
        for smd in smds:
                smd=Pad(smd,self.converter,True)
                self.pads.append(smd) 
    
class LibModule(Module):
    """
    A module created from a lbr file
    """
    def __init__(self,node,converter):
        '''
        Constructor
        '''
        self.converter=converter
        self.x=0
        self.y=0
        self.rotation=0
        self.mirror=False
        self.layer=15        
        self.name=node.get("name")
        
        description=node.find("description")
        if description != None:
            self.description=str(description.text)
        else:
            self.description=""
        
        self.keywords=""
        self.reference="T0 0 0 0 0 0 0 N I 25 \"U\"\n"

        self.value="T1 0 0 0 0 0 0 N I 26 \"val**\"\n"
        self.drawings=[]
        self.pads=[]
        self.getParts(node)

class BrdModule(Module):
    pass  
#    """
#    a module created from a .brd file
#    """  
#    def __init__(self,node):
#        self.x,self.y=convertCoordinate(mod['x'],mod['y'])
#        self.rotation = getRotationInfo(node.get('rot'))
#        self.layer='0' if rotation['mirror'] else '15'
#        libraryName=node.get('library')

class Line(object):
    __slots__=('x1','y1','x2','y2','width','layer','curve')
    
    def __init__(self,node,converter,noTranspose=False):
        self.getWireInfo(node,converter,noTranspose)
        
        
    def getWireInfo(self,wire,converter,noTranspose=False):
        """
        Converts a wire dictionary node from Eagle to a usable form for kicad
        It then returns the dictionary of the wires info
        
        Params:
            wire:    the wire's node from myDict
            noTranspose: if true, coordinates will not be transposed
                            to screens center
        Returns:
            dict:    the wires info in a kicad usable dictionary form
                    Keys = x1,x2,y1,y2,layer,curve,width
            
        """
        x1,y1=converter.convertCoordinate(wire.get('x1'),wire.get('y1'),noTranspose)
        x2,y2=converter.convertCoordinate(wire.get('x2'),wire.get('y2'),noTranspose)
        width=converter.convertUnit(wire.get('width'))
        layer=LayerIds.getLayerId(wire.get('layer'))
        curve=wire.get('curve')
        if not curve==None:
            x1,y1,x2,y2,curve=self.getWireArcInfo(wire,converter,noTranspose)
                
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.width=width
        self.layer=layer
        self.curve=curve


    def getWireArcInfo(self,arc,converter,noTranspose=False,noInvert=False):
        """
        Converts between Eagle's arc definitions, and kicads arc definitions
        Eagle holds the two endpoints and the degrees of the sweep ccw betweeen them
        
        Kicad holds the center point, and an enpoint, and a degree sweep CW from 
        the endpoint
        
        This was the hardest part to get working
        
        Params:
            arc: the node of the arc from myDict
            noTranspose:    If true the coordinates will not be transposed
            noInvert:       If True the coordinates will not be inverted
        
        Returns:
            cX: the center x coord
            cY: the center y coord
            x1: the endpt x coord
            y1: the endpt y coord
            curve: the angle to sweep in 1/10 degrees
        """
        
        curve=float(arc.get('curve'))
        x1,y1=arc.get('x1'),arc.get('y1')
        x2,y2=arc.get('x2'),arc.get('y2')
        
        #radius of arc
        x1=float(x1)
        x2=float(x2)
        y1=float(y1)
        y2=float(y2)
        l=math.sqrt((x1-x2)**2+(y1-y2)**2)
        r=l/(2*math.sin(math.radians(curve/2.0)))
            
        ##go to midpoint of chord move perpendicular by arc height
        h=math.sqrt(r**2-(l/2)**2)    
        #slope of chord
        dY=(y2-y1)
        dX=(x2-x1)
        mX=(x2+x1)/2
        mY=(y2+y1)/2
        chordangle=math.atan2(dY,dX)
        if chordangle<0:
            chordangle+=math.radians(360)    
        angleSign=curve/math.fabs(curve)    
        angle=chordangle-math.radians(90)*angleSign   
        xChange=h*math.cos(angle)
        yChange=h*math.sin(angle)
        if math.fabs(curve)<180:
            xChange=-xChange
            yChange=-yChange    
        cX=mX+xChange
        cY=mY+yChange
        x1,y1=converter.convertCoordinate(x1,y1,noTranspose,noInvert)
        cX,cY=converter.convertCoordinate(cX,cY,noTranspose,noInvert)
        curve=str(-int(curve*10))
        return cX,cY,x1,y1,curve
     
    def moduleRep(self):
        stype="DS " if self.curve==None else "DA "
        curve=" " if self.curve==None else " "+str(self.curve)+" "
        
        myString=stype+str(self.x1)+" "+str(self.y1)+" "+str(self.x2)+" "+str(self.y2)
        myString+=curve+str(self.width)+" "+str(self.layer)+"\n"
        
        return myString

class Polyline(object):
    __slots__=("lines")
    
    def __init__(self, node, converter, noTranspose=False):
        vertexs=node.findall('vertex')
        width=node.get('width')
        layer=LayerIds.getLayerId(node.get('layer'))
        self.lines=[]
        
        for _i in range(len(vertexs)):
            nexti=(_i+1)%len(vertexs)
            x1=vertexs[_i].get('x')
            y1=vertexs[_i].get('y')
            x2=vertexs[nexti].get('x')
            y2=vertexs[nexti].get('y')
            curve=vertexs[_i].get('curve')
            wire={'x1':x1,'y1':y1,'x2':x2,'y2':y2,'curve':curve,'width':width,'layer':layer}
            line=Line(wire,converter,noTranspose)
            self.lines.append(line)
            
    def moduleRep(self):
        myString="";
        for line in self.lines:
            myString+=line.moduleRep()
        return myString

class Circle(object):
    __slots__=('cX','cY','pX','pY','layer','width')
    def __init__(self,node,converter,noTranspose=False):
        radius=converter.convertUnit(node.get('radius'))
        cX,cY=converter.convertCoordinate(node.get('x'),node.get('y'),noTranspose)
        width=converter.convertUnit(node.get('width'))
        layer=LayerIds.getLayerId((node.get('layer')))
        pX=int(cX)+int(radius)
        pY=cY        
        self.cX=str(cX)
        self.cY=str(cY)
        self.pX=str(pX)
        self.pY=str(pY)
        self.layer=layer
        self.width=str(width)
        
    def moduleRep(self):
        myString="DC "+self.cX+" "+self.cY+" "+self.pX+" "+self.pY+" "+self.width+" "+self.layer+"\n"
        return myString
    
class Text(object):
    __slots__=("val","x","y","width","size","rot","mirror","justification","layer","style")
    
    def __init__(self,node,converter,noTranspose=False):    
        
        self.val=node.text
        self.style='Normal'
        
        x,y=converter.convertCoordinate(node.get('x'),node.get('y'),noTranspose)
        size=converter.convertUnit(node.get('size'))
        
        wMod=node.get('ratio')
        if wMod==None:
            wMod=8
        else:
            wMod=int(wMod)
        width=size*wMod//100
    
        
        rot=node.get('rot')
        if rot==None:
            rot=0
            mirror=1
            spin=False
        else:
            rot=converter.convertRotation(rot)
            mirror=0 if rot['mirror'] else 1
            spin=rot['spin']
            rot=rot['rot']
        
        rot=(rot+3600)%3600
    
        if not (rot==0 or rot==900 or rot==1800 or rot==2700 or rot==3600):
            print("Warning Text must be rotated increments of 90 degrees")
            print("\tText: "+self.val+"\tRotation: "+str(rot))
         
        layer=LayerIds.getLayerId(node.get('layer'))
        
        if spin:
            justification='L'
        
        elif rot<=900 or rot>2700:
            justification='L'
            
        else:
            justification='R'
            rot=rot-1800
        
        offset=size//2
        sign=1
        
        if justification=='R':
            sign=-1
        #TODO only if we have to force it on the center    
        if (rot+3600)%3600==0:
            y=y-offset*sign
            x=x+offset*sign*len(self.val)
        elif(rot+3600)%3600==900:
            x=x-offset*sign
            y=y+offset*sign*len(self.val)
        elif(rot+3600)%3600==1800:
            y=y+offset*sign
            x=x-offset*sign*len(self.val)
        elif(rot+3600)%3600==2700:
            x=x+offset*sign
            y=y-offset*sign*len(self.val)
            
        rot=str(rot)
        
        self.x=str(x)
        self.y=str(y)
        self.size=str(size)
        self.width=str(width)
        self.rot=str(rot)
        self.mirror=mirror
        self.justification=justification
        self.layer=str(layer)
                
    def moduleRep(self,num):
    #T<field number> <Xpos> <Ypos> <Xsize> <Ysize> <rotation> <penWidth> N <visible> <layer> "text"
        myString="T"+str(num)+" "+self.x+" "+self.y+" "+self.size+" "+self.size+" "+self.rot+" "+self.width+" N V "+self.layer+" \""+self.val+"\"\n"
        return myString
    
class Pad(object):
    __slots__=("name","drill","xSize","ySize","x","y","net","kind","shape","layerMask","rot")
    
    def __init__(self,node,converter,noTranspose=False):
        self.x=0
        self.y=0
        self.getPadInfo(node,converter)
    
    def getPadInfo(self,node,converter,modName="",modRot=0,mirror=False):
        """
        Gets info for a given pad
        
        Params:
            pad: the pad's dictionary node from myDict
            modName: the name of the module
            modRot: the rotation of the module in 10th of a degree
            mirror, whether the module is mirrored or not         
        """
        
        rot=modRot
        
        pName=node.get('name')
        
        shapeType=node.tag
        
        pX,pY=converter.convertCoordinate(node.get('x'),node.get('y'),True)   
        
        net=None
        #TODO net connections
#        if not contactRefs.get(modName)==None:
#            if not contactRefs[modName].get(name)==None:
#                netName=contactRefs[modName][name]
#                netNumber=signalIds[netName]
#                net={'name':netName,'num':netNumber}
        
        if shapeType=='pad':
            pass
            drill=converter.convertUnit(node.get('drill'))
            if node.get('diameter')==None:
                diameter=str(int(int(drill)*1.5))#TODO find default diameter for vias
            else:
                diameter=converter.convertUnit(node.get('diameter'))
            xSize=diameter
            ySize=diameter
            kind='STD'
            layerMask='00C0FFFF'#00C0FFFF should tell it to go through all layers
            shape='O'
        
        elif shapeType=='smd':#TODO roundness
            drill=0
            xSize=converter.convertUnit(node.get('dx'))
            ySize=converter.convertUnit(node.get('dy'))
            if not node.get('rot')==None:
                pRot=converter.convertRotation(node.get('rot'))['rot']
                rot=int(pRot)+int(modRot)
            kind='SMD'
            layerMask ='00440001' if mirror else '00888000'
            shape='R'
            
#        elif shapeType=="hole":
#            TODO HOLES as PADspass

        else:
            drill=0
            diameter=0
            xSize=0
            ySize=0
            kind='0'
            layerMask='0'
            shape='0'
                    
        self.name=pName
        self.drill=str(drill)
        self.xSize=str(xSize)
        self.ySize=str(ySize)
        self.x=str(pX)
        self.y=str(pY)
        self.net=net
        self.kind=kind
        self.shape=shape
        self.layerMask=layerMask
        self.rot=str(rot)                   
        
    def moduleRep(self):
        if self.x==0 and self.y==0:
            return""
        myString='$PAD\n'
        myString+='Sh "'+self.name+'" '+self.shape+' '+self.xSize+' '+self.ySize+' 0 0 '+self.rot+'\n'
        myString+='Dr '+self.drill+' 0 0\n'
        myString+='At '+self.kind+' N '+self.layerMask+'\n'
        if not self.net==None:
            myString+='Ne '+self.net['num']+' "'+self.net['name']+'"\n'
        myString+='Po '+self.x+' '+self.y+'\n'                   
        myString+='$EndPAD\n'
        return myString
        
        
        
        
        
    
    