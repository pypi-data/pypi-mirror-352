from ._mapi import *




class Material:
    mats = []
    ids = []
    def __init__(self,data,id=0):
        if Material.ids == []: 
            count = 1
        else:
            count = max(Material.ids)+1
        if id == 0 or id in Material.ids: self.ID = count
        if id!= 0 and id not in Material.ids: self.ID = id

        self.DATA = data

        Material.mats.append(self)
        Material.ids.append(self.ID)
    
    @classmethod
    def json(cls):
        json = {"Assign":{}}
        for k in cls.mats:
            json["Assign"][k.ID]=k.DATA
        return json
    
    @staticmethod
    def create_only():
        MidasAPI("PUT","/db/MATL",Material.json())
        
    @staticmethod
    def get():
        return MidasAPI("GET","/db/MATL")
    
    
    @staticmethod
    def delete():
        MidasAPI("DELETE","/db/MATL")
        Material.mats=[]
        Material.ids=[]

    @staticmethod
    def sync():
        a = Material.get()
        if a != {'message': ''}:
            if list(a['MATL'].keys()) != []:
                Material.mats = []
                Material.ids=[]
                for j in a['MATL'].keys():
                    Material(a['MATL'][j], int(j))

        # ----------------------------------  ALL FUNCTIONS  ---------------------------------------------------
    
    @staticmethod
    def create():
        if Material.mats!=[] : Material.create()
        if CreepShrinkage.mats!=[] : CreepShrinkage.create()
        if CompStrength.mats!=[] : CompStrength.create()
        if TDLink.json()!={'Assign':{}} : TDLink.create()
        
    
    @staticmethod
    def deleteAll():
        Material.delete()
        CreepShrinkage.delete()
        CompStrength.delete()
        


# ---------------------------------  CONCRETE MATERIAL --------------------------------------------------------------

    class CONC:


        # ----------------------------------  DB MATERIAL ---------------------------------------------------

        def __init__(self,name='',standard='',db='',id:int=0,):  
            js =  {
                "TYPE": "CONC",
                "NAME": name,
                "DAMP_RAT": 0.05,
                "PARAM": [
                    {
                        "P_TYPE": 1,
                        "STANDARD": standard,
                        "CODE": "",
                        "DB": db,
                    }
                ]
            }
            temp = Material(js,id)
            self.ID = temp.ID
            self.DATA = js


        # ----------------------------------  USER MATERIAL ---------------------------------------------------

        class User:
            def __init__(self,name='',E=0,pois=0,den=0,mass=0,therm=0,id:int=0,):
                js =  {
                    "TYPE": "CONC",
                    "NAME": name,
                    "DAMP_RAT": 0.05,
                    "PARAM": [
                        {
                            "P_TYPE": 2,
                            "ELAST": E,
                            "POISN": pois,
                            "THERMAL": therm,
                            "DEN": den,
                            "MASS": mass
                        }
                    ]
                }
                temp = Material(js,id)
                self.ID = temp.ID
                self.DATA = js

    

# ---------------------------------  STEEL MATERIAL --------------------------------------------------------------

    class STEEL:

        # ----------------------------------  DB MATERIAL ---------------------------------------------------

        def __init__(self,name='',standard='',db='',id:int=0,):
            js =  {
                "TYPE": "STEEL",
                "NAME": name,
                "DAMP_RAT": 0.05,
                "PARAM": [
                    {
                        "P_TYPE": 1,
                        "STANDARD": standard,
                        "CODE": "",
                        "DB": db,
                    }
                ]
            }
            temp = Material(js,id)
            self.ID = temp.ID
            self.DATA = js


        # ----------------------------------  USER MATERIAL ---------------------------------------------------

        class User:
            def __init__(self,name='',E=0,pois=0,den=0,mass=0,therm=0,id:int=0,):
                js =  {
                    "TYPE": "STEEL",
                    "NAME": name,
                    "DAMP_RAT": 0.05,
                    "PARAM": [
                        {
                            "P_TYPE": 2,
                            "ELAST": E,
                            "POISN": pois,
                            "THERMAL": therm,
                            "DEN": den,
                            "MASS": mass
                        }
                    ]
                }
                temp = Material(js,id)
                self.ID = temp.ID
                self.DATA = js




# ---------------------------------  USER MATERIAL --------------------------------------------------------------

    class USER:

        def __init__(self,name='',E=0,pois=0,den=0,mass=0,therm=0,id:int=0,):
            js =  {
                "TYPE": "USER",
                "NAME": name,
                "DAMP_RAT": 0.05,
                "PARAM": [
                    {
                        "P_TYPE": 2,
                        "ELAST": E,
                        "POISN": pois,
                        "THERMAL": therm,
                        "DEN": den,
                        "MASS": mass
                    }
                ]
            }
            temp = Material(js,id)
            self.ID = temp.ID
            self.DATA = js




#------------------------------------------ TIME DEPENDENT - CREEP and SHRINKAGE ----------------------------------------------------



