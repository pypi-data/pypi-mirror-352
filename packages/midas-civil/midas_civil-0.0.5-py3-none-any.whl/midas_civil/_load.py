from ._mapi import *
from ._model import *
from ._group import *

#11 Class to define Load Cases:
class Load_Case:
    """Type symbol (Refer Static Load Case section in the Onine API Manual, Load Case names.  
    \nSample: Load_Case("USER", "Case 1", "Case 2", ..., "Case n")"""
    cases = []
    types = ["USER", "D", "DC", "DW", "DD", "EP", "EANN", "EANC", "EAMN", "EAMC", "EPNN", "EPNC", "EPMN", "EPMC", "EH", "EV", "ES", "EL", "LS", "LSC", 
            "L", "LC", "LP", "IL", "ILP", "CF", "BRK", "BK", "CRL", "PS", "B", "WP", "FP", "SF", "WPR", "W", "WL", "STL", "CR", "SH", "T", "TPG", "CO",
            "CT", "CV", "E", "FR", "IP", "CS", "ER", "RS", "GE", "LR", "S", "R", "LF", "RF", "GD", "SHV", "DRL", "WA", "WT", "EVT", "EEP", "EX", "I", "EE"]
    def __init__(self, type, *name):
        self.TYPE = type
        self.NAME = name
        self.ID = []
        for i in range(len(self.NAME)):
            if Load_Case.cases == []: self.ID.append(i+1)
            if Load_Case.cases != []: self.ID.append(max(Load_Case.cases[-1].ID) + i + 1)
        Load_Case.cases.append(self)
    
    @classmethod
    def json(cls):
        ng = []
        json = {"Assign":{}}
        for i in cls.cases:
            if i.TYPE in cls.types:
                for j in i.ID:
                    json['Assign'][j] = {
                        "NAME": i.NAME[i.ID.index(j)],
                        "TYPE": i.TYPE}
            else:
                ng.append(i.TYPE)
        if ng != []: print(f"These load case types are incorrect: {ng}.\nPlease check API Manual.")
        return json
    
    @staticmethod
    def create():
        MidasAPI("PUT","/db/stld",Load_Case.json())
        
    @staticmethod
    def get():
        return MidasAPI("GET","/db/stld")
    
    @staticmethod
    def sync():
        a = Load_Case.get()
        if a != {'message': ''}:
            if list(a['STLD'].keys()) != []:
                Load_Case.cases = []
                for j in a['STLD'].keys():
                    Load_Case(a['STLD'][j]['TYPE'], a['STLD'][j]['NAME'])
    
    @classmethod
    def delete(cls):
        cls.cases=[]
        return MidasAPI("DELETE","/db/stld")
#---------------------------------------------------------------------------------------------------------------



