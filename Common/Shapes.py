'''
Created on Apr 3, 2012

@author: Dan
'''
from math import sin,sqrt,atan2,cos,radians,fabs,degrees
from LayerIds import getLayerId, makeViaMask

class Line(object):
    __slots__=('x1','y1','x2','y2',"cX","cY",'width','layer','curve','radius','sAngle','eAngle')
    
    def __init__(self,node,converter,noTranspose=False, offset=None):
        self.getWireInfo(node,converter,noTranspose, offset)
        
    def getWireInfo(self,wire,converter,noTranspose, offset):
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
        curve=wire.get('curve')
        
        width=converter.convertUnit(wire.get('width'))
        layer=getLayerId(wire.get('layer'))
        
        
        if curve==None:
            cX=(x1+x2)//2
            cY=(y1+y2)//2
            radius = 0
            sAngle = 0
            eAngle = 0
        else:
            cX,cY,curve,radius,sAngle,eAngle=self.getWireArcInfo(wire,converter,noTranspose)
        
        if offset != None:
            dX, dY = converter.convertCoordinate(offset[0], offset[1], noTranspose)
            x1 += dX
            y1 += dY
            x2 += dX
            y2 += dY
            cX += dX
            cY += dY
            
        self.x1=        str(x1)
        self.y1=        str(y1)
        self.x2=        str(x2)
        self.y2=        str(y2)
        self.cX=        str(cX)
        self.cY=        str(cY)
        self.width=     str(width)
        self.layer=     str(layer)
        self.curve=     str(curve)
        self.radius=    str(radius)
        self.sAngle=    str(sAngle)
        self.eAngle=    str(eAngle)

    def getWireArcInfo(self,arc,converter, noTranspose=False,noInvert=False):
        """
        Converts between Eagle's arc definitions, and kicads arc definitions
        Eagle holds the two endpoints and the degrees of the sweep ccw betweeen them
        
        Kicad holds the center point, and an enpoint, and a degree sweep CW from 
        the endpoint

        Params:
            arc:             the node of the arc from myDict
            noTranspose:    If true the coordinates will not be transposed
            noInvert:       If True the coordinates will not be inverted
        
        Returns:
            cX: the center x coord
            cY: the center y coord
            x1: the endpt x coord
            y1: the endpt y coord
            curve: the angle to sweep in 1/10 degrees
            radius: the radius of the arc
        """
        
        curve=float(arc.get('curve'))
        x1,y1= float(arc.get('x1')) , float(arc.get('y1'))
        x2,y2= float(arc.get('x2')) , float(arc.get('y2'))
            
        #length of the chord
        l=sqrt((x1-x2)**2+(y1-y2)**2)
        
        #radius = l / ( 2*sin(curve/2) )
        r = fabs(l/( 2*sin(radians(curve/2.0))))
        
        #find midpoint of chord and then move perpendicularly to the center
           
        #go to midpoint of chord
        mX=(x2+x1)/2
        mY=(y2+y1)/2
        
        #distance between center and chord
        h=sqrt(r**2-(l/2)**2)  
          
        #slope of chord
        dY=(y2-y1)
        dX=(x2-x1)
        
        chordangle=atan2(dY,dX)
        
        #normalise the chord angle
        if chordangle<0:
            chordangle+=radians(360)
        
        #the angle perpendicular to the chord  
        angleSign=curve/fabs(curve)    
        angle=chordangle-radians(90)*angleSign 
          
        xChange=h*cos(angle)
        yChange=h*sin(angle)
        
        if fabs(curve)<180:
            xChange=-xChange
            yChange=-yChange
               
        cX=mX+xChange
        cY=mY+yChange

        if curve<0:
            sAngle=degrees(atan2(y2-cY,x2-cX))
        else:
            sAngle=degrees(atan2(y1-cY,x1-cX))
        eAngle=sAngle+curve
        
        cX,cY  = converter.convertCoordinate(cX,cY,noTranspose,noInvert)
        curve  = int(curve*10)
        r      = converter.convertUnit(r)
        sAngle = int(sAngle*10)%3600
        eAngle = int(eAngle*10)
        
        return cX,cY,curve,r,sAngle,eAngle

    def moduleRep(self):
        myString=""        
        if self.curve=="None":
            myString+="DS "+self.x1+" "+self.y1+" "+self.x2+" "+self.y2+" "+self.width+" "+self.layer+"\n"
        else:     
            myString+="DA "+self.cX+" "+self.cY+" "+self.x1+" "+self.y1+" "+self.curve+" "+self.width+" "+self.layer+"\n"
        return myString

    def boardRep(self):
        myString=""
        if self.curve=="None":
            myString+="$DRAWSEGMENT\n"
            myString+="Po 0 "+self.x1+" "+self.y1+" "+self.x2+" "+self.y2+" "+self.width+"\n"
            myString+="De "+self.layer+" 0 900 0 0\n"
            myString+="$EndDRAWSEGMENT\n"
        else:      
            myString="$DRAWSEGMENT\n"
            myString+="Po 2 "+self.cX+" "+self.cY+" "+self.x1+" "+self.y1+" "+self.width+"\n"
            myString+="De "+self.layer+" 0 "+self.curve+" 0 0\n"
            myString+="$EndDRAWSEGMENT\n"
        return myString
    
    def symRep(self):
        if self.curve == "None":
            myString="P 2 0 0 "+self.width+" "+self.x1+" "+self.y1+" "+self.x2+" "+self.y2+" N\n"
            return myString
        else:
            myString="A "+self.cX+" "+self.cY+" "+self.radius+" "+self.sAngle+" "+\
                self.eAngle+" 0 0 "+self.width+" N "+self.x1+" "+self.y1+" "+self.x2+\
                " "+self.y2+"\n"
            return myString       
    