class CreepShrinkage:
    mats = []
    ids = []
    def __init__(self,data,id=0):
        if CreepShrinkage.ids == []: 
            count = 1
        else:
            count = max(CreepShrinkage.ids)+1
        if id == 0 or id in CreepShrinkage.ids: self.ID = count
        if id!= 0 and id not in CreepShrinkage.ids: self.ID = id

        self.DATA = data

        CreepShrinkage.mats.append(self)
        CreepShrinkage.ids.append(self.ID)
    
    @classmethod
    def json(cls):
        json = {"Assign":{}}
        for k in cls.mats:
            json["Assign"][k.ID]=k.DATA
        return json
    
    @staticmethod
    def create():
        MidasAPI("PUT","/db/TDMT",CreepShrinkage.json())
        
    @staticmethod
    def get():
        return MidasAPI("GET","/db/TDMT")
    
    
    @staticmethod
    def delete():
        MidasAPI("DELETE","/db/TDMT")
        CreepShrinkage.mats=[]
        CreepShrinkage.ids=[]

    @staticmethod
    def sync():
        a = CreepShrinkage.get()
        if a != {'message': ''}:
            if list(a['TDMT'].keys()) != []:
                CreepShrinkage.mats = []
                CreepShrinkage.ids=[]
                for j in a['TDMT'].keys():
                    CreepShrinkage(a['TDMT'][j], int(j))



    # ---------------------------------  IRC CnS --------------------------------------------------------------

    class IRC:

        def __init__(self,name='',code="INDIA_IRC_112_2011",fck=0,notionalSize=1,relHumidity=70,ageShrinkage=3,typeCement='NR',id:int=0,):  
            js =  {
                "NAME": name,
                "CODE": code,
                "STR": fck,
                "HU": relHumidity,
                "AGE": ageShrinkage,
                "MSIZE": notionalSize,
                "CTYPE": typeCement
            }
            temp = CreepShrinkage(js,id)
            self.ID = temp.ID
            self.DATA = js





#------------------------------------------ TIME DEPENDENT - COMPRESSIVE STRENGTH ----------------------------------------------------



class CompStrength:
    mats = []
    ids = []
    def __init__(self,data,id=0):
        if CompStrength.ids == []: 
            count = 1
        else:
            count = max(CompStrength.ids)+1
        if id == 0 or id in CompStrength.ids: self.ID = count
        if id!= 0 and id not in CompStrength.ids: self.ID = id

        self.DATA = data

        CompStrength.mats.append(self)
        CompStrength.ids.append(self.ID)
    
    @classmethod
    def json(cls):
        json = {"Assign":{}}
        for k in cls.mats:
            json["Assign"][k.ID]=k.DATA
        return json
    
    @staticmethod
    def create():
        MidasAPI("PUT","/db/TDME",CompStrength.json())
        
    @staticmethod
    def get():
        return MidasAPI("GET","/db/TDME")
    
    
    @staticmethod
    def delete():
        MidasAPI("DELETE","/db/TDME")
        CompStrength.mats=[]
        CompStrength.ids=[]

    @staticmethod
    def sync():
        a = CompStrength.get()
        if a != {'message': ''}:
            if list(a['TDME'].keys()) != []:
                CompStrength.mats = []
                CompStrength.ids=[]
                for j in a['TDME'].keys():
                    CompStrength(a['TDME'][j], int(j))



    # ---------------------------------  IRC Compressive Strength --------------------------------------------------------------

    class IRC:

        def __init__(self,name,code="INDIA(IRC:112-2020)",fckDelta=0,typeCement=1,typeAggregate=0,id:int=0,):  
            js =   {
                "NAME": name,
                "TYPE": "CODE",
                "CODENAME": code,
                "STRENGTH": fckDelta,
                "iCTYPE": typeCement,
                "nAGGRE": typeAggregate
            }
            temp = CompStrength(js,id)
            self.ID = temp.ID
            self.DATA = js





#------------------------------------------ TIME DEPENDENT - MATERIAL LINK  ----------------------------------------------------



class TDLink:
    mats = {}
    def __init__(self,matID,CnSName='',CompName=''):

        TDLink.mats[str(matID)]={
            "TDMT_NAME": CnSName,
            "TDME_NAME": CompName
        }
    
    @classmethod
    def json(cls):
        json = {"Assign": TDLink.mats}
        return json
    
    @staticmethod
    def create():
        MidasAPI("PUT","/db/TMAT",TDLink.json())
        
    @staticmethod
    def get():
        return MidasAPI("GET","/db/TMAT")
    
    
    @staticmethod
    def delete():
        MidasAPI("DELETE","/db/TMAT")
        TDLink.mats={}

    @staticmethod
    def sync():
        a = TDLink.get()
        if a != {'message': ''}:
            if list(a['TMAT'].keys()) != []:
                TDLink.mats = []
                TDLink.ids=[]
                for j in a['TMAT'].keys():
                    TDLink(a['TMAT'][j], int(j))