class Load:

    @classmethod
    def create(cls):
        if Load_Case.cases!=[]: Load_Case.create()
        if cls.SW.data!=[]: cls.SW.create()
        if cls.Nodal.data!=[]: cls.Nodal.create()
        if cls.Beam.data!=[]: cls.Beam.create()
        

    class SW:
        """Load Case Name, direction, Value, Load Group.\n
        Sample: Load_SW("Self-Weight", "Z", -1, "DL")"""
        data = []
        def __init__(self, load_case, dir = "Z", value = -1, load_group = ""):
            chk = 0
            for i in Load_Case.cases:
                if load_case in i.NAME: chk = 1
            if chk == 0: Load_Case("D", load_case)
            if load_group != "":
                chk = 0
                a = [v['NAME'] for v in Group.Load.json()["Assign"].values()]
                if load_group in a: chk = 1
                if chk == 0: Group.Load(load_group)

            if type(value)==int:
                if dir == "X":
                    fv = [value, 0, 0]
                elif dir == "Y":
                    fv = [0, value, 0]
                else:
                    fv = [0, 0, value]
            elif type(value)==list:
                fv = value
            else: fv = [0,0,-1]


            self.LC = load_case
            self.DIR = dir
            self.FV = fv
            self.LG = load_group
            self.ID = len(Load.SW.data) + 1
            Load.SW.data.append(self)
        
        @classmethod
        def json(cls):
            json = {"Assign":{}}
            for i in cls.data:
                json["Assign"][i.ID] = {
                    "LCNAME": i.LC,
                    "GROUP_NAME": i.LG,
                    "FV": i.FV
                }
            return json
        
        @staticmethod
        def create():
            MidasAPI("PUT","/db/BODF",Load.SW.json())
        
        @staticmethod
        def get():
            return MidasAPI("GET","/db/BODF")
        
        @staticmethod
        def sync():
            a = Load.SW.get()
            if a != {'message': ''}:
                for i in list(a['BODF'].keys()):
                    if a['BODF'][i]['FV'][0] != 0:
                        di = "X"
                        va = a['BODF'][i]['FV'][0]
                    elif a['BODF'][i]['FV'][1] != 0:
                        di = "Y"
                        va = a['BODF'][i]['FV'][1]
                    else:
                        di = "Z"
                        va = a['BODF'][i]['FV'][2]
                    Load.SW(a['BODF'][i]['LCNAME'], di, va, a['BODF'][i]['GROUP_NAME'])
    
    
    #--------------------------------   NODAL LOADS  ------------------------------------------------------------

    #18 Class to add Nodal Loads:
    class Nodal:
        """Creates node loads and converts to JSON format.
        Example: Load_Node(101, "LC1", "Group1", FZ = 10)
        """
        data = []
        def __init__(self, node, load_case, load_group = "", FX:float = 0, FY:float = 0, FZ:float= 0, MX:float =0, MY:float =0, MZ:float=0, id = ""):


            chk = 0
            for i in Load_Case.cases:
                if load_case in i.NAME: chk = 1
            if chk == 0: Load_Case("D", load_case)
            if load_group != "":
                chk = 0
                a = [v['NAME'] for v in Group.Load.json()["Assign"].values()]
                if load_group in a: chk = 1
                if chk == 0: Group.Load(load_group)


            self.NODE = node
            self.LCN = load_case
            self.LDGR = load_group
            self.FX = FX
            self.FY = FY
            self.FZ = FZ
            self.MX = MX
            self.MY = MY
            self.MZ = MZ
            if id == "": id = len(Load.Nodal.data) + 1
            self.ID = id
            Load.Nodal.data.append(self)
        
        @classmethod
        def json(cls):
            json = {"Assign": {}}
            for i in cls.data:
                if i.NODE not in list(json["Assign"].keys()):
                    json["Assign"][i.NODE] = {"ITEMS": []}

                json["Assign"][i.NODE]["ITEMS"].append({
                    "ID": i.ID,
                    "LCNAME": i.LCN,
                    "GROUP_NAME": i.LDGR,
                    "FX": i.FX,
                    "FY": i.FY,
                    "FZ": i.FZ,
                    "MX": i.MX,
                    "MY": i.MY,
                    "MZ": i.MZ
                })
            return json
        
        @classmethod
        def create(cls):
            MidasAPI("PUT", "/db/CNLD",cls.json())
        
        @classmethod
        def get(cls):
            return MidasAPI("GET", "/db/CNLD")
        
        @classmethod
        def delete(cls):
            cls.data=[]
            return MidasAPI("DELETE", "/db/CNLD")
        
        @classmethod
        def sync(cls):
            cls.data = []
            a = cls.get()
            if a != {'message': ''}:
                for i in a['CNLD'].keys():
                    for j in range(len(a['CNLD'][i]['ITEMS'])):
                        Load.Nodal(int(i),a['CNLD'][i]['ITEMS'][j]['LCNAME'], a['CNLD'][i]['ITEMS'][j]['GROUP_NAME'], 
                            a['CNLD'][i]['ITEMS'][j]['FX'], a['CNLD'][i]['ITEMS'][j]['FY'], a['CNLD'][i]['ITEMS'][j]['FZ'], 
                            a['CNLD'][i]['ITEMS'][j]['MX'], a['CNLD'][i]['ITEMS'][j]['MY'], a['CNLD'][i]['ITEMS'][j]['MZ'],
                            a['CNLD'][i]['ITEMS'][j]['ID'])
    #---------------------------------------------------------------------------------------------------------------

    #19 Class to define Beam Loads:
    class Beam:
        data = []
        def __init__(self, element: int, load_case: str, value: float, load_group: str = "", direction: str = "GZ",
            id = "", D = [0, 1, 0, 0], P = [0, 0, 0, 0], cmd = "BEAM", typ = "UNILOAD", use_ecc = False, use_proj = False,
            eccn_dir = "LZ", eccn_type = 1, ieccn = 0, jeccn = 0.0000195, adnl_h = False, adnl_h_i = 0, adnl_h_j = 0.0000195): 
            """
            element: Element Number 
            load_case (str): Load case name
            load_group (str, optional): Load group name. Defaults to ""
            value (float): Load value
            direction (str): Load direction (e.g., "GX", "GY", "GZ", "LX", "LY", "LZ"). Defaults to "GZ"
            id (str, optional): Load ID. Defaults to auto-generated
            D: Relative distance (list with 4 values, optional) based on length of element. Defaults to [0, 1, 0, 0]
            P: Magnitude of UDL at corresponding position of D (list with 4 values, optional). Defaults to [value, value, 0, 0]
            cmd: Load command (e.g., "BEAM", "LINE", "TYPICAL")
            typ: Load type (e.g., "CONLOAD", "CONMOMENT", "UNITLOAD", "UNIMOMENT", "PRESSURE")
            use_ecc: Use eccentricity (True or False). Defaults to False.
            use_proj: Use projection (True or False). Defaults to False.
            eccn_dir: Eccentricity direction (e.g., "GX", "GY", "GZ", "LX", "LY", "LZ"). Defaults to "LZ"
            eccn_type: Eccentricity from offset (1) or centroid (0). Defaults to 1.
            ieccn, jeccn: Eccentricity values at i-end and j-end of the element
            adnl_h: Consider additional H when applying pressure on beam (True or False). Defaults to False.
            adnl_h_i, adnl_h_j: Additional H values at i-end and j-end of the beam.  Defaults to 0.\n
            Example:
            - Load_Beam(115, "UDL_Case", "", -50.0, "GZ")  # No eccentricity
            - Load_Beam(115, "UDL_Case", "", -50.0, "GZ", ieccn=2.5)  # With eccentricity
            """

            chk = 0
            for i in Load_Case.cases:
                if load_case in i.NAME: chk = 1
            if chk == 0: Load_Case("D", load_case)
            if load_group != "":
                chk = 0
                a = [v['NAME'] for v in Group.Load.json()["Assign"].values()]
                if load_group in a: chk = 1
                if chk == 0: Group.Load(load_group)



            D = (D + [0] * 4)[:4]
            P = (P + [0] * 4)[:4]
            if P == [0, 0, 0, 0]: P = [value, value, 0, 0]
            if eccn_type != 0 or eccn_type != 1: eccn_type = 0
            if direction not in ("GX", "GY", "GZ", "LX", "LY", "LZ"): direction = "GZ"
            if eccn_dir not in ("GX", "GY", "GZ", "LX", "LY", "LZ"): eccn_dir = "LY"
            if cmd not in ("BEAM", "LINE", "TYPICAL"): cmd = "BEAM"
            if typ not in ("CONLOAD", "CONMOMENT", "UNILOAD", "UNIMOMENT","PRESSURE"): typ = "UNILOAD"
            if use_ecc == False:
                if ieccn != 0 or jeccn != 0.0000195: use_ecc = True
            self.ELEMENT = element
            self.LCN = load_case
            self.LDGR = load_group
            self.VALUE = value
            self.DIRECTION = direction
            self.CMD = cmd
            self.TYPE = typ
            self.USE_PROJECTION = use_proj
            self.USE_ECCEN = use_ecc
            self.ECCEN_TYPE = eccn_type
            self.ECCEN_DIR = eccn_dir
            self.IECC = ieccn
            if jeccn == 0.0000195:
                self.JECC = 0
                self.USE_JECC = False
            else:
                self.JECC = jeccn
                self.USE_JECC = True
            self.D = D
            self.P = P
            self.USE_H = adnl_h
            self.I_H = adnl_h_i
            if adnl_h == 0.0000195:
                self.USE_JH = False
                self.J_H = 0
            else:
                self.USE_JH = True
                self.J_H = adnl_h_j
            
            if id == "":
                id = len(Load.Beam.data) + 1
            self.ID = id
            Load.Beam.data.append(self)
        
        @classmethod
        def json(cls):
            json = {"Assign": {}}
            for i in cls.data:
                item_data = {
                    "ID": i.ID,
                    "LCNAME": i.LCN,
                    "GROUP_NAME": i.LDGR,
                    "CMD": i.CMD,
                    "TYPE": i.TYPE,
                    "DIRECTION": i.DIRECTION,
                    "USE_PROJECTION": i.USE_PROJECTION,
                    "USE_ECCEN": i.USE_ECCEN,
                    "D": i.D,
                    "P": i.P
                }
                if i.USE_ECCEN == True:
                    item_data.update({
                        "ECCEN_TYPE": i.ECCEN_TYPE,
                        "ECCEN_DIR": i.ECCEN_DIR,
                        "I_END": i.IECC,
                        "J_END": i.JECC,
                        "USE_J_END": i.USE_JECC
                    })
                if i.TYPE == "PRESSURE":
                    item_data.update({
                        "USE_ADDITIONAL": i.USE_H,
                        "ADDITIONAL_I_END": i.I_H,
                        "ADDITIONAL_J_END": i.J_H,
                        "USE_ADDITIONAL_J_END": i.J_H
                    })
                if i.ELEMENT not in json["Assign"]:
                    json["Assign"][i.ELEMENT] = {"ITEMS": []}
                json["Assign"][i.ELEMENT]["ITEMS"].append(item_data)
            return json
        
        @classmethod
        def create(cls):
            MidasAPI("PUT", "/db/bmld", cls.json())
        
        @classmethod
        def get(cls):
            return MidasAPI("GET", "/db/bmld")
        
        @classmethod
        def delete(cls):
            cls.data=[]
            return MidasAPI("DELETE", "/db/bmld")
        
        @classmethod
        def sync(cls):
            cls.data = []
            a = cls.get()
            if a != {'message': ''}:
                for i in a['BMLD'].keys():
                    for j in range(len(a['BMLD'][i]['ITEMS'])):
                        if a['BMLD'][i]['ITEMS'][j]['USE_ECCEN'] == True and a['BMLD'][i]['ITEMS'][j]['USE_ADDITIONAL'] == True:
                            Load.Beam(i,a['BMLD'][i]['ITEMS'][j]['LCNAME'], a['BMLD'][i]['ITEMS'][j]['P'][0], a['BMLD'][i]['ITEMS'][j]['GROUP_NAME'],
                                a['BMLD'][i]['ITEMS'][j]['DIRECTION'], a['BMLD'][i]['ITEMS'][j]['ID'], a['BMLD'][i]['ITEMS'][j]['D'], a['BMLD'][i]['ITEMS'][j]['P'],
                                a['BMLD'][i]['ITEMS'][j]['CMD'], a['BMLD'][i]['ITEMS'][j]['TYPE'], a['BMLD'][i]['ITEMS'][j]['USE_ECCEN'], a['BMLD'][i]['ITEMS'][j]['USE_PROJECTION'],
                                a['BMLD'][i]['ITEMS'][j]['ECCEN_DIR'], a['BMLD'][i]['ITEMS'][j]['ECCEN_TYPE'], a['BMLD'][i]['ITEMS'][j]['I_END'], a['BMLD'][i]['ITEMS'][j]['J_END'],
                                a['BMLD'][i]['ITEMS'][j]['USE_ADDITIONAL'], a['BMLD'][i]['ITEMS'][j]['ADDITIONAL_I_END'], a['BMLD'][i]['ITEMS'][j]['ADDITIONAL_J_END'])
                        elif a['BMLD'][i]['ITEMS'][j]['USE_ECCEN'] == False and a['BMLD'][i]['ITEMS'][j]['USE_ADDITIONAL'] == True:
                            Load.Beam(i,a['BMLD'][i]['ITEMS'][j]['LCNAME'], a['BMLD'][i]['ITEMS'][j]['P'][0], a['BMLD'][i]['ITEMS'][j]['GROUP_NAME'],
                                a['BMLD'][i]['ITEMS'][j]['DIRECTION'], a['BMLD'][i]['ITEMS'][j]['ID'], a['BMLD'][i]['ITEMS'][j]['D'], a['BMLD'][i]['ITEMS'][j]['P'],
                                a['BMLD'][i]['ITEMS'][j]['CMD'], a['BMLD'][i]['ITEMS'][j]['TYPE'], a['BMLD'][i]['ITEMS'][j]['USE_ECCEN'], a['BMLD'][i]['ITEMS'][j]['USE_PROJECTION'],
                                adnl_h = a['BMLD'][i]['ITEMS'][j]['USE_ADDITIONAL'], adnl_h_i = a['BMLD'][i]['ITEMS'][j]['ADDITIONAL_I_END'], adnl_h_j = a['BMLD'][i]['ITEMS'][j]['ADDITIONAL_J_END'])
                        elif a['BMLD'][i]['ITEMS'][j]['USE_ECCEN'] == True and a['BMLD'][i]['ITEMS'][j]['USE_ADDITIONAL'] == False:
                            Load.Beam(i,a['BMLD'][i]['ITEMS'][j]['LCNAME'], a['BMLD'][i]['ITEMS'][j]['P'][0], a['BMLD'][i]['ITEMS'][j]['GROUP_NAME'],
                                a['BMLD'][i]['ITEMS'][j]['DIRECTION'], a['BMLD'][i]['ITEMS'][j]['ID'], a['BMLD'][i]['ITEMS'][j]['D'], a['BMLD'][i]['ITEMS'][j]['P'],
                                a['BMLD'][i]['ITEMS'][j]['CMD'], a['BMLD'][i]['ITEMS'][j]['TYPE'], a['BMLD'][i]['ITEMS'][j]['USE_ECCEN'], a['BMLD'][i]['ITEMS'][j]['USE_PROJECTION'],
                                a['BMLD'][i]['ITEMS'][j]['ECCEN_DIR'], a['BMLD'][i]['ITEMS'][j]['ECCEN_TYPE'], a['BMLD'][i]['ITEMS'][j]['I_END'], a['BMLD'][i]['ITEMS'][j]['J_END'])
                        else:
                            Load.Beam(i,a['BMLD'][i]['ITEMS'][j]['LCNAME'], a['BMLD'][i]['ITEMS'][j]['P'][0], a['BMLD'][i]['ITEMS'][j]['GROUP_NAME'],
                                a['BMLD'][i]['ITEMS'][j]['DIRECTION'], a['BMLD'][i]['ITEMS'][j]['ID'], a['BMLD'][i]['ITEMS'][j]['D'], a['BMLD'][i]['ITEMS'][j]['P'],
                                a['BMLD'][i]['ITEMS'][j]['CMD'], a['BMLD'][i]['ITEMS'][j]['TYPE'], a['BMLD'][i]['ITEMS'][j]['USE_ECCEN'], a['BMLD'][i]['ITEMS'][j]['USE_PROJECTION'])
    #---------------------------------------------------------------------------------------------------------------
