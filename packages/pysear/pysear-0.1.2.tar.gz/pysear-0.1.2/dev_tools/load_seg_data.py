from openpyxl import load_workbook
import json

column_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

FLD_IND = 0
SAF_IND = 1
FLG_IND = 2
KEY_REF = 3
ADD_REQ = 4
ALT_REQ = 5
EXT_REQ = 6
DEL_REQ = -1
LST_REQ = -1


def sheet2list(sheet):
    table = []
    for col_ind in column_list:
        col = sheet[col_ind]
        col_list = [col[x].value for x in range(len(col))]
        table.append(col_list)
    tmp = []
    for ind in range(len(table[0])):
        row = []
        for j in range(len(table)):
            row.append(table[j][ind])
        tmp.append(row)
    table = tmp
    return table

def evalBool(string):
    if 'boolean' in string:
        return True
    else:
        return False

def evalNoneStr(string):
    if string is None:
        return ''
    else:
        return string

def evalYN(string):
    if string == "Yes":
        return True
    elif string == "No":
        return False
    else:
        return None

def buildTableDict(table):
    tableDict = {}
    for row in table:
        print(row[FLD_IND])
        if (not row[FLD_IND] is None) and (row[FLD_IND].find('Table') == FLD_IND):
            curr_name = row[FLD_IND].split('. ')[1].split(' ')[FLD_IND].lower().replace('®','')
            tableDict[curr_name] = {}
            print("Now working on table for %s segment!" % curr_name)
            continue
        elif (not row[FLD_IND] is None) and not (row[FLD_IND].find("Field name") == -1):
            SAF_IND = -1
            ADD_REQ = -1
            ALT_REQ = -1
            EXT_REQ = -1
            DEL_REQ = -1
            LST_REQ = -1
            for header in row:
                if not header is None:
                    if "add requests" in header:
                        ADD_REQ = row.index(header)
                    if "alter requests" in header:
                        ALT_REQ = row.index(header)
                    if "extract requests" in header:
                        EXT_REQ = row.index(header)
                    if "list requests" in header:
                        LST_REQ = row.index(header)
                    if "delete requests" in header:
                        DEL_REQ = row.index(header)
                    if "SAF field" in header:
                        SAF_IND = row.index(header)

        elif (not row[FLD_IND] is None and (row[FLD_IND].find("Field name") == -1) and (not row[2] is None)):
            if ('(') in row[FLD_IND]:
                field_name = row[FLD_IND].split('(')[FLD_IND].replace(' ','').lower()
                is_boolean = evalBool(row[FLD_IND])
            else:
                field_name = row[FLD_IND].replace(' ','').lower()
                is_boolean = False
            print(field_name)
            tableDict[curr_name][field_name] = {}
            if SAF_IND >= 0:
                tableDict[curr_name][field_name]['saf name'] = evalNoneStr(row[SAF_IND])
            tableDict[curr_name][field_name][row[FLG_IND]] = {}
            tableDict[curr_name][field_name][row[FLG_IND]]['keyword'] = row[KEY_REF]
            tableDict[curr_name][field_name][row[FLG_IND]]['add'] = evalYN(row[ADD_REQ])
            tableDict[curr_name][field_name][row[FLG_IND]]['alt'] = evalYN(row[ALT_REQ])
            tableDict[curr_name][field_name][row[FLG_IND]]['extract'] = evalYN(row[EXT_REQ])
            if (DEL_REQ >= 0) :
                tableDict[curr_name][field_name][row[FLG_IND]]['del'] = evalYN(row[DEL_REQ])
            if (LST_REQ >= 0) :
                tableDict[curr_name][field_name][row[FLG_IND]]['lst'] = evalYN(row[LST_REQ])
            tableDict[curr_name][field_name][row[FLG_IND]]['bool'] = is_boolean
            
            #print(field_name,tableDict[curr_name][field_name])

        elif(row[FLD_IND] is None and (not row[FLG_IND] is None)):
            tableDict[curr_name][field_name][row[FLG_IND]] = {}
            tableDict[curr_name][field_name][row[FLG_IND]]['keyword'] = row[KEY_REF]
            tableDict[curr_name][field_name][row[FLG_IND]]['add'] = evalYN(row[ADD_REQ])
            tableDict[curr_name][field_name][row[FLG_IND]]['alt'] = evalYN(row[ALT_REQ])
            tableDict[curr_name][field_name][row[FLG_IND]]['extract'] = evalYN(row[EXT_REQ])
            if (DEL_REQ >= 0) :
                tableDict[curr_name][field_name][row[FLG_IND]]['del'] = evalYN(row[DEL_REQ])
            if (LST_REQ >= 0) :
                tableDict[curr_name][field_name][row[FLG_IND]]['lst'] = evalYN(row[LST_REQ])

    return tableDict


class func_group:
    name = ''
    table = []
    myDict = {}

    def __init__(self,name):
        self.name = name
        tmp = load_workbook(name+'.xlsx')
        self.table = sheet2list(tmp['Sheet1'])
        self.myDict = buildTableDict(self.table)
    
    def write2JSON(self):
        with open(self.name+'.json', 'w') as fp:
            json.dump(self.myDict,fp)


u_admin = func_group('u_admin')
u_admin.write2JSON()
#print(u_admin_table)

p_admin = func_group('p_admin')
p_admin.write2JSON()

d_admin = func_group('d_admin')
d_admin.write2JSON()

perm_admin = func_group('perm_admin')
perm_admin.write2JSON()

setr_admin = func_group('s_admin')
setr_admin.write2JSON()

group_admin = func_group('g_admin')
group_admin.write2JSON()

groupconn_admin = func_group('gc_admin')
groupconn_admin.write2JSON()
