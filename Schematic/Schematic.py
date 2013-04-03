'''
Created on Apr 5, 2012

@author: Dan
'''
import sys

if "../Common" not in sys.path:
    sys.path.append(r'../Common')
    

class Schematic(object):
    __slots__=("components","noConnects","sheets","texts","junction","wires","busses","busEntries")


    def __init__(self,node,converter=None):
        pass
        