class Track(Line):
    __slots__=("netCode")
    def __init__(self,node,converter,netCode='0',noTranspose=False):
        Line.__init__(self,node,converter,noTranspose)
        self.netCode=netCode
        if netCode=='0':
            print("Warning: track with netCode 0")
    
    def boardRep(self):
        myString= "Po 0 "+self.x1+" "+self.y1+" "+self.x2+" "+self.y2+" "+self.width+"\n"
        myString+="De "+self.layer+" 0 "+self.netCode+" 0 0\n"
        return myString

class Via(object):
    __slots__=("x","y","drill","diameter","extent","shape","netCode")
    
    def __init__(self,node,converter,netCode='0',noTranspose=False):
        x,y=node.get("x"),node.get("y")
        x,y=converter.convertCoordinate(x,y,noTranspose)
        drill=converter.convertUnit(node.get("drill"))
        extent=node.get("extent")
        
        diameter=node.get("diameter") #unused
        shape=node.get("shape")       #unused
        
        self.x=str(x)
        self.y=str(y)
        self.drill=str(drill)
        self.diameter=str(diameter)
        self.extent=makeViaMask(extent)
        self.shape=str(shape)
        self.netCode=str(netCode)
        
        if netCode=='0':
            print("Warning: via with netCode 0")
        if self.extent!='F0' and self.extent!='0F':
            print("Warning: blind or buried via")
    
    def boardRep(self):
        #TODO use drill or diameter for via width?
        #TODO figure out via extent
        #TODO via shape :  through=3 blind=2 buried=1
        shape='3'
        myString= "Po "+shape+" "+self.x+" "+self.y+" "+self.x+" "+self.y+" "+self.drill+"\n"
        myString+="De 15 1 "+self.netCode+" 0 0\n"

        return myString

class Zone(object):
    
    def __init__(self,node,converter,node_name,netCode='0',noTranspose=False):
        self.vertexs = node.findall('vertex')
        self.width = converter.convertUnit(node.get('width'))
        self.layer = getLayerId(node.get('layer'))
        
        isolate=node.get('isolate')
        if isolate is not None:
            self.isolate = converter.convertUnit(isolate)
        else:
            self.isolate=0
            
        self.corners = len(self.vertexs)
        self.cornerstr = ""
        self.name = node_name
        
        for _i in range(len(self.vertexs)):
            x=self.vertexs[_i].get('x')
            y=self.vertexs[_i].get('y')
            x,y=converter.convertCoordinate(x,y,noTranspose)
            string = "ZCorner " + str(x) + " " + str(y);
            if _i == self.corners-1:
                string += " 1\n"
            else:
                string += " 0\n"
            self.cornerstr+=string
        self.netCode=netCode
        if netCode=='0':
            print("Warning: track with netCode 0")
    
    def boardRep(self):
        myString= "$CZONE_OUTLINE\n"
        myString+="ZInfo 0 " + str(self.netCode) + ' "' + str(self.name) + '"\n' 
        myString+="ZLayer " + str(self.layer) + "\n"
        myString+="ZAux " + str(self.corners) + " E\n"
        myString+="ZClearance " + str(self.isolate) + " T\n"
        myString+="ZMinThickness " + str(self.width) + "\n"
        myString+=self.cornerstr
        myString+="$endCZONE_OUTLINE\n"
        return myString
    
