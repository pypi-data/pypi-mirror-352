from ._mapi import *
from ._node import *

import numpy as np

def _ADD(self):
    # Commom HERE ---------------------------------------------
    id = int(self.ID)
    if Element.ids == []: 
        count = 1
    else:
        count = max(Element.ids)+1

    if id==0 :
        self.ID = count
        Element.elements.append(self)
        Element.ids.append(int(self.ID))
    elif id in Element.ids:
        self.ID=int(id)
        print(f'⚠️  Element with ID {id} already exist! It will be replaced.')
        index=Element.ids.index(id)
        Element.elements[index]=self
    else:
        self.ID=id        
        Element.elements.append(self)
        Element.ids.append(int(self.ID))
    # Common END -------------------------------------------------------


def _updateElem(self):
    js2s = {'Assign':{self.ID : _Obj2JS(self)}}
    MidasAPI('PUT','/db/elem',js2s)
    return js2s




def _Obj2JS(obj):

    js={}

    if obj.TYPE == 'BEAM':
        #---  BEAM ---------------------------------------
        js =  {
            "TYPE": obj.TYPE,
            "MATL": obj.MATL,
            "SECT": obj.SECT,
            "NODE": [
                obj.NODE[0],
                obj.NODE[1]
            ],
            "ANGLE": obj.ANGLE
        }
    elif obj.TYPE == 'TRUSS':
        #---  TRUSS ---------------------------------------
        js =  {
            "TYPE": obj.TYPE,
            "MATL": obj.MATL,
            "SECT": obj.SECT,
            "NODE": [
                obj.NODE[0],
                obj.NODE[1]
            ],
            "ANGLE": obj.ANGLE
        }
    
    elif obj.TYPE == 'PLATE':
        #---  PLATE ---------------------------------------
        js =  {
            "TYPE": obj.TYPE,
            "MATL": obj.MATL,
            "SECT": obj.SECT,
            "NODE": obj.NODE,
            "ANGLE": obj.ANGLE,
            "STYPE": obj.STYPE
        }

    return js

def _JS2Obj(id,js):
    type = js['TYPE']
    matl = js['MATL']
    sect = js['SECT']
    node = js['NODE']
    angle = js['ANGLE']

    if type == 'BEAM':
        Element.Beam(node[0],node[1],matl,sect,angle,id)
    elif type == 'TRUSS':
        Element.Truss(node[0],node[1],matl,sect,angle,id)
    elif type == 'PLATE':
        stype = js['STYPE']
        Element.Plate(node,stype,matl,sect,angle,id)
    


class _common:
    def __str__(self):
        return str(f'ID = {self.ID}  \nJSON : {_Obj2JS(self)}\n')

    def update(self):
        return _updateElem(self)






