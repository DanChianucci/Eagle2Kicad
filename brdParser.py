from xml.parsers.expat import ParserCreate
class brdParser:
    __slots__=('myDict','tree','polygonHolder','polygonIndex','lastPolygonHolder','textHolder','lastTextHolder','textIndex','addTo')
    
    def __init__(self):
        self.myDict={}
        self.tree=[]
        self.polygonIndex=-1
        self.polygonHolder=''
        self.lastPolygonHolder=''
        self.textHolder=''
        self.lastTextHolder=''
        self.textIndex=-1
        self.addTo=self.myDict
        
    def start_element(self,name,attrs):
        self.addTo=self.myDict
    
        if name=='autorouter' or name=='designrules' or self.tree.__contains__('designrules') or self.tree.__contains__('autorouter'):
                self.tree.append(name)
                return None
        
        if len(self.tree)>0:     
            for unit in self.tree:
                self.addTo=self.addTo[unit]
        
        if name=='setting':
            for key in attrs:
                self.addTo[key]=attrs[key]        
        else:
            if name=='layer': 
                name=attrs['number']
                self.addTo[name]=attrs            
            
            elif name=='element' or name=='signal' or name=='library' or name=='class' or name=='package' or name=='attribute':
                name=attrs['name']
                self.addTo[name]=attrs
            
            elif name=='smd' or name=='pad':
                if self.addTo.get(name)==None:
                    self.addTo[name]={}
                pname=attrs['name']
                self.addTo[name][pname]=attrs
            
            elif name=='contactref':
                if self.addTo.get('contactref')==None:
                    self.addTo['contactref']={}
                name=attrs['element']+':'+attrs['pad']
                self.addTo['contactref'][name]=attrs
                
            elif name=='wire' or name=='circle' or name=='rectangle' or name=='polygon' or name=='via':
                if name=='polygon':
                    self.polygonHolder=self.tree[-1]
                    if not self.polygonHolder == self.lastPolygonHolder:
                        self.polygonIndex=-1
                        self.lastPolygonHolder=self.polygonHolder
                    self.polygonIndex+=1
                    
                if self.addTo.get(name)==None:
                    self.addTo[name]=[]
                
                self.addTo[name].append(attrs)
            
            elif name=='vertex':
                #vertexs lie within polygon... therefore self.addTo will be a list of dictionaries see above
                #we must add the vertex to the correct dictionary
                if self.addTo[self.polygonIndex].get('vertex')==None: #makes sure there is a vertex list in the polygon
                    self.addTo[self.polygonIndex]['vertex']=[]
                self.addTo[self.polygonIndex]['vertex'].append(attrs)
    
            
            elif name=='text':
                self.textHolder=self.tree[-1]
                if not self.textHolder == self.lastTextHolder:
                    self.textIndex=-1
                    self.lastTextHolder=self.textHolder
                self.textIndex+=1
                    
                if self.addTo.get(name)==None:
                    self.addTo[name]=[]            
                self.addTo[name].append(attrs)
            
            else:
                self.addTo[name]=attrs    
            
        self.tree.append(name)   
    
    def end_element(self,name):
        self.tree.pop()
    
    def char_data(self,data):
        if self.tree[-1]=='text':
            if self.addTo['text'][self.textIndex].get('txtData')==None:
                self.addTo['text'][self.textIndex]['txtData']=''
            self.addTo['text'][self.textIndex]['txtData']+=data
    
    def parse(self,inFile):
        encoding='utf-8'
        p=ParserCreate(encoding)
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        contents=''
        for line in inFile:
            contents+=line.strip()  
        p.Parse(contents)
        self.myDict['border']=self.getBorder()

        

        return self.myDict
    
    def getBorder(self):
        left=float('inf')
        right=float('-inf')
        top=float('-inf')
        bottom=float('inf')
        
        wires=self.myDict['eagle']['drawing']['board']['plain']['wire']
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
        
        border={'left':str(left),'right':str(right),'top':str(top),'bottom':str(bottom),'cX':str(cX),'cY':str(cY)}    
        return border