class Polyline(object):
    __slots__=("lines")
    
    def __init__(self, node, converter, noTranspose=False, offset=None):
        #DON't convert any units they will get converted in the Line()
        vertexs=node.findall('vertex')
        width=node.get('width')
        layer=node.get('layer')
        self.lines=[]
        
        for _i in range(len(vertexs)):
            nexti=(_i+1)%len(vertexs)
            x1=vertexs[_i].get('x')
            y1=vertexs[_i].get('y')
            x2=vertexs[nexti].get('x')
            y2=vertexs[nexti].get('y')
            curve=vertexs[_i].get('curve')
            wire={'x1':x1,'y1':y1,'x2':x2,'y2':y2,'curve':curve,'width':width,'layer':layer}
            line=Line(wire, converter, noTranspose, offset)
            self.lines.append(line)
            
    def moduleRep(self):
        myString="";
        for line in self.lines:
            myString+=line.moduleRep()
        return myString

    def symRep(self):
        myString="";
        for line in self.lines:
            myString+=line.symRep()
        return myString
    
    def boardRep(self):
        myString=""
        for line in self.lines:
            myString+=line.boardRep()
        return myString
        
class Circle(object):
    __slots__=('cX','cY','pX','pY','layer','width',"radius")
    def __init__(self,node,converter,noTranspose=False, offset=None):
        radius=converter.convertUnit(node.get('radius'))
        cX,cY=converter.convertCoordinate(node.get('x'),node.get('y'),noTranspose)
        
        if offset != None:
            dX, dY = converter.convertCoordinate(offset[0], offset[1], noTranspose)
            cX += dX
            cY += dY

        
        width=converter.convertUnit(node.get('width'))
        layer=getLayerId((node.get('layer')))
        pX=int(cX)+int(radius)
        pY=cY
        self.cX=str(cX)
        self.cY=str(cY)
        self.pX=str(pX)
        self.pY=str(pY)
        self.layer=layer
        self.width=str(width)
        self.radius=str(radius)
        
    def moduleRep(self):
        myString="DC "+self.cX+" "+self.cY+" "+self.pX+" "+self.pY+" "+self.width+" "+self.layer+"\n"
        return myString
    
    def boardRep(self):
        curve='900'
        shape='3'
        myString="$DRAWSEGMENT\n"
        myString+="Po "+shape+" "+self.cX+" "+self.cY+" "+self.pX+" "+self.pY+" "+self.width+"\n"
        myString+="De "+self.layer+" 0 "+curve+" 0 0\n"
        myString+="$EndDRAWSEGMENT\n"
        return myString
    
    def symRep(self):
        myString="C "+self.cX+" "+self.cY+" "+self.radius+" 0 0 "+self.width+" N\n"
        return myString
    
