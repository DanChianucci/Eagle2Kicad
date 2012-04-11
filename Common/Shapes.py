'''
Created on Apr 3, 2012

@author: Dan
'''
import math
import LayerIds

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
                
        self.x1=str(x1)
        self.y1=str(y1)
        self.x2=str(x2)
        self.y2=str(y2)
        self.width=str(width)
        self.layer=str(layer)
        self.curve=str(curve)

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
        stype="DS " if self.curve=="None" else "DA "
        curve=" " if self.curve=="None" else " "+str(self.curve)+" "
        
        myString=stype+str(self.x1)+" "+str(self.y1)+" "+str(self.x2)+" "+str(self.y2)
        myString+=curve+str(self.width)+" "+str(self.layer)+"\n"
        
        return myString

    def boardRep(self):
        if self.curve=="None":
            shape='0'
            curve='900'
        else:
            shape='2'
            curve=self.curve
        
        myString="$DRAWSEGMENT\n"
        myString+="Po "+shape+" "+self.x1+" "+self.y1+" "+self.x2+" "+self.y2+" "+self.width+"\n"
        myString+="De "+self.layer+" 0 "+curve+" 0 0\n"
        myString+="$EndDRAWSEGMENT\n"
        return myString
    
    def symRep(self):
        if self.curve=="NONE":
            myString="P 2 0 0 "+self.width+" "+self.x1+" "+self.y1+" "+self.x2+" "+self.y2+" N\n"
            return myString
        else:#TODO Curve Support in symbols lines
            myString="P 2 0 0 "+self.width+" "+self.x1+" "+self.y1+" "+self.x2+" "+self.y2+" N\n"
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

class Via():
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
        self.extent=LayerIds.makeViaMask(extent)
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
        
        
class Polyline(object):
    __slots__=("lines")
    
    def __init__(self, node, converter, noTranspose=False):
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
            line=Line(wire,converter,noTranspose)
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
        
class Circle(object):
    __slots__=('cX','cY','pX','pY','layer','width',"radius")
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
    
    def __init__(self,node,converter,noTranspose=False):    
        
        self.val=node.text
        self.style='Normal'
        layer=LayerIds.getLayerId(node.get('layer'))
        x,y=converter.convertCoordinate(node.get('x'),node.get('y'),noTranspose)
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
        
        rot=(rot+3600)%3600
    

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
        myString='$TEXTPCB\n'         
        myString+='Te "'+self.val+'"\n'
        myString+='Po '+X+' '+Y+' '+self.size+' '+self.size+' '+self.width+' '+self.rot+'\n'
        myString+='De '+self.layer+' '+self.mirror+' 0000 '+self.style+' '+hjustify+'\n'
        myString+='$EndTEXTPCB\n'
        return myString
    
    def symRep(self):
        orientation="0"
        if self.rot=="90" or self.rot=="270":
            orientation="1"
        hJust=self.hJust[0].capitalise()
        vJust=self.vJust[0].capitalise()
        
        myString="T "+orientation+" "+self.x+" "+self.y+" "+self.width+" 0 0 0 "+self.val+" Normal 0 "+hJust+" "+vJust+"\n"
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
        #convert whatever it is to center-LCR:
        dX,dY=0,0        
        rot=int(self.rot)
        vJust=self.vJust
        size=int(self.size)
           
        if rot==0 or rot==1800:
            if vJust=="top":
                dY=-size//2
            if vJust=="bottom":
                dY=size//2
                
        elif rot==900 or rot==2700:
            if vJust=="top":
                dX=-size//2
            if vJust=="bottom":
                dX=size//2
                
        X=str(int(int(self.x)+dX))
        Y=str((int(self.y)+dY))
        return X, Y
        return X,Y

    def getSchemOffset(self):
        #dont need to force anything
        return self.x,self.y
