#6 Class to create elements
class Element:
    """ Use Beam or Truss function"""
    elements = []
    ids = []

    @classmethod
    def json(cls):
        json = {"Assign":{}}
        for elem in cls.elements:
            js = _Obj2JS(elem)
            json["Assign"][elem.ID] = js
        return json
    
    @classmethod
    def create(cls):
        if cls.elements!=[]:
            MidasAPI("PUT","/db/ELEM",Element.json())
        
    @staticmethod
    def get():
        return MidasAPI("GET","/db/ELEM")
    
    @staticmethod
    def sync():
        a = Element.get()
        if a != {'message': ''}:
            if list(a['ELEM'].keys()) != []:
                Element.elements = []
                Element.ids=[]
                for elem_id in a['ELEM'].keys():
                    _JS2Obj(elem_id,a['ELEM'][elem_id])
    
    @staticmethod
    def delete():
        MidasAPI("DELETE","/db/ELEM")
        Element.elements=[]
        Element.ids=[]
        


    class Beam(_common):

        def __init__(self,i:int,j:int,mat:int=1,sect:int=1,angle:float=0,id:int=0):
            self.ID = id
            self.TYPE = 'BEAM'
            self.MATL = mat
            self.SECT = sect
            self.NODE=[i,j]
            self.ANGLE = angle

            _ADD(self)

        @staticmethod
        def SDL(s_loc:list,dir:list,l:float,n:int=1,mat:int=1,sect:int=1,angle:float=0,id:int=0): #CHANGE TO TUPLE
            beam_nodes =[]
            beam_obj = []
            s_locc = np.array(s_loc)
            unit_vec = np.array(dir)/np.linalg.norm(dir)

            for i in range(n+1):
                locc = s_locc+i*l*unit_vec/n
                Enode=Node(locc[0].item(),locc[1].item(),locc[2].item())
                beam_nodes.append(Enode.ID)
            
            for i in range(n):
                if id == 0 : id_new = 0
                else: id_new = id+i
                beam_obj.append(Element.Beam(beam_nodes[i],beam_nodes[i+1],mat,sect,angle,id_new))
            
            return beam_obj
                

        @staticmethod
        def SE(s_loc:list,e_loc:list,n:int=1,mat:int=1,sect:int=1,angle:float=0,id:int=0):
            beam_nodes =[]
            beam_obj = []
            i_loc = np.linspace(s_loc,e_loc,n+1)
            for i in range(n+1):
                Enode=Node(i_loc[i][0].item(),i_loc[i][1].item(),i_loc[i][2].item())
                beam_nodes.append(Enode.ID)
            
            for i in range(n):
                if id == 0 : id_new = 0
                else: id_new = id+i
                beam_obj.append(Element.Beam(beam_nodes[i],beam_nodes[i+1],mat,sect,angle,id_new))
            
            return beam_obj





    class Truss(_common):

        def __init__(self,i:int,j:int,mat:int=1,sect:int=1,angle:float=0,id:int=0):
            self.ID = id
            self.TYPE = 'TRUSS'
            self.MATL = mat
            self.SECT = sect
            self.NODE=[i,j]
            self.ANGLE = angle

            _ADD(self)
            


        @staticmethod
        def SDL(s_loc:list,dir:list,l:float,n:int=1,mat:int=1,sect:int=1,angle:float=0,id:int=0):
            beam_nodes =[]
            beam_obj =[]
            s_locc = np.array(s_loc)
            unit_vec = np.array(dir)/np.linalg.norm(dir)

            for i in range(n+1):
                locc = s_locc+i*l*unit_vec/n
                Enode=Node(locc[0].item(),locc[1].item(),locc[2].item())
                beam_nodes.append(Enode.ID)
            
            for i in range(n):
                if id == 0 : id_new = 0
                else: id_new = id+i
                beam_obj.append(Element.Truss(beam_nodes[i],beam_nodes[i+1],mat,sect,angle,id_new))
            
            return beam_obj
                

        @staticmethod
        def SE(s_loc:list,e_loc:list,n:int=1,mat:int=1,sect:int=1,angle:float=0,id:int=0):
            beam_nodes =[]
            beam_obj = []
            i_loc = np.linspace(s_loc,e_loc,n+1)
            for i in range(n+1):
                Enode=Node(i_loc[i][0].item(),i_loc[i][1].item(),i_loc[i][2].item())
                beam_nodes.append(Enode.ID)
            
            for i in range(n):
                if id == 0 : id_new = 0
                else: id_new = id+i
                beam_obj.append(Element.Truss(beam_nodes[i],beam_nodes[i+1],mat,sect,angle,id_new))
            
            return beam_obj
    


    class Plate(_common):

        def __init__(self,nodes:list,stype:int=1,mat:int=1,sect:int=1,angle:float=0,id:int=0):
            self.ID = id
            self.TYPE = 'PLATE'
            self.MATL = mat
            self.SECT = sect
            self.NODE=nodes
            self.ANGLE = angle
            self.STYPE = stype

            _ADD(self)


    