class Text(object):
    __slots__=("val","x","y","width","size","rot","mirror","hJust","vJust","layer","style","forceCenter")
    
    def __init__(self,node,converter,noTranspose=False, offset=None):    
        
        self.val=node.text
        self.style='Normal'
        layer=getLayerId(node.get('layer'))
        x,y = converter.convertCoordinate(node.get('x'), node.get('y'), noTranspose)
        if offset != None:
            dX, dY =   converter.convertCoordinate(offset[0], offset[1], noTranspose)
            x += dX
            y += dY
            
        self.x=str(x)
        self.y=str(y)
        self.layer=str(layer)
        
        self.getSize(node,converter)
        self.getOrientation(node,converter)
    
    def getSize(self,node,converter):
        size=converter.convertUnit(node.get('size'))        
        wMod=node.get('ratio')
        if wMod==None:
            wMod=8
        else:
            wMod=int(wMod)
        width=size*wMod//100
        self.size=str(size)
        self.width=str(width)
    
    def getOrientation(self,node,converter):
        rot=node.get('rot')
        rot=converter.convertRotation(rot)
        mirror='0' if rot['mirror'] else '1'
        spin=rot['spin']
        rot=rot['rot']
        
        rot=(rot+3600)%3600   #only work with pos angles
    

        if rot%900 != 0:
            print("Warning Text must be rotated increments of 90 degrees")
            print("\tText: "+self.val+"\tRotation: "+str(rot))

        
        just=node.get("align")
        if just==None:
            just="bottom-left"
        just = just.split("-")
        if len(just)==2:
            hJust=just[1]
            vJust=just[0]
        else:#center
            hJust=just[0]
            vJust=just[0]
        
        #if not spin
        #    if angle<=90 or angle>270
        #        just describes where the pointer is compared to text
        #    else:
        #        just describes where the text is compared to pointer
        #else:
        #    just describes where the pointer is compared to text        
        #kicad describes always by where the pointer is rel to the text
        #so to make it consistant we must convert the justification terms
        #to always describe the same thing.
        
        if rot>900 and rot<=2700 and not spin:
            oppositeDict={"left":"right",
                          "right":"left",
                          "center":"center",
                          "top":"bottom",
                          "bottom":"top"}
            
            hJust=oppositeDict[hJust]
            vJust=oppositeDict[vJust]
        
        if not spin and rot>900 and rot<=2700:
            rot=rot-1800
            
            
        self.rot=str(rot)
        self.mirror=str(mirror)
        self.hJust=hJust
        self.vJust=vJust

    def moduleRep(self,num):
        X,Y=self.getModuleFieldOffset()
        #T<field number> <Xpos> <Ypos> <Xsize> <Ysize> <rotation> <penWidth> N <visible> <layer> "text"
        myString="T"+str(num)+" "+X+" "+Y+" "+self.size+" "+self.size+" "+self.rot+" "+self.width+" N V "+self.layer+" \""+self.val+"\"\n"
        return myString
    
    def boardRep(self):
        X,Y=self.getBoardOffset()
        hjustify=self.hJust[0].capitalize()
        try:
            myString='$TEXTPCB\n'         
            myString+='Te "'+self.val+'"\n'
            myString+='Po '+X+' '+Y+' '+self.size+' '+self.size+' '+self.width+' '+self.rot+'\n'
            myString+='De '+self.layer+' '+self.mirror+' 0000 '+self.style+' '+hjustify+'\n'
            myString+='$EndTEXTPCB\n'
        except TypeError:
            return '\n'
        return myString
    
    def symRep(self):
        orientation="0"
        if self.rot=="90" or self.rot=="270":
            orientation="1"
        hJust=self.hJust[0].capitalize()
        vJust=self.vJust[0].capitalize()
        #TODO fix text size
        myString="T "+orientation+" "+self.x+" "+self.y+" "+self.size+" 0 0 0 "+self.val+" Normal 0 "+hJust+" "+vJust+"\n"
        return myString

    def getModuleFieldOffset(self):
        #convert whatever it is to center-center:
        dX,dY=0,0        
        rot=int(self.rot)
        hJust=self.hJust
        vJust=self.vJust
        size=int(self.size)
        
        if rot==0 or rot==1800:
            if hJust=="left":
                dX=len(self.val)//2*size
            if hJust=="right":
                dX=-len(self.val)//2*size
            if vJust=="top":
                dY= size//2
            if vJust=="bottom":
                dY=size//2
                
        elif rot==900 or rot==2700:
            if hJust=="left":
                dY=-len(self.val)//2*size
            if hJust=="right":
                dY=len(self.val)//2*size
            if vJust=="top":
                dX= size//2
            if vJust=="bottom":
                dX=-size//2
                
        X=str(int(int(self.x)+dX))
        Y=str((int(self.y)+dY))
        return X,Y

    def getBoardOffset(self): 

#        if (rot+3600)%3600==0:
#            dY-offset*sign)
#        elif(rot+3600)%3600==900:
#            dX-offset*sign)
#        elif(rot+3600)%3600==1800:
#            dY=offset*sign)
#        elif(rot+3600)%3600==2700:
#            dX=offset*sign)
        #Messed it up
        #convert whatever it is to center-LCR:
        dX,dY=0,0        
        rot=int(self.rot)
        vJust=self.vJust
        size=int(self.size)        
        vsign=0 #if vjust is center
        
        if vJust=="top":
            vsign=-1
        if vJust=="bottom": 
            vsign=1
            
        offset=size//2
        
        if rot==0:
            dY=-offset*vsign
        elif rot==900:
            dX=-offset*vsign
        elif rot==1800:
            dY=offset*vsign
        elif rot==2700:
            dX=offset*vsign
                
        X=str(int(int(self.x)+dX))
        Y=str((int(self.y)+dY))
        return X,Y

    def getSchemOffset(self):
        #TODO Schem only allow s Bottom-Left (right,down), Bottom-Right(left,up), 
        return self.x,self.y
