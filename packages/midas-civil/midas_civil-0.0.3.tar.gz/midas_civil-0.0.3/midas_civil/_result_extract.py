import polars as pl
import json
import xlsxwriter
from ._mapi import *
# js_file = open('JSON_Excel Parsing\\test.json','r')

# print(js_file)
# js_json = json.load(js_file)


#---- INPUT: JSON -> OUTPUT : Data FRAME --------- ---------
def JSToDF(js_json):
    for i in js_json:
        table_name= i
    
    res_json = {}

    c=0
    for heading in js_json[table_name]["HEAD"]:
        for dat in js_json[table_name]["DATA"]:
            try:
                res_json[heading].append(dat[c])
            except:
                res_json[heading]=[]
                res_json[heading].append(dat[c])

        c+=1

    res_df = pl.DataFrame(res_json)
    return(res_df)

    


# js_dat = {
#     "Argument": {
#         "TABLE_NAME": "SS_Table",
#         "TABLE_TYPE": "REACTIONG",
#         "UNIT": {
#             "FORCE": "kN",
#             "DIST": "m"
#         },
#         "STYLES": {
#             "FORMAT": "Fixed",
#             "PLACE": 12
#         }
#     }
# }

# MAPI_KEY('eyJ1ciI6InN1bWl0QG1pZGFzaXQuY29tIiwicGciOiJjaXZpbCIsImNuIjoib3R3aXF0NHNRdyJ9.da8f9dd41fee01425d8859e0091d3a46b0f252ff38341c46c73b26252a81571d')
# ss_json = MidasAPI("POST","/post/table",js_dat)
# df4 = JSToDF(ss_json)








# print(df4)
# df4.write_excel("new.xlsx",
#                 "Plate Forces",
#                 header_format={"bold":True},
#                 autofit=True,
#                 autofilter=True,
#                 table_style="Table Style Light 8"
#                 )


# with xlsxwriter.Workbook("test2.xlsx") as Wb:
#     ws = Wb.add_worksheet()

#     df4.write_excel(Wb,"Sheet 1",table_style="Table Style Light 8",autofit=True)

#     df4.write_excel(Wb,"Sheet 1",table_style="Table Style Light 8",autofit=True,autofilter=False,position="A31",include_header=False)


def ResultData(tabletype:str,elements:list=[],loadcase:list=[]):
    js_dat = {
        "Argument": {
            "TABLE_NAME": "SS_Table",
            "TABLE_TYPE": tabletype,
            "UNIT": {
                "FORCE": "kN",
                "DIST": "m"
            },
            "STYLES": {
                "FORMAT": "Fixed",
                "PLACE": 12
            }
        }
    }

    node_elem_js = {
            "KEYS": elements
        }

    if elements!=[]: js_dat["Argument"]['NODE_ELEMS'] = node_elem_js
    if loadcase!=[]: js_dat["Argument"]['LOAD_CASE_NAMES'] = loadcase

    ss_json = MidasAPI("POST","/post/table",js_dat)
    return JSToDF(ss_json)